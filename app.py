from flask import Flask, request, render_template, jsonify
from google.cloud import vision
import os
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import json
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def process_image_with_vision(image_path):
    """Process an image using Google Cloud Vision API"""
    client = vision.ImageAnnotatorClient()

    with open(image_path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations

    if texts:
        # Get the full text
        full_text = texts[0].description
        
        # Get individual words with their bounding boxes
        words_with_bounds = []
        for text in texts[1:]:  # Skip the first one as it contains all text
            vertices = [(vertex.x, vertex.y) for vertex in text.bounding_poly.vertices]
            words_with_bounds.append({
                'text': text.description,
                'bounds': vertices
            })
        
        return {
            'full_text': full_text,
            'words': words_with_bounds
        }
    
    return {'error': 'No text found in image'}

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
        
        try:
            # Process with Google Cloud Vision
            result = process_image_with_vision(filepath)
            
            # Save results to JSON
            result_filename = f"{filename}_results.json"
            result_filepath = os.path.join(app.config['UPLOAD_FOLDER'], result_filename)
            with open(result_filepath, 'w') as f:
                json.dump(result, f, indent=2)
            
            return jsonify({
                'success': True,
                'filename': filename,
                'result': result
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        
    return jsonify({'error': 'Invalid file type'}), 400

if __name__ == '__main__':
    app.run(debug=True) 