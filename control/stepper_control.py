#!/usr/bin/env python3
"""
Wrapper for stepper motor control (DRV8825 + NEMA17) based on test_stepper_control.py.
Provides initialization, homing, movement to waste channels, and cleanup functions.
"""
import time
import RPi.GPIO as GPIO
import config

class StepperControl:
    def __init__(self, step_pin, dir_pin,
                 enable_pin=None,
                 limit_switch_pin_left=None,
                 limit_switch_pin_right=None):
        self.step_pin = step_pin
        self.dir_pin = dir_pin
        self.enable_pin = enable_pin
        self.limit_switch_pin_left = limit_switch_pin_left
        self.limit_switch_pin_right = limit_switch_pin_right

        # Collect active limit switch pins
        self._switch_pins = []

        # Use BCM numbering
        GPIO.setmode(GPIO.BCM)

        # Motor driver pins
        GPIO.setup(self.step_pin, GPIO.OUT)
        GPIO.setup(self.dir_pin, GPIO.OUT)

        # Optional enable pin (active-low = enabled when LOW)
        if self.enable_pin is not None:
            GPIO.setup(self.enable_pin, GPIO.OUT)
            GPIO.output(self.enable_pin, GPIO.LOW)

        # Optional left (homing) and right (safety) switches
        if self.limit_switch_pin_left is not None:
            GPIO.setup(self.limit_switch_pin_left,
                       GPIO.IN, pull_up_down=GPIO.PUD_UP)
            self._switch_pins.append(self.limit_switch_pin_left)
        if self.limit_switch_pin_right is not None:
            GPIO.setup(self.limit_switch_pin_right,
                       GPIO.IN, pull_up_down=GPIO.PUD_UP)
            self._switch_pins.append(self.limit_switch_pin_right)

        print(f"[INIT] STEP={self.step_pin}, DIR={self.dir_pin}, "
              f"EN={self.enable_pin if self.enable_pin is not None else 'None (GND)'}, "
              f"SWITCHES={self._switch_pins if self._switch_pins else 'None'}")

    def move_steps(self, steps, step_delay=0.002):
        """
        Move the motor by 'steps' pulses.
        Positive → forward (DIR LOW)
        Negative → backward (DIR HIGH)
        Stops if any limit switch is triggered.
        """
        # Determine direction
        if steps >= 0:
            GPIO.output(self.dir_pin, GPIO.LOW)
            direction = "forward"
        else:
            GPIO.output(self.dir_pin, GPIO.HIGH)
            direction = "backward"

        count = abs(steps)
        print(f"[MOVE] {direction} {count} steps @ {1/step_delay:.0f} Hz")

        for _ in range(count):

            # Safety: abort if the switch is pressed
            if direction == "forward":
                if self.limit_switch_pin_right is not None and GPIO.input(self.limit_switch_pin_right) == GPIO.LOW:
                    print("[SAFETY] Right switch triggered → stopping forward motion.")
                    break
            else:
                if self.limit_switch_pin_left is not None and GPIO.input(self.limit_switch_pin_left) == GPIO.LOW:
                    print("[SAFETY] Left switch triggered → stopping backward motion.")
                    break

            GPIO.output(self.step_pin, GPIO.HIGH)
            time.sleep(step_delay)
            GPIO.output(self.step_pin, GPIO.LOW)
            time.sleep(step_delay)

    def home(self, step_delay=0.005):
        """
        Home the motor: step backward until any limit switch closes.
        Assumes switches are wired NO→GND when triggered.
        """
        print("[HOME] Starting homing (DIR→HIGH/backward)")
        GPIO.output(self.dir_pin, GPIO.HIGH)

        while True:
            if any(GPIO.input(pin) == GPIO.LOW for pin in self._switch_pins):
                break

            GPIO.output(self.step_pin, GPIO.HIGH)
            time.sleep(step_delay)
            GPIO.output(self.step_pin, GPIO.LOW)
            time.sleep(step_delay)

        print("[HOME] Limit switch triggered; homing complete.")

    def cleanup(self):
        """Release all GPIO resources."""
        print("[CLEANUP] Releasing GPIO")
        GPIO.cleanup()

# Module-level controller
_stepper = None


def init_stepper():
    """Initialize the stepper controller."""
    global _stepper
    _stepper = StepperControl(
        step_pin=config.STEPPER_STEP_PIN,
        dir_pin=config.STEPPER_DIR_PIN,
        enable_pin=None,
        limit_switch_pin_left=config.LIMIT_SWITCH_PIN_LEFT,
        limit_switch_pin_right=config.LIMIT_SWITCH_PIN_RIGHT
    )
    return _stepper


def home_stepper():
    """Perform homing routine via the limit switches."""
    if _stepper is None:
        raise RuntimeError("Stepper not initialized. Call init_stepper() first.")
    _stepper.home()


def move_to_channel(channel):
    if _stepper is None:
        raise RuntimeError("Call init_stepper() first.")

    # Compute target:
    distance_cm  = config.CHANNEL_SPACING_CM * (channel - 1)
    revs_needed  = distance_cm / config.TRAVEL_PER_REV_CM
    target_steps = int(round(revs_needed * config.STEPPER_STEPS_PER_REV))

    print(f"[STEP] channel {channel}: {distance_cm} cm")
    _stepper.move_steps(target_steps)


def move_back(channel):
    if _stepper is None:
        raise RuntimeError("Call init_stepper() first.")

    distance_cm = max(0, config.CHANNEL_SPACING_CM * (channel - 1) - 5) # 5 cm for homing (slower)
    revs_needed  = distance_cm / config.TRAVEL_PER_REV_CM
    target_steps = int(round(revs_needed * config.STEPPER_STEPS_PER_REV))

    print(f"[STEP] Back from channel {channel}: {distance_cm} cm")
    _stepper.move_steps(-target_steps)


def cleanup_all():
    """Cleanup GPIO and release the stepper controller."""
    if _stepper is not None:
        _stepper.cleanup()
    # Ensure any leftover pins are reset
    GPIO.cleanup()
