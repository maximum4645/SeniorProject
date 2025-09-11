#!/usr/bin/env python3
"""
test_servo_control.py

This script controls two SG90-like servos on channels 3 and 7 of a PCA9685 board.
It uses the adafruit_motor.servo module to automatically convert angles into the
correct PWM signal. Both servos are configured so the flaps are 90° when CLOSED
and 0° when OPEN.

Pulse width range is set to 500–2400 µs, which corresponds to typical SG90 specs.
"""

import time
import board
import busio
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo

# 1) Initialize the I2C bus and PCA9685
i2c = board.I2C()  # Requires I2C to be enabled on the Pi
pca = PCA9685(i2c)
pca.frequency = 50  # 50 Hz is standard for SG90 servos

# 2) Create servo objects on channels 3 and 7
#    Using 500 µs for min_pulse and 2400 µs for max_pulse (per your SG90 datasheet)
servo3 = servo.Servo(pca.channels[3], min_pulse=500, max_pulse=2400)
servo7 = servo.Servo(pca.channels[7], min_pulse=500, max_pulse=2400)
servo_lock = servo.Servo(pca.channels[11], min_pulse=500, max_pulse=2400)

# 3) Define the positions for each servo
#    Both servos: 90° (closed) and 0° (open)
SERVO_3_CLOSED = 90
SERVO_3_OPEN   = 0

SERVO_7_CLOSED = 90
SERVO_7_OPEN   = 0

try:
    while True:
        # Move servos to the "closed" position
        servo3.angle = SERVO_3_CLOSED
        servo7.angle = SERVO_7_CLOSED
        servo_lock.angle = SERVO_7_CLOSED
        print("Flaps closed: Servo 3 is at 90°, Servo 7 is at 90°, Servo lock is at 90°")
        time.sleep(3)  # Give time for movement

        # Move servos to the "open" position
        servo3.angle = SERVO_3_OPEN
        servo7.angle = SERVO_7_OPEN
        servo_lock.angle = SERVO_7_OPEN
        print("Flaps open: Servo 3 is at 0°, Servo 7 is at 0°, Servo lock is at 0°")
        time.sleep(3)

except KeyboardInterrupt:
    print("Interrupted by user. Stopping servo signals.")
    pca.deinit()
