#!/usr/bin/env python3
"""
camera_capture.py

Base module for camera operations.
Provides:
  - initialize(): Initializes the Pi Camera.
  - capture_image(): Captures an image and returns it as a NumPy array in BGR format.
"""

import cv2
from picamera2 import Picamera2
from config import CAMERA_RESOLUTION

# Global camera instance
camera = None

def initialize():
    """Initialize the Pi Camera for capturing images."""
    global camera
    camera = Picamera2()
    video_config = camera.create_video_configuration(main={"size": CAMERA_RESOLUTION})
    camera.configure(video_config)
    return camera

def capture_image():
    """Capture an image from the camera and return it as a NumPy array (BGR format)."""
    global camera
    if camera is None:
        raise RuntimeError("Camera not initialized. Call initialize() first.")
    frame = camera.capture_array()
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    return frame

if __name__ == '__main__':
    initialize()
    frame = capture_image()
    cv2.imshow("Captured Image", frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
