#!/usr/bin/env python3
"""
test_servo_control.py

Controls two SG90-like servos on channels 3 and 8 of a PCA9685 board.
Both flaps are CLOSED at 90° and OPEN at 0°.

Pulse width range is set to 500–2400 µs (typical SG90). If your horn binds
near 0° or 90°, adjust min_pulse/max_pulse slightly or add small angle offsets.
"""

import time
import board
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo

# 1) Initialize I2C and PCA9685
i2c = board.I2C()         # Enable I2C on the Pi first (raspi-config)
pca = PCA9685(i2c)
pca.frequency = 50        # SG90s use ~50 Hz

# 2) Create servo objects on channels 3 and 8
servo_left = servo.Servo(pca.channels[15], min_pulse=500, max_pulse=2400)
servo_right = servo.Servo(pca.channels[0], min_pulse=500, max_pulse=2400)
servo_lock = servo.Servo(pca.channels[8], min_pulse=500, max_pulse=2400)

# 3) Define positions (shared mapping for both servos)
LEFT_UP = 110
LEFT_DOWN   = 0
RIGHT_UP = 0
RIGHT_DOWN = 110
UNLOCK_ANGLE = 120
LOCK_ANGLE = 0

try:
    while True:
        print("Unlocking...")
        time.sleep(1)
        servo_lock.angle = UNLOCK_ANGLE
        time.sleep(1)

        # Close
        print("Closing flaps...")
        time.sleep(1)
        servo_left.angle = LEFT_UP
        servo_right.angle = RIGHT_UP
        time.sleep(1)
        servo_lock.angle = LOCK_ANGLE
        time.sleep(1)
        servo_left.angle = LEFT_DOWN
        servo_right.angle = RIGHT_DOWN
        print("Flaps CLOSED")
        time.sleep(2)

        # Open
        print("Opening flaps...")
        time.sleep(1)
        servo_left.angle = LEFT_UP
        servo_right.angle = RIGHT_UP
        time.sleep(1)
        servo_lock.angle = UNLOCK_ANGLE
        time.sleep(1)
        servo_left.angle = LEFT_DOWN
        servo_right.angle = RIGHT_DOWN
        print("Flaps OPENED")
        time.sleep(2)

except KeyboardInterrupt:
    print("Interrupted by user.")
    pca.deinit()
