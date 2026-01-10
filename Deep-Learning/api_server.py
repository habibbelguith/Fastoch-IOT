"""
Flask API Server for Vehicle License Plate Recognition
Provides REST API endpoint for testing with Postman or other HTTP clients
Uses OpenAI GPT-4 Vision API for text extraction from license plates
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import tempfile
from werkzeug.utils import secure_filename
import traceback
import base64
import requests
import json
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add Main-Scripts to path
script_dir = os.path.dirname(os.path.abspath(__file__))
main_scripts_dir = os.path.join(script_dir, "Main-Scripts")
sys.path.insert(0, main_scripts_dir)

# Import detection and recognition modules
import object_detection_yolo as LP_detection
from cv2 import imwrite, imread

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
UPLOAD_FOLDER = os.path.join(script_dir, "uploads")
OUTPUT_FOLDER = os.path.join(script_dir, "output")
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4.1')
OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def encode_image_to_base64(image_path):
    """
    Encode an image file to base64 string for OpenAI API
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Base64 encoded string of the image
    """
    try:
        with open(image_path, 'rb') as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return encoded_string
    except Exception as e:
        print(f"Error encoding image to base64: {e}")
        raise

def extract_text_with_llm(image_path):
    """
    Extract text from Tunisian license plate image using OpenAI GPT-4 Vision API
    
    Args:
        image_path: Path to the license plate image
        
    Returns:
        tuple: (plate_data_dict, model_used, usage_info) or (None, None, None) on error
        plate_data_dict contains: left_number, middle_text, right_number
    """
    if not OPENAI_API_KEY:
        return None, None, {
            'error': 'OPENAI_API_KEY not configured. Please set it in your .env file.'
        }
    
    try:
        # Encode image to base64
        base64_image = encode_image_to_base64(image_path)
        
        # Determine image MIME type
        image_ext = os.path.splitext(image_path)[1].lower()
        mime_type = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp'
        }.get(image_ext, 'image/jpeg')
        
        # Prepare API request
        headers = {
            'Authorization': f'Bearer {OPENAI_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        # Prompt for Tunisian license plates
        prompt_text = """Analyze the image and extract the Tunisian license plate information.
A Tunisian license plate is composed of three distinct parts:

Right part: a numeric value

Middle part: the Arabic word "تونس"

Left part: a numeric value

Your task is to:

Detect and read each part separately.

Keep the Arabic text in its original form (do NOT transliterate). The middle_text must be in Arabic as written: "تونس".

Return the result as three variables:

left_number

middle_text (must be in Arabic: "تونس")

right_number

If any part cannot be read clearly, set its value to "UNREADABLE".

Output format (JSON only, no extra text):

