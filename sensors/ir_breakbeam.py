#!/usr/bin/env python3
"""
ir_breakbeam.py

Module for IR break-beam sensor logic (polling method).
Provides init, state check, and cleanup functions.
"""

import RPi.GPIO as GPIO
from config import BREAKBEAM_PIN

def init_ir_breakbeam():
    """Initialize the IR break-beam sensor GPIO pin."""
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BREAKBEAM_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def is_beam_intact() -> bool:
    """Return True if beam is intact (no object detected)."""
    return GPIO.input(BREAKBEAM_PIN) == GPIO.HIGH

def is_beam_broken() -> bool:
    """Return True if beam is broken (object detected)."""
    return GPIO.input(BREAKBEAM_PIN) == GPIO.LOW

def cleanup():
    """Clean up GPIO resources used by the break-beam sensor."""
    GPIO.cleanup([BREAKBEAM_PIN])
