#!/usr/bin/env python3
"""
ultrasonic_sensor.py

Module for ultrasonic sensor logic, providing initialization and distance measurement.
"""

import RPi.GPIO as GPIO
import time
from config import ULTRASONIC_TRIGGER_PIN, ULTRASONIC_ECHO_PIN, DISTANCE_THRESHOLD

def initialize():
    """Initialize the ultrasonic sensor GPIO pins."""
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(ULTRASONIC_TRIGGER_PIN, GPIO.OUT)
    GPIO.setup(ULTRASONIC_ECHO_PIN, GPIO.IN)
    GPIO.output(ULTRASONIC_TRIGGER_PIN, False)
    time.sleep(0.1)  # Allow sensor to settle

def measure_distance():
    """Measure distance using the ultrasonic sensor."""
    # Send a 10 µs pulse to trigger the sensor
    GPIO.output(ULTRASONIC_TRIGGER_PIN, True)
    time.sleep(0.00001)  # 10 µs pulse
    GPIO.output(ULTRASONIC_TRIGGER_PIN, False)

    # Wait for the echo to start and end
    start_time = time.time()
    timeout = start_time + 0.04  # 40 ms timeout
    while GPIO.input(ULTRASONIC_ECHO_PIN) == 0 and time.time() < timeout:
        start_time = time.time()

    stop_time = time.time()
    timeout = stop_time + 0.04  # 40 ms timeout
    while GPIO.input(ULTRASONIC_ECHO_PIN) == 1 and time.time() < timeout:
        stop_time = time.time()

    # Calculate the distance (speed of sound is ~34300 cm/s)
    time_elapsed = stop_time - start_time
    distance = (time_elapsed * 34300) / 2
    return distance

def is_object_detected():
    """Return True if an object is within the detection threshold."""
    return measure_distance() < DISTANCE_THRESHOLD

if __name__ == "__main__":
    try:
        initialize()
        while True:
            distance = measure_distance()
            if is_object_detected():
                print(f"Object detected! Distance: {distance:.2f} cm")
            else:
                print(f"No object detected. Distance: {distance:.2f} cm")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nMeasurement stopped by user.")
    finally:
        GPIO.cleanup()
