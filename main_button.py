#!/usr/bin/env python3
import time
import random
import os

import cv2

from config import (
    POLLING_INTERVAL,
    CLASS_TO_CHANNEL,
    IMAGE_SAVE_DIR,   # NEW: where images are saved
)

from sensors.ir_breakbeam import init_ir_breakbeam, is_beam_broken, is_beam_intact, cleanup as cleanup_breakbeam
from sensors.button import init_buttons, wait_for_button, cleanup as cleanup_buttons
from control.servo_control import init_servo, open_trapdoor, close_trapdoor, cleanup_servo
from control.stepper_control import init_stepper, home_stepper, move_to_channel, move_back, cleanup_all

# NEW: real camera functions
from camera.camera_capture import initialize as camera_initialize, capture_image


# (Classification still stubbed out)
def init_camera():
    print("[MAIN] init_camera() - initializing real camera")
    camera_initialize(mode="still")
    print("[MAIN] Camera initialized.")


def load_model():
    print("[stub] load_model()"); time.sleep(1)
    return "model"


def channel_to_class(channel):
    """
    Map a channel number (1..N) back to a class name using CLASS_TO_CHANNEL.
    Example CLASS_TO_CHANNEL: {"general": 1, "plastic": 2, ...}
    """
    for cls, ch in CLASS_TO_CHANNEL.items():
        if ch == channel:
            return cls
    # Fallback (should not normally happen)
    return str(channel)


def save_labeled_image(img, image_class):
    """
    Save captured image under IMAGE_SAVE_DIR/image_class with
    a timestamped filename, e.g. IMAGE_SAVE_DIR/plastic/plastic_20251208_120001.jpg
    """
    os.makedirs(IMAGE_SAVE_DIR, exist_ok=True)
    save_dir = os.path.join(IMAGE_SAVE_DIR, image_class)
    os.makedirs(save_dir, exist_ok=True)

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"{image_class}_{timestamp}.jpg"
    full_path = os.path.join(save_dir, filename)

    cv2.imwrite(full_path, img)
    print(f"[MAIN] Saved image: {full_path}")
    return full_path


def capture_image_to_memory(image_class):
    """
    Capture an image from the camera, save it with the given class label,
    and keep it in memory (return the image array).
    """
    print(f"[MAIN] capture_image_to_memory() - capturing frame for class '{image_class}'")
    img = capture_image()   # BGR numpy array from camera_capture.py
    save_labeled_image(img, image_class)
    return img


def classify_image(model, img):
    label = random.choice(list(CLASS_TO_CHANNEL.keys()))
    print(f"[stub] classify_image() -> {label}"); time.sleep(1)
    return label


def main():
    # Initialize real modules
    init_ir_breakbeam()
    init_servo()
    init_camera()
    init_buttons()
    init_stepper()

    print("\n[MAIN] Homing startup…")
    home_stepper()

    print("\n[MAIN] Closing trapdoor")
    close_trapdoor()

    model = load_model()
    print("\n[MAIN] Running loop… (polling break-beam)")
    try:
        while True:
            ch = wait_for_button(timeout=None)  # returns 1..4
            channel = ch
            image_class = channel_to_class(channel)

            print(f"[MAIN] Requested channel {channel} (class '{image_class}'). Running cycle…")

            # Capture + save image for this class
            img = capture_image_to_memory(image_class)
            # (Later you can classify or do something with `img` + `model` here)

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

            print("[MAIN] Cycle complete.\n")

            time.sleep(POLLING_INTERVAL)

    except KeyboardInterrupt:
        print("\n[MAIN] Stopping…")
    finally:
        cleanup_breakbeam()
        cleanup_servo()
        cleanup_buttons()
        cleanup_all()


if __name__ == "__main__":
    main()
