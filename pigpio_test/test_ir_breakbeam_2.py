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

# Optional: uncomment to debounce very short glitches (microseconds)
# pi.set_glitch_filter(BREAKBEAM_PIN, 2000)  # 2000 µs = 2 ms

def _beam_callback(gpio, level, tick):
    # level: 0 = LOW, 1 = HIGH, 2 = no-change watchdog (ignore)
    if level == 0:
        print("Beam broken - object detected!")
    elif level == 1:
        print("Beam intact - no object detected.")

# Register interrupt on both edges so we get messages for break + restore
cb = pi.callback(BREAKBEAM_PIN, pigpio.EITHER_EDGE, _beam_callback)

try:
    # Print the initial state once
    initial = pi.read(BREAKBEAM_PIN)
    if initial == 1:
        print("Beam intact - no object detected.")
    else:
        print("Beam broken - object detected!")

    # Keep the program alive while interrupts do the work
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\nTest stopped by user.")

finally:
    cb.cancel()
    pi.stop()
