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
        
        Args:
            rows: List of rows, where each row is a list of word dictionaries
            
        Returns:
            Dict containing table headers and data frame
        """
        headers = ['Position', 'Team', 'MP', 'O', 'U', 'G', 'G/M']  # Removed 'Last 5'
        df = []
        
        # Skip navigation elements at the top
        start_idx = 0
        for i, row in enumerate(rows):
            row_text = ' '.join(word['text'] for word in row)
            if 'TEAM' in row_text and 'MP' in row_text:  # Found the header row
                start_idx = i + 1
                break
        
        # Process data rows
        for row in rows[start_idx:]:
            # Sort words by x_center to maintain left-to-right order
            sorted_words = sorted(row, key=lambda x: x['x_center'])
            
            # Skip rows that don't match our expected pattern
            if not sorted_words or len(sorted_words) < 4:
                continue
                
            row_data = [''] * len(headers)
            
            # Extract position (remove the dot if present)
            first_word = sorted_words[0]['text'].replace('.', '')
            if first_word.isdigit():
                row_data[0] = int(first_word)
                
                # Extract team name (usually the second word/group)
                team_words = []
                current_x = 0
                for word in sorted_words[1:]:
                    if word['x_center'] < 200:  # Team names are typically on the left
                        team_words.append(word['text'])
                    else:
                        break
                # Clean up team name by removing leading ". " if present
                team_name = ' '.join(team_words).strip()
                if team_name.startswith('. '):
                    team_name = team_name[2:]
                row_data[1] = team_name
                
                # Process remaining columns
                for word in sorted_words:
                    x = word['x_center']
                    text = word['text'].strip()
                    
                    # MP column (usually around x=350)
                    if 330 < x < 370 and text.isdigit():
                        row_data[2] = int(text)
                    
                    # O column (around x=380-400)
                    elif 370 < x < 400 and text.isdigit():
                        row_data[3] = int(text)
                    
                    # U column (around x=410-430)
                    elif 400 < x < 430 and text.isdigit():
                        row_data[4] = int(text)
                    
                    # G column (Goals, format like "84:29")
                    elif 430 < x < 480 and ':' in text:
                        row_data[5] = text
                    
                    # G/M column (usually a float value)
                    elif 480 < x < 520:
                        try:
                            row_data[6] = float(text)
                        except ValueError:
                            pass
                
                # Only add rows that have at least position and team
                if row_data[0] and row_data[1]:
                    df.append(row_data)
        
        return {
            'headers': headers,
            'df': sorted(df, key=lambda x: x[0]) if df else []  # Sort by position
        }

    def set_y_threshold(self, threshold: float):
        """Set the Y-coordinate threshold for grouping words into rows."""
        self.y_threshold = threshold
        logger.info(f"Y-threshold set to: {threshold}") 