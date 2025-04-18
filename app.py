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
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        # Create unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{secure_filename(file.filename)}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save the file
        file.save(filepath)
        logger.info(f"Saved file to: {filepath}")
        
        try:
            # Process with Vision API
            result = process_image(filepath)
            
            # Save results to JSON
            result_filename = f"{filename}_results.json"
            result_filepath = os.path.join(app.config['UPLOAD_FOLDER'], result_filename)
            with open(result_filepath, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved results to: {result_filepath}")
            
            # Return the result directly without extra nesting
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"Error in upload_file: {str(e)}", exc_info=True)
            return jsonify({'error': str(e)}), 500
        
    return jsonify({'error': 'Invalid file type'}), 400

if __name__ == '__main__':
    app.run(debug=True) 