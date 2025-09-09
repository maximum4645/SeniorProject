#!/usr/bin/env python3
"""
test_ir_breakbeam.py

This script tests an IR break-beam sensor (emitter + receiver).
If the beam is broken (object passes through), the script will
print that the object is detected. Otherwise, it will print that
the path is clear.

Wiring:
- Emitter (TX): Red -> 5V, Black -> GND
- Receiver (RX): Red -> 5V, Black -> GND, White -> GPIO pin
- IMPORTANT: Use a pull-up to 3.3V (either internal or external).
"""

import RPi.GPIO as GPIO
import time

# Use Broadcom (BCM) pin numbering
GPIO.setmode(GPIO.BCM)

# Define the GPIO pin for the break-beam receiver output
BREAKBEAM_PIN = 23  # Change if you use another pin

# Setup the GPIO pin: input with pull-up
# (internal pull-up ensures the pin idles HIGH when the beam is intact)
GPIO.setup(BREAKBEAM_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    while True:
        if GPIO.input(BREAKBEAM_PIN) == GPIO.HIGH:
            print("Beam intact - no object detected.")
        else:
            print("Beam broken - object detected!")
        time.sleep(0.5)  # Adjust polling interval as needed

except KeyboardInterrupt:
    print("\nTest stopped by user.")

finally:
    GPIO.cleanup()
