# control/stepper_control.py
"""
Wrapper for stepper motor control (DRV8825 + NEMA17) based on test_stepper_control.py.
Provides initialization, homing, movement to waste channels, and cleanup functions.
"""
import time
import RPi.GPIO as GPIO
import config

class StepperControl:
    def __init__(self, step_pin, dir_pin, enable_pin=None, limit_switch_pin=None):
        self.step_pin = step_pin
        self.dir_pin = dir_pin
        self.enable_pin = enable_pin
        self.limit_switch_pin = limit_switch_pin

        # Use BCM numbering
        GPIO.setmode(GPIO.BCM)

        # Motor driver pins
        GPIO.setup(self.step_pin, GPIO.OUT)
        GPIO.setup(self.dir_pin, GPIO.OUT)

        # Optional enable pin (active-low = enabled when LOW)
        if self.enable_pin is not None:
            GPIO.setup(self.enable_pin, GPIO.OUT)
            GPIO.output(self.enable_pin, GPIO.LOW)

        # Optional limit switch (pull-up, active-low)
        if self.limit_switch_pin is not None:
            GPIO.setup(self.limit_switch_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        print(f"[INIT] STEP={self.step_pin}, DIR={self.dir_pin}, "
              f"EN={self.enable_pin if self.enable_pin is not None else 'None (GND)'}, "
              f"LIMIT={self.limit_switch_pin if self.limit_switch_pin is not None else 'None'}")

    def move_steps(self, steps, step_delay=0.002):
        # Determine direction
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
        if self.limit_switch_pin is None:
            print("[HOME] No limit switch configured.")
            return

        print("[HOME] Starting homing (DIR→LOW/backward)")
        GPIO.output(self.dir_pin, GPIO.LOW)
        # Step until switch closes (reads LOW)
        while GPIO.input(self.limit_switch_pin) == GPIO.HIGH:
            GPIO.output(self.step_pin, GPIO.HIGH)
            time.sleep(step_delay)
            GPIO.output(self.step_pin, GPIO.LOW)
            time.sleep(step_delay)

        print("[HOME] Limit switch triggered; homing complete.")

    def cleanup(self):
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
        limit_switch_pin=config.LIMIT_SWITCH_PIN
    )
    return _stepper


def home_stepper():
    """Perform homing routine via the limit switch."""
    if _stepper is None:
        raise RuntimeError("Stepper not initialized. Call init_stepper() first.")
    _stepper.home()


def move_to_channel(channel):
    """
    Move from home to channel N (1-indexed), spacing=10 cm, GT2 belt & 20T pulley.
    """
    if _stepper is None:
        raise RuntimeError("Call init_stepper() first.")

    # Constants:
    spacing_cm      = 2          # channel spacing
    belt_pitch_mm   = 2           # GT2 belt pitch
    pulley_teeth    = 20          # count your pulley’s teeth!
    travel_per_rev_cm = (pulley_teeth * belt_pitch_mm) / 10  # mm→cm

    # Compute target:
    distance_cm  = spacing_cm * (channel - 1)
    revs_needed  = distance_cm / travel_per_rev_cm
    target_steps = int(round(revs_needed * config.STEPPER_STEPS_PER_REV))

    print(f"[STEP] channel {channel}: {distance_cm} cm → "
          f"{revs_needed:.2f} rev → {target_steps} steps")
    _stepper.move_steps(target_steps)



def cleanup_all():
    """Cleanup GPIO and release the stepper controller."""
    if _stepper is not None:
        _stepper.cleanup()
    # Ensure any leftover pins are reset
    GPIO.cleanup()
