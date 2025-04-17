import os
from google.cloud import vision
from google.cloud.vision_v1 import types
from typing import List, Dict, Any
from src.config.ocr_config import GOOGLE_CLOUD_CREDENTIALS, OCR_SETTINGS

class VisionClient:
    def __init__(self):
        """Initialize the Vision API client."""
        if not os.path.exists(GOOGLE_CLOUD_CREDENTIALS):
            raise FileNotFoundError(f"Google Cloud credentials file not found at {GOOGLE_CLOUD_CREDENTIALS}")
        
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_CLOUD_CREDENTIALS
        self.client = vision.ImageAnnotatorClient()

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