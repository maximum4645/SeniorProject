#!/usr/bin/env python3
"""
Test script for the real limit switch hardware.

This script directly accesses the GPIO pin where the limit switch is connected,
and continuously polls its state. When the limit switch is activated, the input
should read LOW (assuming a pull-up resistor configuration). Adjust the GPIO pin 
and pull-up/pull-down settings as needed for your wiring.

Press Ctrl+C to exit.
"""

import time
import RPi.GPIO as GPIO

# Configure the GPIO pin for the limit switch.
# Update this value to match your hardware wiring.
LIMIT_SWITCH_PIN = 17

def setup_gpio():
    # Use BCM pin numbering.
    GPIO.setmode(GPIO.BCM)
    # Configure the pin as input.
    # If your switch wiring requires a pull-up resistor (common case), use GPIO.PUD_UP.
    # Otherwise, if you need a pull-down, change to GPIO.PUD_DOWN.
    GPIO.setup(LIMIT_SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def main():
    setup_gpio()
    print("Starting limit switch test. Monitoring pin {}.".format(LIMIT_SWITCH_PIN))
    print("Activate the switch and observe the output. Press Ctrl+C to exit.")
    
    try:
        while True:
            # Read the state of the limit switch.
            # With pull-up enabled, the input is HIGH when not pressed, and LOW when pressed.
            if GPIO.input(LIMIT_SWITCH_PIN) == GPIO.LOW:
                print("Limit switch activated!")
            else:
                print("Limit switch not activated.")
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Test interrupted by user. Exiting...")
    finally:
        GPIO.cleanup()

if __name__ == '__main__':
    main()
