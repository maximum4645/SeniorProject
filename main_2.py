#!/usr/bin/env python3
import time
import random
import threading

from config import (
    CLASS_TO_CHANNEL,
)
from sensor_2.ir_breakbeam import (
    init_ir_breakbeam,
    is_beam_broken,
    is_beam_intact,
    attach_callback,
    detach_callback,
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

    # --- interrupt-driven trigger (simple) ---
    trigger_evt = threading.Event()
    def _ir_on_change(level_str, tick):
        if level_str == "broken":
            trigger_evt.set()

    attach_callback(_ir_on_change)

    print("\n[MAIN] Ready. Waiting for object…")
    try:
        while True:
            # Wait for first beam break
            trigger_evt.clear()
            trigger_evt.wait()
            time.sleep(0.02)  # tiny confirm delay
            if not is_beam_broken():
                continue

            # Ignore further edges until the cycle completes
            detach_callback()

            print("[MAIN] Detected (beam broken)! Running full cycle…")

            # a) Grab & classify
            img = capture_image_to_memory()
            cls = classify_image(model, img)
            channel = CLASS_TO_CHANNEL[cls]

            # b) Slide to the right bin
            time.sleep(1)
            move_to_channel(channel)

            # c) Dump it
            open_trapdoor()
            time.sleep(1)
            close_trapdoor()

            # d) Return home using real homing routine
            print("[MAIN] Returning home...")
            move_back(channel)
            home_stepper()

            # e) Wait until beam intact again
            print("[MAIN] Cycle done; waiting clearance…")
            while not is_beam_intact():
                print("[wait] beam still broken…"); time.sleep(0.5)
            print("[MAIN] Waiting for next detection…")

            # Re-arm callback for the next object
            attach_callback(_ir_on_change)

    except KeyboardInterrupt:
        print("\n[MAIN] Stopping…")
    finally:
        detach_callback()
        cleanup_breakbeam()
        cleanup_servo()
        cleanup_all()

if __name__ == "__main__":
    main()

