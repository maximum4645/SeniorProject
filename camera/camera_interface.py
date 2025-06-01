#!/usr/bin/env python3
"""
camera_interface.py

Provides a Flask web interface for streaming the Pi Camera feed via MJPEG
and capturing images with a dropdown selection.
Uses the base camera module (camera_capture.py) for camera functions.
"""

import os
import sys

SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import re
import cv2
from flask import Flask, render_template, Response, request, redirect, flash, url_for
from camera.camera_capture import initialize, capture_image
from config import IMAGE_SAVE_DIR

app = Flask(__name__)
app.secret_key = 'pi'  # Replace with a secure key for production

# Initialize the camera using the base module.
camera = initialize(mode="video")

# Ensure the image save directory exists.
os.makedirs(IMAGE_SAVE_DIR, exist_ok=True)

def gen_frames():
    """Generator that continuously captures frames and yields them as MJPEG."""
    while True:
        frame = capture_image()
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    """Render the main page with the live video stream and capture button."""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Return the MJPEG video stream."""
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/capture', methods=['POST'])
def capture():
    """
    Capture an image using the camera.
    The selected image class from the form is used to determine the save location.
    """
    image_class = request.form.get('image_class', '').lower()
    if image_class not in ['cardboard', 'plastic', 'metal', 'organic']:
        flash("Invalid class selected!")
        return redirect(url_for('index'))
    
    # Define save directory based on class.
    save_dir = os.path.join(IMAGE_SAVE_DIR, image_class)
    os.makedirs(save_dir, exist_ok=True)
    
    frame = capture_image()
    
    # Determine sequential filename (e.g., plastic1.jpg, plastic2.jpg, etc.)
    existing_files = os.listdir(save_dir)
    max_index = 0
    pattern = re.compile(r'^' + re.escape(image_class) + r'(\d+)\.jpg$')
    for filename in existing_files:
        match = pattern.match(filename)
        if match:
            num = int(match.group(1))
            if num > max_index:
                max_index = num
    next_index = max_index + 1
    filename = f"{image_class}{next_index}.jpg"
    full_path = os.path.join(save_dir, filename)
    
    cv2.imwrite(full_path, frame)
    flash(f"Captured image saved as {full_path}")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
