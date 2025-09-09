#!/usr/bin/env python3
"""
test_ir_breakbeam.py

This script tests an IR break-beam sensor (emitter + receiver).
If the beam is broken (object passes through), the script will
print that the object is detected.

Wiring:
- Emitter (TX): Red -> 5V, Black -> GND
- Receiver (RX): Red -> 5V, Black -> GND, White -> GPIO pin
- IMPORTANT: Use a pull-up to 3.3V (either internal or external).

Notes:
- Uses edge-triggered detection (interrupt-style) instead of polling.
- We detect a FALLING edge because the receiver pulls the line LOW when the beam breaks.
"""

import RPi.GPIO as GPIO
import time
import signal
import sys

# Use Broadcom (BCM) pin numbering
GPIO.setmode(GPIO.BCM)

# Define the GPIO pin for the break-beam receiver output
BREAKBEAM_PIN = 23  # Change if you use another pin

# Setup the GPIO pin: input with pull-up
GPIO.setup(BREAKBEAM_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def beam_broken_callback(channel):
    # This callback runs immediately when the beam is broken (FALLING edge)
    print("Beam broken - object detected!")

# Register edge detection for FALLING edges (beam goes from HIGH -> LOW)
# bouncetime provides simple software debouncing (in milliseconds).
GPIO.add_event_detect(BREAKBEAM_PIN, GPIO.FALLING, callback=beam_broken_callback, bouncetime=10)

def handle_exit(signum, frame):
    print("\nTest stopped by user.")
    GPIO.cleanup()
    sys.exit(0)

# Graceful exit on Ctrl+C
signal.signal(signal.SIGINT, handle_exit)

try:
    # Keep the script alive while hardware interrupts do the work
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    handle_exit(None, None)
finally:
    GPIO.cleanup()
