#!/usr/bin/env python3
import time
import random

from config import (
    POLLING_INTERVAL,
    CLASS_TO_CHANNEL,
)
from sensors.ir_breakbeam import (
    init_ir_breakbeam,
    is_beam_broken,
    is_beam_intact,
    cleanup as cleanup_breakbeam,
)
from control.servo_control import init_servo, open_trapdoor, close_trapdoor, cleanup_servo
from control.stepper_control import init_stepper, home_stepper, move_to_channel, cleanup_all

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
    print("\n[MAIN] Running loop… (polling break-beam)")
    try:
        while True:
            if is_beam_broken():
                print("[MAIN] Detected (beam broken)! Running full cycle…")

                # a) Grab & classify
                img = capture_image_to_memory()
                cls = classify_image(model, img)
                tgt = CLASS_TO_CHANNEL[cls]

                # b) Slide to the right bin
                home_stepper()
                time.sleep(1)
                move_to_channel(tgt)

                # c) Dump it
                open_trapdoor()
                time.sleep(1)
                close_trapdoor()

                # d) Return home using real homing routine
                print("[MAIN] Returning home via stepper…")
                home_stepper()

                # e) Wait until beam intact again
                print("[MAIN] Cycle done; waiting clearance…")
                while not is_beam_intact():
                    print("[wait] beam still broken…"); time.sleep(POLLING_INTERVAL)
                print("[MAIN] Cleared.")

            time.sleep(POLLING_INTERVAL)

    except KeyboardInterrupt:
        print("\n[MAIN] Stopping…")
    finally:
        cleanup_breakbeam()
        cleanup_servo()
        cleanup_all()

if __name__ == "__main__":
    main()
