#!/usr/bin/env python3
"""
test_stepper_control.py

This script tests the stepper motor functionality on a Raspberry Pi Zero 2 W
using a DRV8825 driver. It will:
  1. Move the motor forward a specified number of steps.
  2. Move the motor backward the same number of steps.
  3. Perform a homing routine until any limit switch is pressed.
"""

import time
import pigpio

class StepperControl:
    def __init__(self, step_pin, dir_pin, enable_pin=None,
                 limit_switch_pin_left=None, limit_switch_pin_right=None):
        self.step_pin = step_pin
        self.dir_pin = dir_pin
        self.enable_pin = enable_pin
        self.limit_switch_pin_left = limit_switch_pin_left
        self.limit_switch_pin_right = limit_switch_pin_right

        self._switch_pins = []

        self.pi = pigpio.pi()
        if not self.pi.connected:
            raise RuntimeError("pigpio daemon not running. Start it with: sudo pigpio")

        # Setup pins
        self.pi.set_mode(self.step_pin, pigpio.OUTPUT)
        self.pi.set_mode(self.dir_pin, pigpio.OUTPUT)

        # Optional enable pin (active-low)
        if self.enable_pin is not None:
            self.pi.set_mode(self.enable_pin, pigpio.OUTPUT)
            self.pi.write(self.enable_pin, 0)  # LOW = driver enabled

        # Optional left (homing) and right (safety) switches, pull-ups enabled
        if self.limit_switch_pin_left is not None:
            self.pi.set_mode(self.limit_switch_pin_left, pigpio.INPUT)
            self.pi.set_pull_up_down(self.limit_switch_pin_left, pigpio.PUD_UP)
            self._switch_pins.append(self.limit_switch_pin_left)
        if self.limit_switch_pin_right is not None:
            self.pi.set_mode(self.limit_switch_pin_right, pigpio.INPUT)
            self.pi.set_pull_up_down(self.limit_switch_pin_right, pigpio.PUD_UP)
            self._switch_pins.append(self.limit_switch_pin_right)

        print(f"[INIT] STEP={self.step_pin}, DIR={self.dir_pin}, "
              f"EN={'None (GND)' if self.enable_pin is None else self.enable_pin}, "
              f"LIMIT_LEFT={'None' if self.limit_switch_pin_left is None else self.limit_switch_pin_left}, "
              f"LIMIT_RIGHT={'None' if self.limit_switch_pin_right is None else self.limit_switch_pin_right}")

    def move_steps(self, steps, step_delay=0.002):
        """
        Move the motor by 'steps' pulses.
        Positive → forward (DIR LOW).
        Negative → backward (DIR HIGH).
        Stops if any limit switch is triggered.
        """
        # Set direction
        if steps >= 0:
            self.pi.write(self.dir_pin, 0)  # LOW
            direction = "forward"
        else:
            self.pi.write(self.dir_pin, 1)  # HIGH
            direction = "backward"

        count = abs(steps)
        print(f"[MOVE] {direction} {count} steps @ {1/step_delay:.0f} Hz")

        for _ in range(count):
            # Safety: abort if the switch is pressed
            if direction == "forward":
                if self.limit_switch_pin_right is not None and self.pi.read(self.limit_switch_pin_right) == 0:
                    print("[SAFETY] Right switch triggered → stopping forward motion.")
                    break
            else:
                if self.limit_switch_pin_left is not None and self.pi.read(self.limit_switch_pin_left) == 0:
                    print("[SAFETY] Left switch triggered → stopping backward motion.")
                    break

            self.pi.write(self.step_pin, 1)
            time.sleep(step_delay)
            self.pi.write(self.step_pin, 0)
            time.sleep(step_delay)

    def home(self, step_delay=0.005):
        """
        Home the motor: step backward until any limit switch closes.
        Assumes switches are wired NO→GND when triggered.
        """
        print("[HOME] Starting homing (DIR→HIGH/backward)")
        self.pi.write(self.dir_pin, 1)  # HIGH

        while True:
            if any(self.pi.read(pin) == 0 for pin in self._switch_pins):
                break

            self.pi.write(self.step_pin, 1)
            time.sleep(step_delay)
            self.pi.write(self.step_pin, 0)
            time.sleep(step_delay)

        print("[HOME] Limit switch triggered; homing complete.")

    def cleanup(self):
        """Release all GPIO resources."""
        print("[CLEANUP] Releasing GPIO")
        # Optionally disable the driver if enable pin is used (set HIGH)
        if self.enable_pin is not None:
            self.pi.write(self.enable_pin, 1)
        self.pi.stop()


def main():
    try:
        # BCM pin assignments
        STEP_PIN = 6    # GPIO6  (pin 31)
        DIR_PIN = 5     # GPIO5  (pin 29)
        ENABLE_PIN = None  # tied to GND
        LIMIT_SWITCH_PIN_LEFT = 17
        LIMIT_SWITCH_PIN_RIGHT = 27

        # Initialize controller with left & right switches
        stepper = StepperControl(
            step_pin=STEP_PIN,
            dir_pin=DIR_PIN,
            enable_pin=ENABLE_PIN,
            limit_switch_pin_left=LIMIT_SWITCH_PIN_LEFT,
            limit_switch_pin_right=LIMIT_SWITCH_PIN_RIGHT
        )

        # Run tests
        print("\n--- TEST: Move Forward ---")
        stepper.move_steps(400)
        time.sleep(1)

        print("\n--- TEST: Move Backward ---")
        stepper.move_steps(-400)
        time.sleep(1)

        print("\n--- TEST: Homing ---")
        stepper.home()

    except KeyboardInterrupt:
        print("\n[INTERRUPT] User aborted test.")
    except Exception as e:
        print(f"\n[ERROR] {e}")
    finally:
        if 'stepper' in locals():
            stepper.cleanup()
        print("[DONE] Stepper motor test complete.")


if __name__ == "__main__":
    main()
