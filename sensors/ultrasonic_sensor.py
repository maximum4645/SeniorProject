#!/usr/bin/env python3
"""
ultrasonic_sensor.py

Module for ultrasonic sensor logic, providing init and read_distance functions.
"""

import RPi.GPIO as GPIO
import time
from config import ULTRASONIC_TRIGGER_PIN, ULTRASONIC_ECHO_PIN

def init_ultrasonic():
    """Initialize the ultrasonic sensor GPIO pins."""
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(ULTRASONIC_TRIGGER_PIN, GPIO.OUT)
    GPIO.setup(ULTRASONIC_ECHO_PIN, GPIO.IN)
    GPIO.output(ULTRASONIC_TRIGGER_PIN, False)
    time.sleep(0.1)  # Allow sensor to settle

def read_distance() -> float:
    """Measure and return distance in cm using the ultrasonic sensor."""
    # Trigger a 10 µs pulse
    GPIO.output(ULTRASONIC_TRIGGER_PIN, True)
    time.sleep(0.00001)
    GPIO.output(ULTRASONIC_TRIGGER_PIN, False)

    # Wait for echo start
    start_time = time.time()
    timeout = start_time + 0.04
    while GPIO.input(ULTRASONIC_ECHO_PIN) == 0 and time.time() < timeout:
        start_time = time.time()

    # Wait for echo end
    stop_time = time.time()
    timeout = stop_time + 0.04
    while GPIO.input(ULTRASONIC_ECHO_PIN) == 1 and time.time() < timeout:
        stop_time = time.time()

    # Compute distance (speed of sound ~34300 cm/s)
    elapsed = stop_time - start_time
    return (elapsed * 34300) / 2

def cleanup():
    """Clean up GPIO resources used by the ultrasonic sensor."""
    GPIO.cleanup([ULTRASONIC_TRIGGER_PIN, ULTRASONIC_ECHO_PIN])
