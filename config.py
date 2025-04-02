#!/usr/bin/env python3
"""
config.py - Global configuration for the Smart Bin project.
"""

import os

# ----------------------------
# GPIO Pin Configuration (using BCM numbering)
# ----------------------------
# Ultrasonic Sensor Pins
ULTRASONIC_TRIGGER_PIN = 23
ULTRASONIC_ECHO_PIN = 24

# ----------------------------
# Sensor Thresholds & Timing (in appropriate units)
# ----------------------------
DISTANCE_THRESHOLD = 20      # Distance (in cm)
POLLING_INTERVAL = 0.5           # Seconds between sensor readings

# ----------------------------
# Camera Settings
# ----------------------------
CAMERA_RESOLUTION = (640, 480)   # Resolution for image capture/streaming

# ----------------------------
# Data Collection / Image Save Directory
# ----------------------------
IMAGE_SAVE_DIR = os.path.join("images")
if not os.path.exists(IMAGE_SAVE_DIR):
    os.makedirs(IMAGE_SAVE_DIR)
