import os
from google.cloud import vision
from google.cloud.vision_v1 import types
from typing import List, Dict, Any

class VisionClient:
    def __init__(self):
        """Initialize the Google Cloud Vision client."""
        self.client = vision.ImageAnnotatorClient()

    def detect_text(self, image_path: str) -> Dict[str, Any]:
        """
        Detect text in an image using Google Cloud Vision API.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            Dict[str, Any]: Dictionary containing detected text and confidence scores
        """
        try:
            # Read the image file
            with open(image_path, 'rb') as image_file:
                content = image_file.read()

            # Create image object
            image = types.Image(content=content)

            # Perform text detection
            response = self.client.text_detection(image=image)
            texts = response.text_annotations

            if response.error.message:
                raise Exception(
                    '{}\nFor more info on error messages, check: '
                    'https://cloud.google.com/apis/design/errors'.format(
                        response.error.message))

            # Process the results
            if texts:
                full_text = texts[0].description
                detected_texts = []
                
                # Get individual text blocks with their locations
                for text in texts[1:]:
                    detected_texts.append({
                        'text': text.description,
                        'confidence': text.confidence,
                        'bounding_box': [
                            (vertex.x, vertex.y)
                            for vertex in text.bounding_poly.vertices
                        ]
                    })

                return {
                    'full_text': full_text,
                    'text_blocks': detected_texts,
                    'language': response.text_annotations[0].locale if response.text_annotations[0].locale else 'en'
                }
            else:
                return {
                    'full_text': '',
                    'text_blocks': [],
                    'language': 'en'
                }

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