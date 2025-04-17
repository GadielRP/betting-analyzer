import os
from pathlib import Path

# Google Cloud Vision API credentials path
GOOGLE_CLOUD_CREDENTIALS = os.getenv(
    "GOOGLE_APPLICATION_CREDENTIALS",
    str(Path(__file__).parent.parent.parent / "credentials" / "google_cloud_credentials.json")
)

# OCR settings
OCR_SETTINGS = {
    "language": "es",  # Spanish language code
    "max_image_size": 10485760,  # 10MB in bytes
    "supported_formats": [".jpg", ".jpeg", ".png", ".bmp", ".gif"]
}

# Output directory for OCR results
OCR_OUTPUT_DIR = str(Path(__file__).parent.parent.parent / "data" / "ocr_results")

# Create output directory if it doesn't exist
os.makedirs(OCR_OUTPUT_DIR, exist_ok=True) 