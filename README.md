# Sports OCR Processor

A clean, modern web application for processing sports screenshots using Google Cloud Vision OCR. Upload images and extract text data with ease.

## Features

- Modern, clean UI with drag-and-drop file upload
- Supports PNG, JPG, and JPEG formats
- Google Cloud Vision OCR integration
- Copy results to clipboard
- Automatic JSON result storage
- Responsive design

## Prerequisites

- Python 3.8+
- Google Cloud Vision API credentials
- Flask

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/sports-ocr-processor.git
cd sports-ocr-processor
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up Google Cloud Vision:
   - Create a project in Google Cloud Console
   - Enable the Cloud Vision API
   - Create a service account and download the JSON key
   - Set the environment variable:
     ```bash
     export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/credentials.json"
     ```

5. Create necessary directories:
```bash
mkdir uploads
mkdir templates
```

## Usage

1. Start the Flask application:
```bash
python app.py
```

2. Open your browser and navigate to `http://localhost:5000`

3. Upload an image by either:
   - Dragging and dropping onto the upload zone
   - Clicking "Upload a file" and selecting from your computer

4. View the extracted text and copy it to your clipboard if needed

## Project Structure

```
sports-ocr-processor/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── templates/         
│   └── index.html     # Frontend template
├── uploads/           # Uploaded files and results
└── README.md
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Google Cloud Vision API
- Flask
- TailwindCSS 

# Betting App OCR Integration

This project integrates Google Cloud Vision API for OCR (Optical Character Recognition) functionality to process betting site screenshots.

## Setup

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up Google Cloud Vision API:
   - Create a Google Cloud project
   - Enable the Cloud Vision API
   - Create a service account and download the credentials JSON file
   - Place the credentials file in the `credentials` directory as `google_cloud_credentials.json`
   - Alternatively, set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to point to your credentials file

3. Configure the OCR settings in `src/config/ocr_config.py` if needed.

## Usage

The OCR functionality can be used through the `OCRClient` class:

```python
from src.ocr.ocr_client import OCRClient

# Initialize the OCR client
ocr_client = OCRClient()

# Process an image
result = ocr_client.process_image("path/to/image.jpg")
print(result)
```

## Output

OCR results are saved in the `data/ocr_results` directory as JSON files. Each result includes:
- Detected text
- Confidence level
- Language
- Image path

## Troubleshooting

If you encounter issues:
1. Verify your Google Cloud credentials are correctly set up
2. Check that the image format is supported (jpg, jpeg, png, bmp, gif)
3. Ensure the image size is within the limit (10MB)
4. Check the logs for any error messages 