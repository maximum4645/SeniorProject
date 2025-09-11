#!/usr/bin/env python3
"""
Two-cycle demo script (hardcoded classification)

Cycle 1 -> move to channel 2, open/close trapdoor, return home
Cycle 2 -> move to channel 3, open/close trapdoor, return home

Purpose: Record a short video showcasing stepper + servo functionality.
Notes:
- No ultrasonic, camera, or ML model is used here.
- Channels here should match whatever indexing your `move_to_channel()` expects
  (i.e., the same indexing you already use in your project/config).
- Adjust the CHANNELS list if you want a different sequence.
"""
import time

from control.servo_control import (
    init_servo,
    open_trapdoor,
    close_trapdoor,
    cleanup_servo,
)
from control.stepper_control import (
    init_stepper,
    home_stepper,
    move_to_channel,
    cleanup_all,
)

CHANNELS = [2, 3]

def run_cycle(target_channel: int, cycle_no: int) -> None:
    print(f"\n[DEMO] === Cycle {cycle_no}: pretending classification -> channel {target_channel} ===")

    # a) Ensure we start from home for consistency on camera
    print("[DEMO] Homing stepper…")
    home_stepper()
    time.sleep(3)

    # b) Slide to target bin channel
    print(f"[DEMO] Moving to channel {target_channel}…")
    move_to_channel(target_channel)
    time.sleep(1)

    # c) Dump: open then close trapdoor
    print("[DEMO] Opening trapdoor…")
    open_trapdoor()
    time.sleep(3)
    print("[DEMO] Closing trapdoor…")
    close_trapdoor()
    time.sleep(1)

    # d) Return home for a clean finish to the shot
    print("[DEMO] Returning home…")
    home_stepper()


def main() -> None:
    print("[DEMO] Starting 2-cycle demo (channels: " + ", ".join(map(str, CHANNELS)) + ")")

    # Initialize hardware
    init_servo()
    close_trapdoor()  # start in a known-safe state
    init_stepper()

    try:
        for i, ch in enumerate(CHANNELS, start=1):
            run_cycle(ch, i)
            if i < len(CHANNELS):
                print("[DEMO] Short pause before next cycle…")
                time.sleep(1.5)
        print("\n[DEMO] All cycles complete. Demo finished.")
    except KeyboardInterrupt:
        print("\n[DEMO] Interrupted by user.")
    finally:
        # Always leave things tidy
        try:
            close_trapdoor()
        except Exception:
            pass
        cleanup_servo()
        cleanup_all()
        print("[DEMO] Cleaned up and exiting.")


if __name__ == "__main__":
    main()
