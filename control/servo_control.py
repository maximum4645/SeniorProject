#!/usr/bin/env python3
"""
servo_control.py

Module for trapdoor servo logic using a PCA9685 + SG90 servos.
Wraps the exact timing and angles from test_servo_control_3.py.
"""

import board
import busio
import time
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo

from config import (
    TRAPDOOR_LEFT_CHANNEL,
    TRAPDOOR_RIGHT_CHANNEL,
    LOCK_SERVO_CHANNEL,
    LEFT_UP,
    LEFT_DOWN,
    RIGHT_UP,
    RIGHT_DOWN,
    UNLOCK_ANGLE,
    LOCK_ANGLE,
)

# Module‐level PCA and servo objects (same naming as the test)
_pca = None
servo_left = None
servo_right = None
servo_lock = None

def init_servo():
    """Initialize the PCA9685 board and create Servo objects."""
    global _pca, servo_left, servo_right, servo_lock
    i2c = busio.I2C(board.SCL, board.SDA)
    _pca = PCA9685(i2c)
    _pca.frequency = 50  # SG90s use ~50 Hz

    servo_left  = servo.Servo(_pca.channels[TRAPDOOR_LEFT_CHANNEL],  min_pulse=500, max_pulse=2400)
    servo_right = servo.Servo(_pca.channels[TRAPDOOR_RIGHT_CHANNEL], min_pulse=500, max_pulse=2400)
    servo_lock  = servo.Servo(_pca.channels[LOCK_SERVO_CHANNEL],     min_pulse=500, max_pulse=2400)

def open_trapdoor():

    print("Opening flaps...")
    time.sleep(1)
    servo_left.angle  = LEFT_UP
    servo_right.angle = RIGHT_UP
    time.sleep(1)
    servo_lock.angle  = UNLOCK_ANGLE
    time.sleep(1)
    servo_left.angle  = LEFT_DOWN
    servo_right.angle = RIGHT_DOWN
    print("Flaps OPENED")
    time.sleep(2)

def close_trapdoor():

    print("Closing flaps...")
    time.sleep(1)
    servo_left.angle  = LEFT_UP
    servo_right.angle = RIGHT_UP
    time.sleep(1)
    servo_lock.angle  = LOCK_ANGLE
    time.sleep(1)
    servo_left.angle  = LEFT_DOWN
    servo_right.angle = RIGHT_DOWN
    print("Flaps CLOSED")
    time.sleep(1)

def cleanup_servo():
    """Deinitialize the PCA9685 to stop sending PWM."""
    if _pca:
        _pca.deinit()
