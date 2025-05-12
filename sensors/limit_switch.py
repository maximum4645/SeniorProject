#!/usr/bin/env python3
"""
limit_switch.py: Module for handling the limit switch functionality.

This module provides functions to initialize the GPIO for the limit switch,
read its current state (activated or not), and properly clean up the GPIO 
settings when done. The pin configuration is imported from config.py.
"""

import time  # only needed for the test block delays
import RPi.GPIO as GPIO
from config import LIMIT_SWITCH_PIN

def init_limit_switch():
    """
    Initializes the GPIO setup for the limit switch.
    
    Configures the selected GPIO pin as an input with a pull-up resistor
    (common configuration for limit switches).
    """
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LIMIT_SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def is_limit_switch_activated():
    """
    Checks if the limit switch is activated.
    
    Returns:
        bool: True if the limit switch is activated (i.e., the input reads LOW
              when using a pull-up resistor configuration), otherwise False.
    """
    return GPIO.input(LIMIT_SWITCH_PIN) == GPIO.LOW

def cleanup_limit_switch():
    """
    Cleans up the GPIO configuration.
    
    Should be called when limit switch operations are complete to free the GPIO resources.
    """
    GPIO.cleanup()

# Test block: Runs the module directly to verify the limit switch behavior.
if __name__ == '__main__':
    init_limit_switch()
    print(f"Starting limit switch test. Monitoring GPIO pin {LIMIT_SWITCH_PIN}.")
    print("Activate the switch to see updates. Press Ctrl+C to exit.")
    
    try:
        while True:
            if is_limit_switch_activated():
                print("Limit switch activated!")
            else:
                print("Limit switch not activated.")
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Test interrupted by user. Exiting...")
    finally:
        cleanup_limit_switch()
