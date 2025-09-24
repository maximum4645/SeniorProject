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

import time
import pigpio

# Define the GPIO pin for the break-beam receiver output (BCM numbering)
BREAKBEAM_PIN = 23  # Change if you use another pin

# Initialize pigpio and configure the pin as input with pull-up
pi = pigpio.pi()
if not pi.connected:
    raise RuntimeError("pigpio daemon not running. Start with: sudo pigpiod")

pi.set_mode(BREAKBEAM_PIN, pigpio.INPUT)
pi.set_pull_up_down(BREAKBEAM_PIN, pigpio.PUD_UP)  # idle HIGH when beam intact

try:
    while True:
        if pi.read(BREAKBEAM_PIN) == 1:
            print("Beam intact - no object detected.")
        else:
            print("Beam broken - object detected!")
        time.sleep(0.5)  # Adjust polling interval as needed

except KeyboardInterrupt:
    print("\nTest stopped by user.")

finally:
    pi.stop()
