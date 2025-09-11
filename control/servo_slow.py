#!/usr/bin/env python3
"""
servo_slow.py

Module for trapdoor servo logic using a PCA9685 + SG90 servos.
Identical API to servo_control.py, but moves with a slower, smooth ramp.

Adjust APPARENT_SPEED_DPS to change how slow/fast the motion feels.
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

# ===== User-tunable speed (degrees per second) =====
APPARENT_SPEED_DPS = 45.0   # lower = slower
UPDATE_HZ = 50.0            # update rate for ramp (50 Hz works well for hobby servos)

# Module-level PCA and servo objects
_pca = None
_servos = {}


def _slew_to(servo_obj, target_deg, dps=APPARENT_SPEED_DPS, update_hz=UPDATE_HZ, clamp=(0.0, 180.0)):
    """
    Move a positional hobby servo to `target_deg` at approx `dps` degrees/sec.
    Simple linear ramp; blocks until finished.

    If servo_obj.angle is None (first command), it snaps to target once.
    """
    lo, hi = clamp
    target = float(max(lo, min(hi, target_deg)))

    start = servo_obj.angle
    if start is None:
        servo_obj.angle = target
        return

    start = float(start)
    total = abs(target - start)
    if total < 1e-3 or dps <= 0.0:
        servo_obj.angle = target
        return

    dt = 1.0 / float(update_hz)
    step = dps * dt
    steps = max(1, int(total / step))

    for i in range(1, steps + 1):
        u = i / float(steps)
        current = start + (target - start) * u
        servo_obj.angle = current
        time.sleep(dt)


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
    """Invert angle if needed and command the servo with a slow ramp."""
    angle = 180 - base_angle if SERVO_INVERT.get(ch, False) else base_angle
    _slew_to(_servos[ch], angle)


def open_trapdoor():
    """Move both servos to the configured open angle (slowly)."""
    for ch in TRAPDOOR_SERVOS:
        _apply_angle(ch, SERVO_OPEN_ANGLE)


def close_trapdoor():
    """Move both servos to the configured closed angle (slowly)."""
    for ch in TRAPDOOR_SERVOS:
        _apply_angle(ch, SERVO_CLOSED_ANGLE)


def cleanup_servo():
    """Deinitialize the PCA9685 to stop sending PWM."""
    if _pca:
        _pca.deinit()
