from flask import Flask, request, jsonify
import os
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Function to handle general file uploads (e.g., for Aadhaar, PAN, etc.)
@app.route('/upload', methods=['POST'])
def upload_files():
    if 'aadhaar_image' not in request.files or 'pan_image' not in request.files or 'selfie' not in request.files or 'video' not in request.files:
        return jsonify({"error": "All files are required!"}), 400

    aadhaar_image = request.files['aadhaar_image']
    pan_image = request.files['pan_image']
    selfie = request.files['selfie']
    video = request.files['video']

    for file in [aadhaar_image, pan_image, selfie, video]:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    return jsonify({"status": "Files uploaded successfully!"}), 200

# Function to handle only video uploads
@app.route('/upload_video', methods=['POST'])
def upload_video():
    # Check for the video file in the request
    if 'file' not in request.files:
        return jsonify({"error": "No video file provided"}), 400

    video = request.files['file']
    filename = secure_filename(video.filename)
    video.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    return jsonify({"status": "Video uploaded successfully!"}), 200

@app.route('/test', methods=['GET'])
def test_connection():
    return jsonify({"message": "Connection successful!"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
