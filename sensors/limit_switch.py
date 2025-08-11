#!/usr/bin/env python3
"""
limit_switch.py: Module for handling the limit switch functionality.

This module provides functions to initialize the GPIO for the limit switch,
read its current state (activated or not), and properly clean up the GPIO 
settings when done. The pin configuration is imported from config.py.
"""

import os
import sys

SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import time  # only needed for the test block delays
import RPi.GPIO as GPIO
from config import LIMIT_SWITCH_PIN_LEFT, LIMIT_SWITCH_PIN_RIGHT

def init_limit_switch():
    """
    Initializes the GPIO setup for the limit switch.
    
    Configures the selected GPIO pin as an input with a pull-up resistor
    (common configuration for limit switches).
    """
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LIMIT_SWITCH_PIN_LEFT,  GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(LIMIT_SWITCH_PIN_RIGHT, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def is_left_switch_activated():
    return GPIO.input(LIMIT_SWITCH_PIN_LEFT) == GPIO.LOW

def is_right_switch_activated():
    return GPIO.input(LIMIT_SWITCH_PIN_RIGHT) == GPIO.LOW

def cleanup_limit_switch():
    """
    Cleans up the GPIO configuration.
    
    Should be called when limit switch operations are complete to free the GPIO resources.
    """
    GPIO.cleanup()

# Test block: Runs the module directly to verify the limit switch behavior.
if __name__ == '__main__':
    init_limit_switch()
    print(f"Starting limit switch test. Monitoring pins {LIMIT_SWITCH_PIN_LEFT} (left) and {LIMIT_SWITCH_PIN_RIGHT} (right).")
    print("Activate the switch to see updates. Press Ctrl+C to exit.")
    
    try:
        while True:
            left = is_left_switch_activated()
            right = is_right_switch_activated()
            left_str  = "Activated    " if left  else "Not activated"
            right_str = "Activated    " if right else "Not activated"
            print(f"Left: {left_str}, Right: {right_str}")
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Test interrupted by user. Exiting...")
    finally:
        cleanup_limit_switch()
