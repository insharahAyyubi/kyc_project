from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
import os

app = Flask(__name__)

# Load Haar Cascade
haar_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def extract_face(image_path):
    """Extract face from a given image path using Haar Cascade."""
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = haar_cascade.detectMultiScale(gray, 1.1, 4)
    if len(faces) == 0:
        return None
    x, y, w, h = faces[0]
    return gray[y:y+h, x:x+w]

def capture_face_from_video():
    """Capture a face from the live video using the webcam."""
    video_capture = cv2.VideoCapture(0)  # Opens the default camera
    face = None
    while True:
        ret, frame = video_capture.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = haar_cascade.detectMultiScale(gray, 1.1, 4)
        if len(faces) > 0:
            x, y, w, h = faces[0]
            face = gray[y:y+h, x:x+w]
            break
    video_capture.release()
    return face

def compare_faces(face1, face2):
    """Compare two face images and return True if they match, otherwise False."""
    if face1 is None or face2 is None:
        return False
    face1 = cv2.resize(face1, (100, 100))
    face2 = cv2.resize(face2, (100, 100))
    diff = cv2.absdiff(face1, face2)
    score = np.sum(diff)
    threshold = 5000  # Threshold for matching faces
    return score < threshold

@app.route('/match_faces', methods=['POST'])
def match_faces():
    aadhaar_image_path = request.form['aadhaar_image_path']  # Local path to Aadhaar image
    if not os.path.exists(aadhaar_image_path):
        return jsonify({"error": "Aadhaar image path does not exist."}), 400

    # Extract face from Aadhaar document
    document_face = extract_face(aadhaar_image_path)
    if document_face is None:
        return jsonify({"error": "No face found in Aadhaar image."}), 400

    # Capture face from live video
    live_video_face = capture_face_from_video()
    if live_video_face is None:
        return jsonify({"error": "No face found in live video."}), 400

    # Compare the two faces
    if compare_faces(document_face, live_video_face):
        return jsonify({"result": "FACE MATCHED"}), 200
    else:
        return jsonify({"result": "FACE UNMATCHED"}), 400

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
