#!/usr/bin/env python3
"""
test_servo_control.py

This script controls two SG90-like servos on channels 3 and 8 of a PCA9685 board.
It uses the adafruit_motor.servo module to automatically convert angles into the
correct PWM signal. The servo on channel 3 moves between 0° (closed) and 90° (open),
while the servo on channel 8 (mounted oppositely) moves between 180° (closed) and 90° (open).

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

# 2) Create servo objects on channels 3 and 8
#    Using 500 µs for min_pulse and 2400 µs for max_pulse (per your SG90 datasheet)
servo3 = servo.Servo(pca.channels[3], min_pulse=500, max_pulse=2400)
servo8 = servo.Servo(pca.channels[7], min_pulse=500, max_pulse=2400)

# 3) Define the positions for each servo
#    Channel 3: moves from 0° (closed) to 90° (open)
SERVO_3_CLOSED = 0
SERVO_3_OPEN   = 90

#    Channel 8: mounted oppositely, so moves from 180° (closed) to 90° (open)
SERVO_8_CLOSED = 0
SERVO_8_OPEN   = 90

try:
    while True:
        # Move servos to the "closed" position
        servo3.angle = SERVO_3_CLOSED
        servo8.angle = SERVO_8_CLOSED
        print("Flaps closed: Servo 3 -> 0°, Servo 8 -> 180°")
        time.sleep(3)  # Give time for movement

        # Move servos to the "open" position
        servo3.angle = SERVO_3_OPEN
        servo8.angle = SERVO_8_OPEN
        print("Flaps open: Servo 3 -> 90°, Servo 8 -> 90°")
        time.sleep(3)

except KeyboardInterrupt:
    print("Interrupted by user. Stopping servo signals.")
    pca.deinit()
