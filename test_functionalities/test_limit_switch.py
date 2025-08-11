#!/usr/bin/env python3
"""
Test script for the real limit switch hardware.

This script directly accesses the GPIO pins where the left and right limit switches are connected,
and continuously polls their states. When a switch is activated, the input reads LOW
(assuming a pull-up resistor configuration). Adjust the GPIO pins and pull-up/pull-down
settings as needed for your wiring.

Press Ctrl+C to exit.
"""

import time
import RPi.GPIO as GPIO

# Configure the GPIO pins for the left and right limit switches.
# Update these values to match your hardware wiring.
LIMIT_SWITCH_PIN_LEFT = 17   # Physical pin 11
LIMIT_SWITCH_PIN_RIGHT = 27  # Physical pin 13

def setup_gpio():
    # Use BCM pin numbering.
    GPIO.setmode(GPIO.BCM)
    # Configure each pin as input with pull-up resistor.
    GPIO.setup(LIMIT_SWITCH_PIN_LEFT,  GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(LIMIT_SWITCH_PIN_RIGHT, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def main():
    setup_gpio()
    print(f"Starting limit switch test. Monitoring pins {LIMIT_SWITCH_PIN_LEFT} (left) and {LIMIT_SWITCH_PIN_RIGHT} (right).")
    print("Activate the switches and observe the output. Press Ctrl+C to exit.")
    
    try:
        while True:
            left_state = GPIO.input(LIMIT_SWITCH_PIN_LEFT)
            right_state = GPIO.input(LIMIT_SWITCH_PIN_RIGHT)

            left_str = "Activated    " if left_state == GPIO.LOW else "Not activated"
            right_str = "Activated    " if right_state == GPIO.LOW else "Not activated"
            print(f"Left: {left_str}, Right: {right_str}")

            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Test interrupted by user. Exiting...")
    finally:
        GPIO.cleanup()

if __name__ == '__main__':
    main()
