import os
import pandas as pd
import numpy as np
import logging
from google.cloud import vision
from google.cloud.vision_v1 import types
from typing import List, Dict, Any, Tuple
from src.config.ocr_config import GOOGLE_CLOUD_CREDENTIALS, OCR_SETTINGS

# Set up logging
logger = logging.getLogger(__name__)

class VisionClient:
    def __init__(self):
        """Initialize the Vision API client."""
        if not os.path.exists(GOOGLE_CLOUD_CREDENTIALS):
            raise FileNotFoundError(f"Google Cloud credentials file not found at {GOOGLE_CLOUD_CREDENTIALS}")
        
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_CLOUD_CREDENTIALS
        self.client = vision.ImageAnnotatorClient()
        # Increased threshold for better row detection in betting tables
        self.y_threshold = 20  # Increased from 10 to 20
        logger.info("VisionClient initialized successfully")

    def detect_text(self, image_path: str) -> Dict[str, Any]:
        """
        Detect text in an image using Google Cloud Vision API.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            Dict[str, Any]: Dictionary containing detected text and confidence scores
        """
        # Verify file exists and is within size limit
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
            
        file_size = os.path.getsize(image_path)
        if file_size > OCR_SETTINGS["max_image_size"]:
            raise ValueError(f"Image size ({file_size} bytes) exceeds maximum allowed size ({OCR_SETTINGS['max_image_size']} bytes)")
            
        try:
            # Read the image file
            with open(image_path, 'rb') as image_file:
                content = image_file.read()

            # Create image object
            image = types.Image(content=content)

            # Perform text detection
            response = self.client.text_detection(
                image=image,
                image_context={"language_hints": [OCR_SETTINGS["language"]]}
            )

            if response.error.message:
                raise Exception(
                    f"Error detecting text: {response.error.message}"
                )

            # Extract text annotations
            result = {
                "full_text": response.text_annotations[0].description if response.text_annotations else "",
                "text_blocks": []
            }
            
            # Process individual text blocks
            for text in response.text_annotations[1:]:  # Skip the first one as it contains all text
                vertices = [(vertex.x, vertex.y) for vertex in text.bounding_poly.vertices]
                result["text_blocks"].append({
                    "text": text.description,
                    "confidence": text.confidence if hasattr(text, "confidence") else None,
                    "bounds": vertices,
                    "locale": text.locale if hasattr(text, "locale") else None
                })

            return result

        except Exception as e:
            raise Exception(f"Error processing image: {str(e)}")

    def detect_handwriting(self, image_path: str) -> Dict[str, Any]:
        """
        Detect handwriting in an image using Google Cloud Vision API.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            Dict[str, Any]: Dictionary containing detected handwriting and confidence scores
        """
        try:
            # Read the image file
            with open(image_path, 'rb') as image_file:
                content = image_file.read()

            # Create image object
            image = types.Image(content=content)

            # Perform document text detection (better for handwriting)
            response = self.client.document_text_detection(image=image)
            document = response.full_text_annotation

            if response.error.message:
                raise Exception(
                    '{}\nFor more info on error messages, check: '
                    'https://cloud.google.com/apis/design/errors'.format(
                        response.error.message))

            # Process the results
            if document:
                return {
                    'full_text': document.text,
                    'confidence': document.pages[0].confidence if document.pages else 0.0,
                    'language': document.pages[0].property.detected_languages[0].language_code if document.pages and document.pages[0].property.detected_languages else 'en'
                }
            else:
                return {
                    'full_text': '',
                    'confidence': 0.0,
                    'language': 'en'
                }

        except Exception as e:
            raise Exception(f"Error processing handwriting: {str(e)}")

    def detect_table(self, image_path: str) -> Dict[str, Any]:
        """
        Detect and structure tabular data from an image using Google Cloud Vision API.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            Dict[str, Any]: Dictionary containing structured table data and metadata
        """
        try:
            # Verify file exists and check size
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")
                
            file_size = os.path.getsize(image_path)
            if file_size > OCR_SETTINGS["max_image_size"]:
                raise ValueError(f"Image size ({file_size} bytes) exceeds maximum allowed size ({OCR_SETTINGS['max_image_size']} bytes)")
                
            # Read and process the image
            with open(image_path, 'rb') as image_file:
                content = image_file.read()
            
            image = vision.Image(content=content)
            logger.info("Image loaded successfully")
            
            # Use document_text_detection for better structure recognition
            response = self.client.document_text_detection(
                image=image,
                image_context={"language_hints": [OCR_SETTINGS["language"]]}
            )
            logger.info("Document text detection completed")

            if response.error.message:
                raise Exception(f"Error detecting text: {response.error.message}")

            # Process the response into structured data
            words = self.parse_document_text_response(response)
            logger.info(f"Extracted {len(words)} words from response")
            
            rows = self.group_words_into_rows(words, self.y_threshold)
            logger.info(f"Grouped words into {len(rows)} rows")
            
            table_data = self.convert_rows_to_table(rows)
            logger.info(f"Converted rows to table with {len(table_data['headers'])} columns")
            
            result = {
                'table': table_data,
                'raw_text': response.full_text_annotation.text if response.full_text_annotation else "",
                'confidence': response.full_text_annotation.pages[0].confidence if response.full_text_annotation.pages else 0.0
            }
            
            return result

        except Exception as e:
            logger.error(f"Error in detect_table: {str(e)}", exc_info=True)
            raise

    def parse_document_text_response(self, response) -> List[Dict[str, Any]]:
        """
        Extract words and their bounding boxes from the document text response.
        
        Args:
            response: Google Cloud Vision API response
            
        Returns:
            List[Dict[str, Any]]: List of words with their coordinates and metadata
        """
        try:
            words = []
            
            # Process each page (usually just one for screenshots)
            for page in response.full_text_annotation.pages:
                for block in page.blocks:
                    for paragraph in block.paragraphs:
                        for word in paragraph.words:
                            # Get word text
                            text = ''.join([symbol.text for symbol in word.symbols])
                            
                            # Get bounding box coordinates
                            vertices = [(vertex.x, vertex.y) for vertex in word.bounding_box.vertices]
                            
                            # Calculate center points for sorting
                            x_center = sum(x for x, _ in vertices) / 4
                            y_center = sum(y for _, y in vertices) / 4
                            
                            words.append({
                                'text': text,
                                'bounds': vertices,
                                'x_center': x_center,
                                'y_center': y_center,
                                'confidence': word.confidence
                            })
            
            logger.debug(f"Parsed words: {words}")
            return words
            
        except Exception as e:
            logger.error(f"Error in parse_document_text_response: {str(e)}", exc_info=True)
            raise

    def group_words_into_rows(self, words: List[Dict[str, Any]], y_threshold: float) -> List[List[Dict[str, Any]]]:
        """
        Group words into rows based on their Y-coordinates.
        
        Args:
            words: List of word dictionaries with coordinates
            y_threshold: Maximum Y-coordinate difference to consider words in the same row
            
        Returns:
            List[List[Dict[str, Any]]]: Words grouped into rows
        """
        try:
            if not words:
                return []
            
            # Sort words by y_center
            sorted_words = sorted(words, key=lambda w: w['y_center'])
            
            rows = []
            current_row = [sorted_words[0]]
            current_y = sorted_words[0]['y_center']
            
            # Group words into rows
            for word in sorted_words[1:]:
                if abs(word['y_center'] - current_y) <= y_threshold:
                    current_row.append(word)
                else:
                    # Sort words in current row by x_center
                    current_row.sort(key=lambda w: w['x_center'])
                    rows.append(current_row)
                    current_row = [word]
                    current_y = word['y_center']
            
            # Add the last row
            if current_row:
                current_row.sort(key=lambda w: w['x_center'])
                rows.append(current_row)
            
            logger.debug(f"Grouped rows: {rows}")
            return rows
            
        except Exception as e:
            logger.error(f"Error in group_words_into_rows: {str(e)}", exc_info=True)
            raise

    def convert_rows_to_table(self, rows):
        """
        Convert rows of words into a structured table format.
        """
        try:
            if not rows:
                return {'headers': [], 'df': []}
            
            # Define expected columns
            headers = ['Date', 'Team1', 'Score', 'Result', 'Team2', 'Spread', 'OU_Type', 'Total']
            data = []
            
            # Skip header row by checking for header-like content
            header_keywords = {'GAME', 'RESULT', 'ATS', 'O/U'}
            
            for row in rows:
                # Skip rows that contain header keywords
                row_texts = {word['text'].upper() for word in row}
                if any(keyword in row_texts for keyword in header_keywords):
                    continue
                
                row_data = {header: '' for header in headers}
                spread_found = False
                ou_found = False
                total_found = False
                
                # Sort words by x position for consistent processing
                sorted_words = sorted(row, key=lambda x: x['x_center'])
                
                # First pass: Look for specific patterns
                for i, word in enumerate(sorted_words):
                    text = word['text'].strip()
                    text_clean = text.strip('()@ ')
                    text_upper = text_clean.upper()
                    x_coord = word['x_center']
                    
                    # Date (contains '/')
                    if '/' in text:
                        row_data['Date'] = text
                        continue
                    
                    # Teams
                    if text_clean in ['MIN', 'DET']:
                        if not row_data['Team1']:
                            row_data['Team1'] = text_clean
                        elif not row_data['Team2']:
                            row_data['Team2'] = text_clean
                        continue
                    
                    # Score (contains '-')
                    if '-' in text and text.replace('-', '').isdigit():
                        row_data['Score'] = text
                        continue
                    
                    # Spread (contains .5 and +/-)
                    if not spread_found and '.5' in text and ('+' in text or '-' in text):
                        row_data['Spread'] = text_clean
                        spread_found = True
                        
                        # Check if this spread contains team info
                        if 'DET' in text or 'MIN' in text:
                            team = 'DET' if 'DET' in text else 'MIN'
                            if not row_data['Team2']:
                                row_data['Team2'] = team
                        continue
                    
                    # O/U Type and Total
                    if not ou_found:
                        # Check for O/U indicators in various formats
                        if text_upper in ['O', 'U', '0', 'O)', 'U)', '(O', '(U', '(O)', '(U)']:
                            # Clean up the O/U indicator
                            clean_ou = text_upper.strip('() ')
                            row_data['OU_Type'] = 'O' if clean_ou in ['O', '0', 'O)', '(O', '(O)'] else 'U'
                            ou_found = True
                            
                            # Look ahead for the total value
                            if i + 1 < len(sorted_words):
                                next_text = sorted_words[i + 1]['text'].strip('() ')
                                if '.5' in next_text:
                                    row_data['Total'] = next_text
                                    total_found = True
                                elif next_text.isdigit():  # Handle whole numbers
                                    row_data['Total'] = next_text
                                    total_found = True
                            continue
                    
                    # Catch any remaining total values
                    if not total_found:
                        # Check for standalone numbers or decimals
                        if text_clean.isdigit() or '.5' in text_clean:
                            if not ('+' in text or '-' in text):  # Make sure it's not a spread
                                row_data['Total'] = text_clean
                                total_found = True
                                continue
                
                # Clean up data
                row_data = {k: v.strip('() ') for k, v in row_data.items()}
                
                # Second pass: Try to find missing Team2 if we have other data
                if not row_data['Team2'] and row_data['Team1'] and row_data['Score']:
                    # Look for team in spread text
                    for word in sorted_words:
                        text = word['text']
                        if 'DET' in text or 'MIN' in text:
                            team = 'DET' if 'DET' in text else 'MIN'
                            if team != row_data['Team1']:
                                row_data['Team2'] = team
                                break
                
                # Simple Result detection: Look for 'W', otherwise set as 'L'
                found_w = False
                for word in sorted_words:
                    text = word['text'].upper().strip('() ')
                    if 'W' in text:
                        found_w = True
                        break
                row_data['Result'] = 'W' if found_w else 'L'
                
                # Only add rows that have some meaningful data (at least date and team1)
                if row_data['Date'] and row_data['Team1']:
                    data.append(row_data)
            
            return {'headers': headers, 'df': data}
            
        except Exception as e:
            logger.error(f"Error in convert_rows_to_table: {str(e)}", exc_info=True)
            raise

    def set_y_threshold(self, threshold: float):
        """Set the Y-coordinate threshold for grouping words into rows."""
        self.y_threshold = threshold
        logger.info(f"Y-threshold set to: {threshold}") 