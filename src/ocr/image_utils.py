import os
from pathlib import Path
from PIL import Image
import io
from config.ocr_config import MAX_IMAGE_SIZE, SUPPORTED_IMAGE_FORMATS

class ImageProcessor:
    @staticmethod
    def validate_image_path(image_path: str) -> bool:
        """Validate if the image path exists and has a supported format."""
        path = Path(image_path)
        return path.exists() and path.suffix.lower() in SUPPORTED_IMAGE_FORMATS

    @staticmethod
    def read_image(image_path: str) -> bytes:
        """Read and validate image file."""
        if not ImageProcessor.validate_image_path(image_path):
            raise ValueError(f"Invalid image path or format: {image_path}")

        with open(image_path, 'rb') as image_file:
            image_data = image_file.read()
            
            if len(image_data) > MAX_IMAGE_SIZE:
                raise ValueError(f"Image size exceeds maximum allowed size of {MAX_IMAGE_SIZE} bytes")
                
            return image_data

    @staticmethod
    def preprocess_image(image_data: bytes) -> bytes:
        """Basic image preprocessing."""
        try:
            # Open image from bytes
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Save processed image to bytes
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=95)
            return output.getvalue()
            
        except Exception as e:
            raise ValueError(f"Error processing image: {str(e)}")

    @staticmethod
    def save_image(image_data: bytes, output_path: str) -> None:
        """Save image data to file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'wb') as f:
            f.write(image_data) 