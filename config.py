#!/usr/bin/env python3
"""
config.py - Global configuration for senior project.
"""

import os

# ----------------------------
# GPIO Pin Configuration (using BCM numbering)
# ----------------------------
# PCA9685 I2C
I2C_SDA_PIN = 2    # Physical pin 3
I2C_SCL_PIN = 3    # Physical pin 5

# Limit Switch
LIMIT_SWITCH_PIN = 17  # Physical pin 11

# Ultrasonic Sensor
ULTRASONIC_TRIGGER_PIN = 23  # Physical pin 16
ULTRASONIC_ECHO_PIN    = 24  # Physical pin 18

# DRV8825 Stepper Motor Driver
STEPPER_STEP_PIN = 5   # Physical pin 29
STEPPER_DIR_PIN  = 6   # Physical pin 31

# ----------------------------
# Sensor Thresholds & Timing (in appropriate units)
# ----------------------------
DETECTION_THRESHOLD_CM = 20   # Was DISTANCE_THRESHOLD; renamed for clarity
CLEARANCE_THRESHOLD_CM = 15   # New: waiting‐for‐clearance threshold
POLLING_INTERVAL       = 0.5  # Seconds between sensor readings

# ----------------------------
# Control Parameters
# ----------------------------
STEPPER_STEPS_PER_REV = 200    # Steps per revolution
SERVO_OPEN_ANGLE      = 90     # Servo open position
SERVO_CLOSED_ANGLE    = 0      # Servo closed position

# Which PCA9685 channels are your trapdoor servos?
TRAPDOOR_SERVOS = [3, 7]

# If a servo is mounted “backwards,” invert its angle:
# angle_to_set = 180 - base_angle
SERVO_INVERT = {
    3: False,
    7: False
}
# ----------------------------
# Camera Settings
# ----------------------------
CAMERA_RESOLUTION = (640, 480)

# ----------------------------
# Class-to-channel mapping
# ----------------------------
CLASS_TO_CHANNEL = {
    'plastic': 1,
    'metal':   2,
    'paper':   3,
    'organic': 4
}

# ----------------------------
# Data Collection / Image Save Directory
# ----------------------------
IMAGE_SAVE_DIR = os.path.join("images")
if not os.path.exists(IMAGE_SAVE_DIR):
    os.makedirs(IMAGE_SAVE_DIR)

# ----------------------------
# Path to your TFLite file (relative to SeniorProject/)
MODEL_PATH = os.path.join("model", "mobilenet_v2.tflite")
# ----------------------------
