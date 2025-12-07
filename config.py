#!/usr/bin/env python3
"""
config_2.py - Global configuration for senior project (stepper/pigpio tunables included).
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

# DRV8825 Stepper Motor Driver
STEPPER_STEP_PIN = 6   # Physical pin 31
STEPPER_DIR_PIN  = 5   # Physical pin 29
STEPPER_ENABLE_PIN = None  # Set to a BCM pin if you wire EN; keep None to tie EN low

# IR Break-beam Sensor
BREAKBEAM_PIN = 23  # BCM numbering
POLLING_INTERVAL = 0.5  # Seconds between sensor readings

# ----------------------------
# Control Parameters
# ----------------------------
STEPPER_STEPS_PER_REV = 200   # Full-step steps per revolution of motor

# Motion timing (seconds)
STEPPER_STEP_DELAY_S = 0.0008   # Travel speed half-period (HIGH or LOW duration)
HOME_STEP_DELAY_S    = 0.005    # Safer/slower homing

# Pigpio filters/loop timing
PIGPIO_GLITCH_US         = 2000   # Debounce for mechanical switches (microseconds)
PIGPIO_MONITOR_SLEEP_S   = 0.001  # Sleep while monitoring wave playback

# Channel spacing and mechanics
CHANNEL_SPACING_CM     = 19    # spacing between waste channels
BELT_PITCH_MM          = 2     # GT2 belt pitch
PULLEY_TEETH           = 20    # pulley teeth count
TRAVEL_PER_REV_CM      = (PULLEY_TEETH * BELT_PITCH_MM) / 10  # mm to cm

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
    'general': 1,
    'plastic': 2,
    'paper': 3,
    'metal': 4
}
IMAGE_CLASSES = ['general', 'plastic', 'paper', 'metal']

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

BIN_ID = "bin_1"
SERVER_URL = "http://192.168.1.43:5000/"
