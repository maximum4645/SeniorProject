#!/usr/bin/env python3
import time
import random

from config import (
    POLLING_INTERVAL,
    CLASS_TO_CHANNEL,
)
from sensor_2.ir_breakbeam import (
    init_ir_breakbeam,
    is_beam_broken,
    is_beam_intact,
    cleanup as cleanup_breakbeam,
)
from control.servo_control import init_servo, open_trapdoor, close_trapdoor, cleanup_servo
from control_2.stepper_control import init_stepper, home_stepper, move_to_channel, move_back, cleanup_all

# (Camera + classification still stubbed out)
def init_camera():
    print("[stub] init_camera()"); time.sleep(1)

def load_model():
    print("[stub] load_model()"); time.sleep(1)
    return "model"

def capture_image_to_memory():
    print("[stub] capture_image_to_memory()"); time.sleep(1)
    return None

def classify_image(model, img):
    label = random.choice(list(CLASS_TO_CHANNEL.keys()))
    print(f"[stub] classify_image() -> {label}"); time.sleep(1)
    return label

def main():
    # Initialize real modules
    init_ir_breakbeam()
    init_servo()
    init_camera()
    init_stepper()

    print("\n[MAIN] Homing startup…")
    home_stepper()

    print("\n[MAIN] Closing trapdoor")
    close_trapdoor()

    model = load_model()
    print("\n[MAIN] Running sequence: 2 → 3 → 1")

    try:
        for channel in (2, 3, 1):
            print(f"[MAIN] Requested channel {channel}. Running cycle…")

            # b) Slide to the right bin
            time.sleep(3)
            move_to_channel(channel)

            # c) Dump it
            open_trapdoor()
            time.sleep(1)
            close_trapdoor()

            # d) Return home using real homing routine
            print("[MAIN] Returning home...")
            move_back(channel)
            home_stepper()

            print("[MAIN] Cycle complete.\n")
            time.sleep(POLLING_INTERVAL)

    except KeyboardInterrupt:
        print("\n[MAIN] Stopping…")
    finally:
        cleanup_breakbeam()
        cleanup_servo()
        cleanup_all()

if __name__ == "__main__":
    main()
