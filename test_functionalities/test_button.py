#!/usr/bin/env python3
"""
test_button.py
---------------
Stand-alone test for 4 push buttons on a PCF8574 using the Adafruit stack.

Wiring:
- PCF8574 A0-A2 -> GND (address 0x20 unless changed)
- VCC -> 3.3V, GND -> GND
- Buttons connect P0..P3 to GND (active LOW).
"""

import time
import board
from digitalio import Direction
# pip install adafruit-circuitpython-pcf8574
from adafruit_pcf8574 import PCF8574

I2C_ADDR = 0x20
BUTTON_PINS = [0, 1, 2, 3]   # P0..P3 map to buttons 1..4
DEBOUNCE_S = 0.02            # 20 ms

def main():
    print("[INFO] PCF8574 button test (Adafruit style). Ctrl+C to exit.\n")

    i2c = board.I2C()
    pcf = PCF8574(i2c, address=I2C_ADDR)

    pins = [pcf.get_pin(p) for p in BUTTON_PINS]
    for p in pins:
        p.direction = Direction.INPUT  # quasi-bidirectional, internal pull-ups

    # Track last stable states for debouncing (True=HIGH=not pressed)
    last_state = [True] * len(pins)
    last_change = [0.0] * len(pins)

    try:
        while True:
            now = time.time()
            for idx, pin in enumerate(pins):
                raw = pin.value  # True=not pressed, False=pressed
                if raw != last_state[idx] and (now - last_change[idx]) >= DEBOUNCE_S:
                    last_state[idx] = raw
                    last_change[idx] = now
                    if raw is False:
                        print(f"[BUTTON] Button {idx+1} pressed")
                    else:
                        print(f"[BUTTON] Button {idx+1} released")
            time.sleep(0.01)
    except KeyboardInterrupt:
        print("\n[INFO] Exiting cleanly.")

if __name__ == "__main__":
    main()

