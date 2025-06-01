#!/usr/bin/env python3
"""
camera_capture.py

Base module for camera operations.
Provides:
  - initialize(mode="still"): Initialize Pi Camera in still or video mode.
  - capture_image(): Grab one frame (always returns a BGR numpy array).
"""

import cv2
from picamera2 import Picamera2
from config import CAMERA_RESOLUTION

# Global camera instance
camera = None

def initialize(mode="still"):
    """
    Initialize the Pi Camera.
    - mode="still"  → use create_still_configuration()
    - mode="video"  → use create_video_configuration()
    Returns the Picamera2 object.
    """
    global camera
    camera = Picamera2()

    if mode == "video":
        cfg = camera.create_video_configuration(main={"size": CAMERA_RESOLUTION})
    else:
        cfg = camera.create_still_configuration(main={"size": CAMERA_RESOLUTION})

    camera.configure(cfg)
    camera.start()
    return camera

def capture_image():
    """
    Capture a single image from the camera and return it as a BGR numpy array.
    Requires that initialize() was called first.
    """
    global camera
    if camera is None:
        raise RuntimeError("Camera not initialized. Call initialize() first.")

    rgb = camera.capture_array()            # returns H×W×3 RGB
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

if __name__ == '__main__':
    # Quick test: still mode
    cam = initialize(mode="still")
    import time
    time.sleep(2)
    frame = capture_image()
    cv2.imwrite("test_still.jpg", frame)
    cam.stop()
