#!/usr/bin/env python3
"""
test_servo_control_2.py
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
servo_left = servo.Servo(pca.channels[0], min_pulse=500, max_pulse=2400)
servo_right = servo.Servo(pca.channels[15], min_pulse=500, max_pulse=2400)
servo_lock = servo.Servo(pca.channels[8], min_pulse=500, max_pulse=2400)

# 3) Define positions (shared mapping for both servos)
SERVO_UP = 90
SERVO_DOWN   = 0
UNLOCK_ANGLE = 130
LOCK_ANGLE = 0

try:
    while True:
        print("Unlocking...")
        time.sleep(1)
        servo_lock.angle = UNLOCK_ANGLE
        time.sleep(2)
        print("Locking...")
        time.sleep(1)
        servo_lock.angle = LOCK_ANGLE
        time.sleep(2)

except KeyboardInterrupt:
    print("Interrupted by user.")
    pca.deinit()
