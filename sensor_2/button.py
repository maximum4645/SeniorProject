#!/usr/bin/env python3
"""
sensor_2/button.py

PCF8574 button module (Adafruit/CircuitPython style).
Provides init, read, wait-for-press, and cleanup helpers.
"""

import time
import board
from digitalio import Direction
from adafruit_pcf8574 import PCF8574

# Config — adjust to your wiring
I2C_ADDR = 0x20
BUTTON_PINS = [0, 1, 2, 3]   # P0..P3 map to buttons 1..4
DEBOUNCE_S = 0.02

# Module state
_pcf = None
_pins = None
_last_state = None
_last_change = None

def init_buttons():
    """Initialize I2C and configure PCF8574 pins as inputs."""
    global _pcf, _pins, _last_state, _last_change
    i2c = board.I2C()
    _pcf = PCF8574(i2c, address=I2C_ADDR)
    _pins = [_pcf.get_pin(p) for p in BUTTON_PINS]
    for p in _pins:
        p.direction = Direction.INPUT
    _last_state = [True] * len(_pins)   # True=HIGH (not pressed)
    _last_change = [0.0] * len(_pins)

def read_pressed_indices():
    """
    Return a list of zero-based indices currently pressed (active LOW),
    debounced by DEBOUNCE_S.
    """
    pressed = []
    now = time.time()
    for idx, pin in enumerate(_pins):
        raw = pin.value  # True=not pressed, False=pressed
        if raw != _last_state[idx] and (now - _last_change[idx]) >= DEBOUNCE_S:
            _last_state[idx] = raw
            _last_change[idx] = now
        if _last_state[idx] is False:
            pressed.append(idx)
    return pressed

def first_pressed_1to4():
    """
    Return 1..4 for the first pressed button (debounced), or None if none.
    Prioritizes lower-index buttons if multiple are down.
    """
    for idx in range(len(_pins)):
        if _last_state[idx] is False:
            return idx + 1
    return None

def wait_for_button(timeout=None):
    """
    Block until any button is pressed (debounced). Returns 1..4, or None on timeout.
    """
    start = time.time()
    while True:
        _ = read_pressed_indices()
        ch = first_pressed_1to4()
        if ch is not None:
            return ch
        if timeout is not None and (time.time() - start) >= timeout:
            return None
        time.sleep(0.01)

def cleanup():
    """Placeholder for symmetry; nothing required for CircuitPython PCF8574."""
    pass
