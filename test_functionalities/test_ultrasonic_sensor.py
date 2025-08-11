#!/usr/bin/env python3
"""
test_ultrasonic_sensor.py

If the measured distance is below a defined threshold (e.g., 10 cm),
the script will print that object is detected.
"""

import RPi.GPIO as GPIO
import time

# Use Broadcom (BCM) pin numbering
GPIO.setmode(GPIO.BCM)

# Define the GPIO pins for the ultrasonic sensor
TRIG_PIN = 23
ECHO_PIN = 24

# Setup the GPIO pins: TRIG as output, ECHO as input.
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

# Set the threshold distance (in cm) for object detection
DISTANCE_THRESHOLD = 10  # Adjust this value based on your setup

def measure_distance():
    # Ensure the trigger pin is low
    GPIO.output(TRIG_PIN, False)
    time.sleep(0.0002)  # Short delay to settle the sensor

    # Send a 10 microsecond pulse to trigger the sensor
    GPIO.output(TRIG_PIN, True)
    time.sleep(0.00001)  # 10 µs pulse
    GPIO.output(TRIG_PIN, False)

    # Wait for the echo pin to go high and record the start time
    start_time = time.time()
    timeout = start_time + 0.04  # 40 ms timeout
    while GPIO.input(ECHO_PIN) == 0 and time.time() < timeout:
        pass
    if GPIO.input(ECHO_PIN) == 0:
        return None  # No echo received

    start_time = time.time()

    # Wait for the echo pin to go low and record the end time
    timeout = start_time + 0.04  # 40 ms timeout
    while GPIO.input(ECHO_PIN) == 1 and time.time() < timeout:
        pass
    if GPIO.input(ECHO_PIN) == 1:
        return None  # Echo never went low

    stop_time = time.time()

    # Calculate the distance (speed of sound is ~34300 cm/s)
    time_elapsed = stop_time - start_time
    distance = (time_elapsed * 34300) / 2
    return distance

try:
    while True:
        dist = measure_distance()
        if dist is None:
            print("No sensor connected!")
        elif dist <= DISTANCE_THRESHOLD:
            print("Object detected! Distance: {:.2f} cm".format(dist))
        else:
            print("No object detected. Distance: {:.2f} cm".format(dist))
        time.sleep(1)

except KeyboardInterrupt:
    print("\nMeasurement stopped by user.")

finally:
    GPIO.cleanup()
