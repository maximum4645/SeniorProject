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
LIMIT_SWITCH_PIN_LEFT = 17  # Physical pin 11
LIMIT_SWITCH_PIN_RIGHT = 27 # Physical pin 13

# Ultrasonic Sensor
ULTRASONIC_TRIGGER_PIN = 23  # Physical pin 16
ULTRASONIC_ECHO_PIN    = 24  # Physical pin 18

# DRV8825 Stepper Motor Driver
STEPPER_STEP_PIN = 6   # Physical pin 31
STEPPER_DIR_PIN  = 5   # Physical pin 29

# IR Break-beam Sensor
BREAKBEAM_PIN = 23  # BCM numbering

# ----------------------------
# Sensor Thresholds & Timing (in appropriate units)
# ----------------------------
DETECTION_THRESHOLD_CM = 20   # Was DISTANCE_THRESHOLD; renamed for clarity
CLEARANCE_THRESHOLD_CM = 15   # New: waiting‐for‐clearance threshold
POLLING_INTERVAL       = 0.5  # Seconds between sensor readings

# ----------------------------
# Control Parameters
# ----------------------------
STEPPER_STEPS_PER_REV = 200   # Steps per revolution

# === Trapdoor servo channels (match test_servo_control_3.py) ===
TRAPDOOR_LEFT_CHANNEL  = 15   # servo_left
TRAPDOOR_RIGHT_CHANNEL = 0    # servo_right
LOCK_SERVO_CHANNEL     = 8    # servo_lock

# Keep this list for any code that iterates both flaps
TRAPDOOR_SERVOS = [TRAPDOOR_LEFT_CHANNEL, TRAPDOOR_RIGHT_CHANNEL]

# === Exact angles from test_servo_control_3.py ===
LEFT_UP      = 110
LEFT_DOWN    = 0
RIGHT_UP     = 0
RIGHT_DOWN   = 110
UNLOCK_ANGLE = 120
LOCK_ANGLE   = 0

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
MODEL_PATH = os.path.join("model", "model_1.tflite")
# ----------------------------
