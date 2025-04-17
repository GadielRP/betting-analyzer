from google.cloud import vision
from google.cloud.vision_v1 import types
from typing import List, Dict, Optional
import json
from pathlib import Path
from config.ocr_config import (
    GOOGLE_CLOUD_CREDENTIALS,
    OCR_SETTINGS,
    OCR_OUTPUT_DIR
)
from .image_utils import ImageProcessor

class OCRClient:
    def __init__(self):
        """Initialize the OCR client with Google Cloud Vision credentials."""
        self.client = vision.ImageAnnotatorClient.from_service_account_json(
            GOOGLE_CLOUD_CREDENTIALS
        )
        self.image_processor = ImageProcessor()

    def process_image(self, image_path: str) -> Dict:
        """Process an image and return OCR results."""
        try:
            # Read and validate image
            image_data = self.image_processor.read_image(image_path)
            
            # Preprocess image
            processed_image = self.image_processor.preprocess_image(image_data)
            
            # Create Vision API image object
            image = types.Image(content=processed_image)
            
            # Perform text detection
            response = self.client.text_detection(image=image)
            texts = response.text_annotations
            
            if response.error.message:
                raise Exception(f"Error from Vision API: {response.error.message}")
            
            # Process results
            if texts:
                full_text = texts[0].description
                confidence = texts[0].confidence
                
                # Save results
                result = {
                    "text": full_text,
                    "confidence": confidence,
                    "language": OCR_SETTINGS["language"],
                    "image_path": image_path
                }
                
                self._save_results(result, image_path)
                return result
            else:
                return {"text": "", "confidence": 0.0, "language": OCR_SETTINGS["language"]}
                
        except Exception as e:
            raise Exception(f"Error processing image {image_path}: {str(e)}")

    def _save_results(self, result: Dict, image_path: str) -> None:
        """Save OCR results to a JSON file."""
        try:
            # Create output filename based on input image
            image_name = Path(image_path).stem
            output_path = Path(OCR_OUTPUT_DIR) / f"{image_name}_ocr.json"
            
            # Save results
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"Error saving OCR results: {str(e)}") 