from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import cv2
import dlib
import face_recognition
import numpy as np

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Set the upload folder path
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize dlib's face detector
face_detector = dlib.get_frontal_face_detector()

def enhance_image_visibility(image):
    # Convert image to HSV to adjust saturation and brightness
    hsv_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    hsv_image = cv2.cvtColor(hsv_image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv_image)

    # Increase brightness and saturation
    v = cv2.add(v, 30)  # Increase brightness
    s = cv2.add(s, 40)  # Increase saturation

    # Merge and convert back to grayscale
    enhanced_hsv_image = cv2.merge([h, s, v])
    enhanced_bgr_image = cv2.cvtColor(enhanced_hsv_image, cv2.COLOR_HSV2BGR)
    enhanced_gray_image = cv2.cvtColor(enhanced_bgr_image, cv2.COLOR_BGR2GRAY)

    # Apply sharpening
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    sharpened_image = cv2.filter2D(enhanced_gray_image, -1, kernel)

    # Save enhanced image for debugging
    cv2.imwrite('temp_enhanced.jpg', sharpened_image)
    return sharpened_image

def get_face_encoding(image_path):
    # Load the image file and convert to RGB
    image = cv2.imread(image_path)
    enhanced_image = enhance_image_visibility(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY))
    rgb_image = cv2.cvtColor(enhanced_image, cv2.COLOR_GRAY2RGB)

    # Detect and encode the face
    encodings = face_recognition.face_encodings(rgb_image)
    return encodings[0] if encodings else None

def extract_frame_encodings(video_path, num_frames=5):
    """Extracts multiple frame encodings from the video."""
    cap = cv2.VideoCapture(video_path)
    frame_encodings = []
    count = 0

    while count < num_frames:
        success, frame = cap.read()
        if not success:
            break
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(rgb_frame)
        if encodings:
            frame_encodings.append(encodings[0])  # Only take the first face encoding per frame
            count += 1

    cap.release()
    return frame_encodings

def match_faces(aadhar_encoding, video_encodings, tolerance=0.6):
    """Compares Aadhaar face encoding with multiple video encodings."""
    matches = [face_recognition.compare_faces([aadhar_encoding], encoding, tolerance=tolerance)[0] for encoding in video_encodings]
    match_score = sum(matches) / len(matches)  # Proportion of frames that match
    return match_score >= 0.6  # Match if 60% of frames match

@app.route('/api/upload', methods=['POST'])
def upload_files():
    if 'aadhar' not in request.files or 'pan' not in request.files or 'selfie' not in request.files or 'video' not in request.files:
        return jsonify({"error": "All files are required: Aadhaar, PAN, selfie, and video."}), 400

    aadhar = request.files['aadhar']
    pan = request.files['pan']
    selfie = request.files['selfie']
    video = request.files['video']

    # Save files
    aadhar_path = os.path.join(app.config['UPLOAD_FOLDER'], 'aadhar.png')
    aadhar.save(aadhar_path)

    pan_path = os.path.join(app.config['UPLOAD_FOLDER'], 'pan.png')
    pan.save(pan_path)

    selfie_path = os.path.join(app.config['UPLOAD_FOLDER'], 'selfie.png')
    selfie.save(selfie_path)

    video_path = os.path.join(app.config['UPLOAD_FOLDER'], 'video.webm')
    video.save(video_path)

    return jsonify({"message": "Files uploaded successfully!"}), 200

@app.route('/api/match', methods=['POST'])
def face_match():
    aadhar_path = os.path.join(app.config['UPLOAD_FOLDER'], 'aadhar.png')
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], 'video.webm')
    
    # Check if files exist
    if not os.path.exists(aadhar_path) or not os.path.exists(video_path):
        return jsonify({"error": "Aadhaar or video file not found."}), 400

    # Get Aadhaar face encoding
    aadhar_encoding = get_face_encoding(aadhar_path)
    if aadhar_encoding is None:
        return jsonify({"error": "No face detected in Aadhaar image."}), 500

    # Get video frame encodings
    video_encodings = extract_frame_encodings(video_path, num_frames=5)
    if not video_encodings:
        return jsonify({"error": "No face detected in video frames."}), 500

    # Perform face matching
    is_match = match_faces(aadhar_encoding, video_encodings)

    if is_match:
        return jsonify({"message": "Face match found!"}), 200
    else:
        return jsonify({"message": "Face does not match."}), 200

@app.route('/test', methods=['GET'])
def test_connection():
    return jsonify({"message": "Connection successful!"})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