{
  "left_number": "...",
  "middle_text": "...",
  "right_number": "..."
}"""
        
        payload = {
            'model': OPENAI_MODEL,
            'messages': [
                {
                    'role': 'user',
                    'content': [
                        {
                            'type': 'text',
                            'text': prompt_text
                        },
                        {
                            'type': 'image_url',
                            'image_url': {
                                'url': f'data:{mime_type};base64,{base64_image}'
                            }
                        }
                    ]
                }
            ],
            'max_tokens': 150,
            'response_format': {'type': 'json_object'}
        }
        
        # Make API request
        response = requests.post(
            f'{OPENAI_BASE_URL}/chat/completions',
            headers=headers,
            json=payload,
            timeout=30
        )
        
        # Check response
        if response.status_code == 200:
            result = response.json()
            response_content = result['choices'][0]['message']['content'].strip()
            usage_info = result.get('usage', {})
            
            # Parse JSON response
            try:
                # Try to parse JSON directly
                plate_data = json.loads(response_content)
                
                # Validate that we have the required fields
                required_fields = ['left_number', 'middle_text', 'right_number']
                if all(field in plate_data for field in required_fields):
                    return plate_data, OPENAI_MODEL, usage_info
                else:
                    # Missing fields, set defaults
                    plate_data = {
                        'left_number': plate_data.get('left_number', 'UNREADABLE'),
                        'middle_text': plate_data.get('middle_text', 'UNREADABLE'),
                        'right_number': plate_data.get('right_number', 'UNREADABLE')
                    }
                    return plate_data, OPENAI_MODEL, usage_info
                    
            except json.JSONDecodeError:
                # Try to extract JSON from text if it's embedded
                json_match = re.search(r'\{[^{}]*\}', response_content)
                if json_match:
                    try:
                        plate_data = json.loads(json_match.group())
                        # Validate fields
                        plate_data = {
                            'left_number': plate_data.get('left_number', 'UNREADABLE'),
                            'middle_text': plate_data.get('middle_text', 'UNREADABLE'),
                            'right_number': plate_data.get('right_number', 'UNREADABLE')
                        }
                        return plate_data, OPENAI_MODEL, usage_info
                    except json.JSONDecodeError:
                        pass
                
                # If JSON parsing fails, return error
                error_msg = f"Failed to parse JSON response from LLM: {response_content}"
                print(error_msg)
                return None, None, {'error': error_msg, 'raw_response': response_content}
        else:
            error_msg = f"OpenAI API error: {response.status_code}"
            try:
                error_detail = response.json()
                error_msg += f" - {error_detail.get('error', {}).get('message', 'Unknown error')}"
            except:
                error_msg += f" - {response.text}"
            
            print(f"Error calling OpenAI API: {error_msg}")
            return None, None, {'error': error_msg}
            
    except requests.exceptions.Timeout:
        error_msg = "OpenAI API request timed out"
        print(error_msg)
        return None, None, {'error': error_msg}
    except requests.exceptions.RequestException as e:
        error_msg = f"Error connecting to OpenAI API: {str(e)}"
        print(error_msg)
        return None, None, {'error': error_msg}
    except Exception as e:
        error_msg = f"Unexpected error in extract_text_with_llm: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        return None, None, {'error': error_msg}

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'License Plate Recognition API is running',
        'openai_configured': OPENAI_API_KEY is not None
    }), 200

@app.route('/recognize', methods=['POST'])
def recognize_license_plate():
    """
    Main endpoint for license plate recognition
    
    Accepts:
    - POST request with image file (form-data or raw binary)
    
    Returns:
    - JSON with recognition results:
      {
        "success": true,
        "left_number": "1234",
        "middle_text": "تونس",
        "right_number": "56",
        "model": "gpt-4.1",
        "usage": {...}
      }
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
                input_filename = 'uploaded_image.jpg'
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
            input_filename = filename
        
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
        
        # Save extracted license plate image
        # Format: {input_filename}_Licence_Plate_extracted.jpg
        input_basename = os.path.splitext(input_filename)[0]
        extracted_filename = f"{input_basename}_Licence_Plate_extracted.jpg"
        extracted_path = os.path.join(OUTPUT_FOLDER, extracted_filename)
        imwrite(extracted_path, LP_extracted)
        print(f"Saved extracted plate to: {extracted_path}")
        
        # Extract text using OpenAI
        plate_data, model_used, usage_info = extract_text_with_llm(extracted_path)
        
        if plate_data is None:
            # Clean up uploaded file
            if os.path.exists(image_path):
                os.remove(image_path)
            
            return jsonify({
                'success': False,
                'error': 'Failed to extract text from license plate',
                'details': usage_info
            }), 500
        
        # Clean up uploaded file
        if os.path.exists(image_path):
            os.remove(image_path)
        
        # Return response with structured plate data
        response_data = {
            'success': True,
            'left_number': plate_data.get('left_number', 'UNREADABLE'),
            'middle_text': plate_data.get('middle_text', 'UNREADABLE'),
            'right_number': plate_data.get('right_number', 'UNREADABLE'),
            'model': model_used,
            'usage': usage_info
        }
        
        return jsonify(response_data), 200
            
    except Exception as e:
        # Clean up uploaded file if it exists
        if 'image_path' in locals() and os.path.exists(image_path):
            os.remove(image_path)
        
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': str(e),
            'traceback': traceback.format_exc() if app.debug else None
        }), 500

@app.route('/info', methods=['GET'])
def api_info():
    """API information endpoint"""
    return jsonify({
        'name': 'Vehicle License Plate Recognition API',
        'version': '2.0.0',
        'description': 'Detects license plates in images and extracts text using OpenAI GPT-4 Vision',
        'endpoints': {
            'GET /health': 'Health check',
            'GET /info': 'API information',
            'POST /recognize': 'Recognize license plate from image and extract text'
        },
        'usage': {
            'POST /recognize': {
                'description': 'Upload an image to detect license plate and extract text',
                'parameters': {
                    'image (file)': 'Image file (form-data)'
                },
                'example': 'curl -X POST -F "image=@vehicle.jpg" http://localhost:5000/recognize',
                'response': {
                    'success': 'boolean',
                    'left_number': 'string - left numeric part of license plate',
                    'middle_text': 'string - middle text part in Arabic as written ("تونس")',
                    'right_number': 'string - right numeric part of license plate',
                    'model': 'string - OpenAI model used',
                    'usage': 'object - API usage statistics'
                }
            }
        },
        'supported_formats': list(ALLOWED_EXTENSIONS),
        'openai_model': OPENAI_MODEL,
        'openai_configured': OPENAI_API_KEY is not None
    }), 200

if __name__ == '__main__':
    print("=" * 70)
    print("Vehicle License Plate Recognition API Server")
    print("=" * 70)
    print(f"Server starting on http://localhost:5000")
    print(f"Upload folder: {UPLOAD_FOLDER}")
    print(f"Output folder: {OUTPUT_FOLDER}")
    print(f"OpenAI Model: {OPENAI_MODEL}")
    print(f"OpenAI API Key: {'Configured' if OPENAI_API_KEY else 'NOT CONFIGURED'}")
    print("\nAvailable endpoints:")
    print("  GET  /health          - Health check")
    print("  GET  /info            - API information")
    print("  POST /recognize       - Recognize license plate and extract text")
    print("\nExample usage:")
    print('  curl -X POST -F "image=@test.jpg" http://localhost:5000/recognize')
    print("=" * 70)
    
    if not OPENAI_API_KEY:
        print("\n⚠️  WARNING: OPENAI_API_KEY not configured!")
        print("   Create a .env file with: OPENAI_API_KEY=your_api_key_here")
        print("   See env.example for reference")
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
