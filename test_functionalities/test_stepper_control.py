#!/usr/bin/env python3
"""
test_stepper_control.py

This script tests the stepper motor functionality on a Raspberry Pi Zero 2 W
using a DRV8825 driver. It will:
  1. Move the motor forward a specified number of steps.
  2. Move the motor backward the same number of steps.
  3. Perform a homing routine using a limit switch.

Wiring (BCM numbering):
  • STEP       → GPIO5   (pin 29)
  • DIR        → GPIO6   (pin 31)
  • LIMIT SW   → GPIO17  (pin 11)
  • ENABLE     → tied directly to GND (always enabled)
  • Common GND → Pi GND and DRV8825 GND tied together

Before running:
  • Verify your wiring and that the motor power supply (VMOT) shares ground with the Pi.
  • Run as root: sudo python3 test_stepper_control.py
"""

import RPi.GPIO as GPIO
import time

class StepperControl:
    def __init__(self, step_pin, dir_pin, enable_pin=None, limit_switch_pin=None):
        self.step_pin = step_pin
        self.dir_pin = dir_pin
        self.enable_pin = enable_pin
        self.limit_switch_pin = limit_switch_pin

        # Use BCM pin numbering
        GPIO.setmode(GPIO.BCM)

        # Motor driver pins
        GPIO.setup(self.step_pin, GPIO.OUT)
        GPIO.setup(self.dir_pin, GPIO.OUT)

        # Optional enable pin (active-low)
        if self.enable_pin is not None:
            GPIO.setup(self.enable_pin, GPIO.OUT)
            GPIO.output(self.enable_pin, GPIO.LOW)  # LOW = driver enabled

        # Optional limit switch (pull-up, active-low)
        if self.limit_switch_pin is not None:
            GPIO.setup(self.limit_switch_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        print(f"[INIT] STEP={self.step_pin}, DIR={self.dir_pin}, "
              f"EN={'None (GND)'}" if self.enable_pin is None else f"EN={self.enable_pin}, "
              f"LIMIT={'None' if self.limit_switch_pin is None else self.limit_switch_pin}")

    def move_steps(self, steps, step_delay=0.002):
        """
        Move the motor by 'steps' pulses.
        Positive → forward (DIR HIGH)
        Negative → backward (DIR LOW)
        """
        # Direction
        if steps >= 0:
            GPIO.output(self.dir_pin, GPIO.HIGH)
            direction = "forward"
        else:
            GPIO.output(self.dir_pin, GPIO.LOW)
            direction = "backward"

        count = abs(steps)
        print(f"[MOVE] {direction} {count} steps @ {1/step_delay:.0f} Hz")
        for _ in range(count):
            GPIO.output(self.step_pin, GPIO.HIGH)
            time.sleep(step_delay)
            GPIO.output(self.step_pin, GPIO.LOW)
            time.sleep(step_delay)

    def home(self, step_delay=0.005):
        """
        Home the motor: step backward until limit switch closes.
        Assumes limit switch is wired NO→GND when triggered.
        """
        if self.limit_switch_pin is None:
            print("[HOME] No limit switch configured.")
            return

        print("[HOME] Starting homing (DIR→LOW/backward)")
        GPIO.output(self.dir_pin, GPIO.LOW)
        # Keep stepping until switch reads LOW
        while GPIO.input(self.limit_switch_pin) == GPIO.HIGH:
            GPIO.output(self.step_pin, GPIO.HIGH)
            time.sleep(step_delay)
            GPIO.output(self.step_pin, GPIO.LOW)
            time.sleep(step_delay)

        print("[HOME] Limit switch triggered; homing complete.")

    def cleanup(self):
        """ Release all GPIO resources """
        print("[CLEANUP] Releasing GPIO")
        GPIO.cleanup()


def test_move_forward(stepper, steps):
    print("\n--- TEST: Move Forward ---")
    stepper.move_steps(steps)

def test_move_backward(stepper, steps):
    print("\n--- TEST: Move Backward ---")
    stepper.move_steps(-steps)

def test_homing(stepper):
    print("\n--- TEST: Homing ---")
    stepper.home()

def main():
    try:
        # BCM pin assignments
        STEP_PIN         = 5    # GPIO5  (pin 29)
        DIR_PIN          = 6    # GPIO6  (pin 31)
        ENABLE_PIN       = None # tied to GND
        LIMIT_SWITCH_PIN = 17   # GPIO17 (pin 11)

        # Initialize controller
        stepper = StepperControl(
            step_pin=STEP_PIN,
            dir_pin=DIR_PIN,
            enable_pin=ENABLE_PIN,
            limit_switch_pin=LIMIT_SWITCH_PIN
        )

        # Run tests
        test_move_forward(stepper, steps=1500)
        time.sleep(1)
        test_move_backward(stepper, steps=1500)
        time.sleep(1)
        test_homing(stepper)

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
