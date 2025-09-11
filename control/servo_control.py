#!/usr/bin/env python3
"""
servo_control.py

Module for trapdoor servo logic using a PCA9685 + SG90 servos.
Flap mapping: OPEN = 0°, CLOSED = 90° (before any per-channel inversion).
"""

import board
import busio
import time
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo

from config import (
    TRAPDOOR_SERVOS,
    SERVO_OPEN_ANGLE,
    SERVO_CLOSED_ANGLE,
    SERVO_INVERT,
)

# Module‐level PCA and servo objects
_pca = None
_servos = {}

def init_servo():
    """Initialize the PCA9685 board and create Servo objects."""
    global _pca, _servos
    i2c = busio.I2C(board.SCL, board.SDA)
    _pca = PCA9685(i2c)
    _pca.frequency = 50
    for ch in TRAPDOOR_SERVOS:
        _servos[ch] = servo.Servo(
            _pca.channels[ch],
            min_pulse=500,
            max_pulse=2400
        )

def _apply_angle(ch, base_angle):
    """Invert angle if needed and command the servo."""
    angle = 180 - base_angle if SERVO_INVERT.get(ch, False) else base_angle
    _servos[ch].angle = angle
    # small delay ensures servo has time to move
    time.sleep(0.2)

def open_trapdoor():
    """Move both servos to the configured open angle."""
    for ch in TRAPDOOR_SERVOS:
        _apply_angle(ch, SERVO_OPEN_ANGLE)

def close_trapdoor():
    """Move both servos to the configured closed angle."""
    for ch in TRAPDOOR_SERVOS:
        _apply_angle(ch, SERVO_CLOSED_ANGLE)

def cleanup_servo():
    """Deinitialize the PCA9685 to stop sending PWM."""
    if _pca:
        _pca.deinit()
