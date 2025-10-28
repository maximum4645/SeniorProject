#!/usr/bin/env python3
import time
import random

from config import (
    POLLING_INTERVAL,
    CLASS_TO_CHANNEL,
)
from control.servo_control import init_servo, open_trapdoor, close_trapdoor, cleanup_servo
from control_2.stepper_control import init_stepper, home_stepper, move_to_channel, move_back, cleanup_all
from sensor_2.button import init_buttons, wait_for_button, cleanup as cleanup_buttons


# === PATCH PCA9685 servo functions ===
def fake_init_servo():
    print("[fake] init_servo() – PCA9685 not present")

def fake_open_trapdoor():
    print("[fake] open_trapdoor()")

def fake_close_trapdoor():
    print("[fake] close_trapdoor()")

def fake_cleanup_servo():
    print("[fake] cleanup_servo()")

init_servo = fake_init_servo
open_trapdoor = fake_open_trapdoor
close_trapdoor = fake_close_trapdoor
cleanup_servo = fake_cleanup_servo
# =====================================


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
    # Initialize what’s actually available
    init_servo()
    init_camera()
    init_buttons()
    init_stepper()

    print("\n[MAIN] Skipping homing startup (no limit switch available).")

    print("\n[MAIN] Closing trapdoor")
    close_trapdoor()

    model = load_model()
    print("\n[MAIN] Running loop… (waiting for button press)")
    try:
        while True:
            ch = wait_for_button(timeout=None)  # returns 1..4
            channel = ch
            print(f"[MAIN] Requested channel {channel}. Running cycle…")

            # b) Slide to the right bin
            time.sleep(1)
            move_to_channel(channel)

            # c) Dump it
            open_trapdoor()
            time.sleep(1)
            close_trapdoor()

            # d) Return home (skip actual homing)
            print("[MAIN] Returning home (fake, no limit switch)...")
            move_back(channel)

            print("[MAIN] Cycle complete.\n")
            time.sleep(POLLING_INTERVAL)

    except KeyboardInterrupt:
        print("\n[MAIN] Stopping…")
    finally:
        cleanup_servo()
        cleanup_buttons()
        cleanup_all()


if __name__ == "__main__":
    main()
