import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / 'output'
SCREENSHOTS_DIR = OUTPUT_DIR / 'screenshots'
OCR_OUTPUT_DIR = OUTPUT_DIR / 'ocr_results'

# Create directories if they don't exist
for directory in [OUTPUT_DIR, SCREENSHOTS_DIR, OCR_OUTPUT_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Google Cloud Vision settings
GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

# OCR settings
DEFAULT_LANGUAGE = 'en'
CONFIDENCE_THRESHOLD = 0.7

# Image processing settings
MAX_IMAGE_SIZE = 1024 * 1024 * 4  # 4MB
SUPPORTED_IMAGE_FORMATS = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff'] 