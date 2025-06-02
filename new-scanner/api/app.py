#!/usr/bin/env python3
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tempfile
import json
import requests
import traceback
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Directory to store temporary files
TEMP_DIR = os.path.join(os.path.dirname(__file__), "temp_files")
os.makedirs(TEMP_DIR, exist_ok=True)

# Configure OpenAI API key
OPENAI_API_KEY = ""
try:
    key_path = os.path.join(os.path.dirname(__file__), "key.txt")
    if os.path.exists(key_path):
        with open(key_path, "r") as f:
            OPENAI_API_KEY = f.read().strip()
            print(f"OpenAI API key loaded from key.txt (length: {len(OPENAI_API_KEY)})")
            print(f"OpenAI API key starts with: {OPENAI_API_KEY[:8]}...")
    else:
        print("Warning: key.txt not found. Please provide your OpenAI API key.")
except Exception as e:
    print(f"Error loading OpenAI API key: {e}")

# Configure ImgBB API key
IMGBB_API_KEY = ""
try:
    imgbb_key_path = os.path.join(os.path.dirname(__file__), "image_api.txt")
    if os.path.exists(imgbb_key_path):
        with open(imgbb_key_path, "r") as f:
            IMGBB_API_KEY = f.read().strip()
            print(f"ImgBB API key loaded from image_api.txt (length: {len(IMGBB_API_KEY)})")
    else:
        # Use a default key if file doesn't exist
        IMGBB_API_KEY = "7e8199cdbfd21a1ed4bee61a18eb5f9b"
        print(f"Using default ImgBB API key: {IMGBB_API_KEY}")
        # Create the file with the default key
        with open(imgbb_key_path, "w") as f:
            f.write(IMGBB_API_KEY)
except Exception as e:
    print(f"Error loading ImgBB API key: {e}")

# Define allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_to_imgbb(file_path):
    """
    Upload an image to ImgBB and return the URL
    """
    try:
        with open(file_path, "rb") as f:
            response = requests.post(
                "https://api.imgbb.com/1/upload",
                params={"key": IMGBB_API_KEY, "expiration": 600},  # 600 = 10 min expiration
                files={"image": f}
            )
        
        if response.status_code == 200:
            result = response.json()
            image_url = result['data']['url']
            print(f"Image uploaded to ImgBB: {image_url}")
            return image_url
        else:
            print(f"Error uploading to ImgBB: {response.text}")
            return None
    except Exception as e:
        print(f"Exception uploading to ImgBB: {str(e)}")
        return None

@app.route('/analyze', methods=['POST'])
def analyze_document():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed"}), 400
    
    try:
        # Check API keys before proceeding
        if not OPENAI_API_KEY:
            return jsonify({"error": "OpenAI API key is not configured"}), 500
            
        if not IMGBB_API_KEY:
            return jsonify({"error": "ImgBB API key is not configured"}), 500
        
        # Generate a unique filename to avoid collisions
        file_ext = file.filename.split('.')[-1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
        file_path = os.path.join(TEMP_DIR, unique_filename)
        
        # Save the uploaded file
        file.save(file_path)
        
        print(f"File saved temporarily at: {file_path}")
        print(f"File size: {os.path.getsize(file_path)} bytes")
        
        # Upload the file to ImgBB to get a public URL
        image_url = upload_to_imgbb(file_path)
        
        if not image_url:
            return jsonify({"error": "Failed to upload image to hosting service"}), 500
        
        print(f"Using image URL: {image_url}")
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }
        
        payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "This is a medical document. Please extract as much information as possible, it is for a demonstration of a product so the info are synthetic."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 1000
        }
        
        print("Calling OpenAI API...")
        
        # Call OpenAI API
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions", 
                headers=headers, 
                json=payload,
                timeout=60  # Increase timeout to 60 seconds
            )
            
            print(f"OpenAI API response status code: {response.status_code}")
            
            if response.status_code != 200:
                error_detail = response.text
                print(f"OpenAI API error: {error_detail}")
                return jsonify({"error": f"OpenAI API error: {error_detail}"}), 500
                
            result = response.json()
            print("Successfully received response from OpenAI API")
            
        except requests.exceptions.RequestException as e:
            print(f"Request to OpenAI API failed: {str(e)}")
            return jsonify({"error": f"Request to OpenAI API failed: {str(e)}"}), 500
        finally:
            # Clean up the temporary file
            try:
                os.unlink(file_path)
                print(f"Temporary file {file_path} removed")
            except Exception as cleanup_error:
                print(f"Error removing temporary file: {cleanup_error}")
        
        # Try to extract JSON from the response
        try:
            content = result['choices'][0]['message']['content']
            print(f"Raw content from OpenAI (first 100 chars): {content[:100]}...")
            
            # Return the raw response directly
            return jsonify({"raw_response": content})
        except Exception as e:
            print(f"Error parsing OpenAI response: {str(e)}")
            print(f"Response content: {result}")
            return jsonify({"error": f"Error parsing response: {str(e)}", "raw_response": result}), 500
            
    except Exception as e:
        print(f"Server error in /analyze endpoint: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy", 
        "openai_api_key_configured": bool(OPENAI_API_KEY),
        "openai_api_key_length": len(OPENAI_API_KEY) if OPENAI_API_KEY else 0,
        "imgbb_api_key_configured": bool(IMGBB_API_KEY),
        "imgbb_api_key_length": len(IMGBB_API_KEY) if IMGBB_API_KEY else 0,
        "temp_dir": TEMP_DIR,
        "temp_file_count": len(os.listdir(TEMP_DIR))
    })

if __name__ == '__main__':
    print("Starting Flask server for Patient Document Scanner API...")
    print(f"OpenAI API key configured: {bool(OPENAI_API_KEY)}")
    print(f"ImgBB API key configured: {bool(IMGBB_API_KEY)}")
    print(f"Temporary files directory: {TEMP_DIR}")
    # Make sure to run on 0.0.0.0 to allow access from the Tauri app
    app.run(host='0.0.0.0', port=5006, debug=True)