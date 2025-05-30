#!/usr/bin/env python3
import time
import random

from config import (
    DETECTION_THRESHOLD_CM,
    CLEARANCE_THRESHOLD_CM,
    POLLING_INTERVAL,
    CLASS_TO_CHANNEL,
)
from sensors.ultrasonic_sensor import init_ultrasonic, read_distance, cleanup as cleanup_ultrasonic
from sensors.limit_switch import init_limit_switch, is_limit_switch_activated, cleanup_limit_switch
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
    init_ultrasonic()
    init_limit_switch()
    init_servo()
    init_camera()
    init_stepper()

    print("\n[MAIN] Homing startup…")
    home_stepper()

    model = load_model()
    print("\n[MAIN] Running loop…")
    try:
        while True:
            dist = read_distance()
            print(f"[ultra] {dist:.1f} cm")
            if dist < DETECTION_THRESHOLD_CM:
                print("[MAIN] Detected! Running full cycle…")

                # a) Grab & classify
                img = capture_image_to_memory()
                cls = classify_image(model, img)
                tgt = CLASS_TO_CHANNEL[cls]

                # b) Slide to the right bin
                move_to_channel(tgt)

                # c) Dump it
                open_trapdoor()
                time.sleep(3)
                close_trapdoor()

                # d) Return home using real homing routine
                print("[MAIN] Returning home via stepper…")
                home_stepper()

                # e) Wait until cleared
                print("[MAIN] Cycle done; waiting clearance…")
                while read_distance() < CLEARANCE_THRESHOLD_CM:
                    print(f"[wait] {read_distance():.1f} cm"); time.sleep(POLLING_INTERVAL)
                print("[MAIN] Cleared.")

            time.sleep(POLLING_INTERVAL)

    except KeyboardInterrupt:
        print("\n[MAIN] Stopping…")
    finally:
        cleanup_ultrasonic()
        cleanup_limit_switch()
        cleanup_servo()
        cleanup_all()

if __name__ == "__main__":
    main()
