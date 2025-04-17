# Betting Site OCR and Automation

A comprehensive application that combines web automation and OCR capabilities to process betting site information. The application uses Selenium for web automation and Google Cloud Vision API for text extraction from screenshots.

## Features

- Automated web interaction with betting sites using Selenium
- OCR processing using Google Cloud Vision API
- Modern web interface with drag-and-drop file upload
- Screenshot capture and management
- Text extraction and processing
- Automatic JSON result storage
- Responsive design with TailwindCSS

## Prerequisites

- Python 3.8+
- Google Chrome Browser
- Google Cloud Vision API credentials
- Virtual Environment

## Project Structure

```
betting-app/
├── src/
│   ├── selenium/           # Selenium automation components
│   │   ├── screenshot_manager.py
│   │   └── __init__.py
│   ├── ocr/               # OCR processing components
│   │   ├── vision_client.py
│   │   ├── image_utils.py
│   │   ├── ocr_client.py
│   │   └── __init__.py
│   └── config/            # Configuration files
│       └── ocr_config.py
├── app.py                 # Main Flask application
├── templates/            
│   └── index.html        # Frontend template
├── credentials/          # API credentials (not in version control)
│   └── .gitkeep
├── uploads/             # Uploaded files and results
│   └── .gitkeep
├── requirements.txt     # Python dependencies
└── README.md
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/betting-app.git
cd betting-app
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
.\venv\Scripts\activate  # On Windows
source venv/bin/activate # On Unix/MacOS
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up Google Cloud Vision:
   - Create a project in Google Cloud Console
   - Enable the Cloud Vision API
   - Create a service account and download the JSON key
   - Place the key in the `credentials` directory as `google_cloud_credentials.json`

## Configuration

1. OCR Settings:
   - Configure OCR parameters in `src/config/ocr_config.py`
   - Adjust language settings, image size limits, and output directories

2. Selenium Settings:
   - Configure web automation parameters in the Selenium components
   - Adjust browser settings and automation behavior as needed

## Usage

1. Start the Flask application:
```bash
python app.py
```

2. Access the web interface:
   - Open your browser to `http://localhost:5000`
   - Upload screenshots or use the automation features
   - View and copy extracted text

3. Using the OCR Client programmatically:
```python
from src.ocr.ocr_client import OCRClient

# Initialize the OCR client
ocr_client = OCRClient()

# Process an image
result = ocr_client.process_image("path/to/image.jpg")
print(result)
```

4. Using the Screenshot Manager:
```python
from src.selenium.screenshot_manager import ScreenshotManager

# Initialize the screenshot manager
screenshot_manager = ScreenshotManager()

# Capture screenshots from betting site
screenshot_manager.capture_odds("https://www.bet365.mx/#/AS/B1/")
```

## Output

OCR results are saved as JSON files containing:
- Detected text
- Confidence level
- Language
- Image path
- Processing timestamp

## Troubleshooting

1. OCR Issues:
   - Verify Google Cloud credentials are correctly set up
   - Check supported image formats (jpg, jpeg, png, bmp, gif)
   - Ensure image size is within limits (10MB)
   - Review logs for error messages

2. Selenium Issues:
   - Verify Chrome browser is installed
   - Check ChromeDriver compatibility
   - Review automation logs for errors
   - Ensure proper anti-detection measures are configured

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Google Cloud Vision API
- Selenium WebDriver
- Flask
- TailwindCSS 