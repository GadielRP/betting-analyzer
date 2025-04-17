from google.cloud import vision
import os
import io
from typing import List, Dict, Any
import json

class VisionProcessor:
    def __init__(self, credentials_path: str = None):
        """
        Initialize the Vision Processor
        
        Args:
            credentials_path (str): Path to Google Cloud credentials JSON file
        """
        if credentials_path:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        self.client = vision.ImageAnnotatorClient()
    
    def process_image(self, image_path: str) -> Dict[str, Any]:
        """
        Process an image using Google Cloud Vision API
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            Dict containing extracted text and confidence scores
        """
        try:
            # Read image file
            with io.open(image_path, 'rb') as image_file:
                content = image_file.read()
            
            # Create image object
            image = vision.Image(content=content)
            
            # Perform OCR
            response = self.client.text_detection(image=image)
            texts = response.text_annotations
            
            if not texts:
                return {"success": False, "error": "No text detected"}
            
            # Extract full text and individual words with their confidence
            result = {
                "success": True,
                "full_text": texts[0].description,
                "blocks": []
            }
            
            # Process each text block
            for text in texts[1:]:  # Skip first element (contains full text)
                block = {
                    "text": text.description,
                    "confidence": text.confidence,
                    "bounds": [[vertex.x, vertex.y] for vertex in text.bounding_poly.vertices]
                }
                result["blocks"].append(block)
            
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def save_results(self, results: Dict[str, Any], output_path: str):
        """
        Save OCR results to a JSON file
        
        Args:
            results (Dict): OCR results to save
            output_path (str): Path where to save the JSON file
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error saving results: {str(e)}")
            return False 