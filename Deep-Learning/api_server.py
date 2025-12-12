"""
Flask API Server for Vehicle License Plate Recognition
Provides REST API endpoint for testing with Postman or other HTTP clients
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import sys
import tempfile
from werkzeug.utils import secure_filename
import traceback

# Add Main-Scripts to path
script_dir = os.path.dirname(os.path.abspath(__file__))
main_scripts_dir = os.path.join(script_dir, "Main-Scripts")
sys.path.insert(0, main_scripts_dir)

# Import detection and recognition modules
import object_detection_yolo as LP_detection
import Hawk_Eye_LP_recognition as LP_reco
from cv2 import imwrite, imread

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
UPLOAD_FOLDER = os.path.join(script_dir, "uploads")
OUTPUT_FOLDER = os.path.join(script_dir, "output")
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'License Plate Recognition API is running'
    }), 200

@app.route('/recognize', methods=['POST'])
def recognize_license_plate():
    """
    Main endpoint for license plate recognition
    
    Accepts:
    - POST request with image file (form-data or raw binary)
    - Optional: 'return_image' parameter (true/false) to return processed image
    
    Returns:
    - JSON with recognition results
    - Optionally: processed image file
    """
    try:
        # Check if file is present
        if 'image' not in request.files and 'file' not in request.files:
            # Try to get raw image data
            if request.content_type and 'image' in request.content_type:
                image_data = request.data
                if len(image_data) == 0:
                    return jsonify({
                        'success': False,
                        'error': 'No image file provided. Send image as form-data with key "image" or "file", or as raw binary data.'
                    }), 400
                
                # Save raw image data to temporary file
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg', dir=UPLOAD_FOLDER)
                temp_file.write(image_data)
                temp_file.close()
                image_path = temp_file.name
            else:
                return jsonify({
                    'success': False,
                    'error': 'No image file provided. Send image as form-data with key "image" or "file", or as raw binary data.'
                }), 400
        else:
            # Get file from form data
            file = request.files.get('image') or request.files.get('file')
            
            if file.filename == '':
                return jsonify({
                    'success': False,
                    'error': 'No file selected'
                }), 400
            
            if not allowed_file(file.filename):
                return jsonify({
                    'success': False,
                    'error': f'Invalid file type. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'
                }), 400
            
            # Save uploaded file
            filename = secure_filename(file.filename)
            image_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(image_path)
        
        # Get optional parameters
        return_image = request.form.get('return_image', 'false').lower() == 'true'
        
        # Run license plate detection
        print(f"Processing image: {image_path}")
        LP_extracted, newImage, top = LP_detection.LP_detection(image_path)
        
        if LP_extracted is None or (hasattr(LP_extracted, 'size') and LP_extracted.size == 0):
            # Clean up uploaded file
            if os.path.exists(image_path):
                os.remove(image_path)
            
            return jsonify({
                'success': False,
                'error': 'Could not detect license plate in the image',
                'message': 'The image may not contain a visible license plate. Try a different image with a clearer license plate.'
            }), 400
        
        # Run license plate recognition
        try:
            final_img = LP_reco.LP_recognition(LP_extracted, newImage, top)
            
            # Save result image
            result_filename = f"result_{os.path.basename(image_path)}"
            result_path = os.path.join(OUTPUT_FOLDER, result_filename)
            imwrite(result_path, final_img)
            
            # Extract recognized text (if available)
            # The recognition result is embedded in the image, so we'll return the image path
            response_data = {
                'success': True,
                'message': 'License plate recognized successfully',
                'result_image': f'/result_image/{result_filename}',
                'uploaded_file': os.path.basename(image_path)
            }
            
            # Clean up uploaded file
            if os.path.exists(image_path):
                os.remove(image_path)
            
            # Return response
            if return_image:
                return send_file(result_path, mimetype='image/jpeg')
            else:
                return jsonify(response_data), 200
                
        except Exception as e:
            # Clean up uploaded file
            if os.path.exists(image_path):
                os.remove(image_path)
            
            return jsonify({
                'success': False,
                'error': 'Error during license plate recognition',
                'message': str(e),
                'traceback': traceback.format_exc() if app.debug else None
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': str(e),
            'traceback': traceback.format_exc() if app.debug else None
        }), 500

@app.route('/result_image/<filename>', methods=['GET'])
def get_result_image(filename):
    """Serve result images"""
    try:
        file_path = os.path.join(OUTPUT_FOLDER, filename)
        if os.path.exists(file_path):
            return send_file(file_path, mimetype='image/jpeg')
        else:
            return jsonify({
                'success': False,
                'error': 'Result image not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/info', methods=['GET'])
def api_info():
    """API information endpoint"""
    return jsonify({
        'name': 'Vehicle License Plate Recognition API',
        'version': '1.0.0',
        'endpoints': {
            'GET /health': 'Health check',
            'GET /info': 'API information',
            'POST /recognize': 'Recognize license plate from image',
            'GET /result_image/<filename>': 'Get processed result image'
        },
        'usage': {
            'POST /recognize': {
                'description': 'Upload an image to recognize license plate',
                'parameters': {
                    'image (file)': 'Image file (form-data)',
                    'return_image (optional)': 'Set to "true" to return image directly instead of JSON'
                },
                'example': 'curl -X POST -F "image=@vehicle.jpg" http://localhost:5000/recognize'
            }
        },
        'supported_formats': list(ALLOWED_EXTENSIONS)
    }), 200

if __name__ == '__main__':
    print("=" * 70)
    print("Vehicle License Plate Recognition API Server")
    print("=" * 70)
    print(f"Server starting on http://localhost:5000")
    print(f"Upload folder: {UPLOAD_FOLDER}")
    print(f"Output folder: {OUTPUT_FOLDER}")
    print("\nAvailable endpoints:")
    print("  GET  /health          - Health check")
    print("  GET  /info            - API information")
    print("  POST /recognize       - Recognize license plate")
    print("  GET  /result_image/<filename> - Get result image")
    print("\nExample usage:")
    print('  curl -X POST -F "image=@test.jpg" http://localhost:5000/recognize')
    print("=" * 70)
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)

