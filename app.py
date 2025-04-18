from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import os
import json
import logging
from datetime import datetime
from src.ocr.vision_client import VisionClient

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize clients
vision_client = VisionClient()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def process_image(image_path):
    """Process an image using Google Cloud Vision API"""
    try:
        logger.info(f"Processing image: {image_path}")
        # Use table detection instead of simple text detection
        result = vision_client.detect_table(image_path)
        logger.info(f"Raw API result: {result}")
        
        # Ensure we have valid table data
        if not result or 'table' not in result:
            return {'error': 'No table data detected'}
            
        # The table data is already in the correct format from vision_client
        # Just ensure it's properly structured
        if not result['table'].get('headers') or not result['table'].get('df'):
            return {'error': 'Invalid table structure detected'}
            
        return {
            'success': True,
            'table': result['table'],
            'raw_text': result.get('raw_text', '')
        }
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}", exc_info=True)
        return {'error': str(e)}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'})
        
        file = request.files['file']
        tab = request.form.get('tab', 'overunder')  # Get the current tab, default to overunder
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})
        
        if file:
            # Save the file
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            try:
                # Process the image based on the selected tab
                if tab == 'overunder':
                    result = process_image(filepath)  # Current OCR processing for over/under
                else:
                    # For now, other tabs will use the same processing
                    # We'll implement specific processing for each tab later
                    result = process_image(filepath)
                
                return jsonify({
                    'success': True,
                    'table': result['table'],
                    'raw_text': result.get('raw_text', '')
                })
                
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)})
            finally:
                # Clean up the uploaded file
                if os.path.exists(filepath):
                    os.remove(filepath)
                    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True) 