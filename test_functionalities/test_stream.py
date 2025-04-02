#!/usr/bin/env python3
"""
test_stream.py

A Flask app that:
  - Streams Pi camera feed via MJPEG at /video_feed
  - Renders index.html with a dropdown + "Capture" button
  - Captures an image on demand, saving it locally to images/<class>/classX.jpg
"""

import io
import os
import re
import time
import cv2
import numpy as np
from flask import Flask, render_template, Response, request, redirect, url_for, flash
from picamera2 import Picamera2

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure random key

# Set up Picamera2 for streaming
picam2 = Picamera2()
video_config = picam2.create_video_configuration(main={"size": (640, 480)})
picam2.configure(video_config)

# Define local directories for each class
class_directories = {
    "cardboard": "images/cardboard",
    "plastic": "images/plastic",
    "metal": "images/metal",
    "organic": "images/organic"
}

# Create directories if they don't exist
for directory in class_directories.values():
    os.makedirs(directory, exist_ok=True)

def gen_frames():
    """Generator that yields MJPEG frames from the camera."""
    picam2.start()
    while True:
        frame = picam2.capture_array()
        # Convert from RGB to BGR if needed
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    """Render the main page (index.html)."""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Return the MJPEG stream."""
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/capture', methods=['POST'])
def capture():
    image_class = request.form.get('image_class', '').lower()
    if image_class not in class_directories:
        flash("Invalid class selected!")
        return redirect(url_for('index'))

    save_dir = class_directories[image_class]
    frame = picam2.capture_array()
    # Convert from RGB to BGR if needed
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    
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
    flash(f"Captured image saved at {full_path}")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
