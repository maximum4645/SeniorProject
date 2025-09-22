#!/usr/bin/env python3
"""
test_ir_breakbeam_3.py

Standalone test for an IR break-beam sensor using interrupts.
Natural two-condition flow:
- condition1: break event latched by interrupt
- condition2: we're READY (boolean)

When both hold: print, wait for clearance (beam intact), clear any stale event,
and go back to READY.
"""

import time
import threading
import RPi.GPIO as GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
try: GPIO.remove_event_detect(23)
except Exception: pass
try: GPIO.cleanup(23)
except Exception: pass

# --- Adjust if needed ---
BREAKBEAM_PIN = 23
BOUNCE_MS = 100
POLLING_INTERVAL = 0.02
# ------------------------

_break_event = threading.Event()

def _on_falling(channel):
    # Beam HIGH -> LOW = broken
    _break_event.set()

def is_beam_intact() -> bool:
    return GPIO.input(BREAKBEAM_PIN) == GPIO.HIGH

def clear_break_event():
    _break_event.clear()

def main():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BREAKBEAM_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(BREAKBEAM_PIN, GPIO.FALLING,
                          bouncetime=BOUNCE_MS,
                          callback=_on_falling)

    ready = True
    print("[TEST] READY (armed). Break the beam. Ctrl+C to exit.")

    try:
        while True:
            # condition1 (event latched) AND condition2 (we are ready)
            if ready and _break_event.is_set():
                print("[TEST] Beam broken !")
                ready = False  # enter 'sorting' (ignore further breaks)

                # Wait for clearance before going READY again
                print("[TEST] Waiting for clearance...")
                while not is_beam_intact():
                    time.sleep(POLLING_INTERVAL)

                # Drop any edges that may have occurred during 'sorting'
                clear_break_event()
                ready = True
                print("[TEST] Cleared - READY again")

            time.sleep(POLLING_INTERVAL)

    except KeyboardInterrupt:
        print("\n[TEST] Stopping…")
    finally:
        GPIO.remove_event_detect(BREAKBEAM_PIN)
        GPIO.cleanup([BREAKBEAM_PIN])
        print("[TEST] Cleaned up.")

if __name__ == "__main__":
    main()
