#!/usr/bin/env python3
"""
test_stepper_control.py  (Abort on limit)

DMA-timed stepper control on Raspberry Pi (pigpio + DRV8825)
- Move N steps via waveform repeat (no time.sleep bit-banging)
- Asynchronous safety stops via callbacks with glitch filters
- On limit hit during move_steps(): RETURN "stopped" and ABORT remaining tests
"""

import time
import pigpio


class StepperControl:
    def __init__(self, step_pin, dir_pin, enable_pin=None,
                 limit_switch_pin_left=None, limit_switch_pin_right=None,
                 glitch_us=2000, monitor_sleep_s=0.001):
        self.step_pin = step_pin
        self.dir_pin = dir_pin
        self.enable_pin = enable_pin
        self.limit_switch_pin_left = limit_switch_pin_left
        self.limit_switch_pin_right = limit_switch_pin_right
        self._glitch_us = glitch_us
        self._monitor_sleep_s = monitor_sleep_s

        self.pi = pigpio.pi()
        if not self.pi.connected:
            raise RuntimeError("pigpio daemon not running. Start with: sudo pigpio")

        # I/O setup
        self.pi.set_mode(self.step_pin, pigpio.OUTPUT)
        self.pi.set_mode(self.dir_pin, pigpio.OUTPUT)
        if self.enable_pin is not None:
            self.pi.set_mode(self.enable_pin, pigpio.OUTPUT)
            self.pi.write(self.enable_pin, 0)  # LOW = driver enabled

        # Switches (pull-up + debounce)
        self._switch_pins = []
        for pin in (self.limit_switch_pin_left, self.limit_switch_pin_right):
            if pin is not None:
                self.pi.set_mode(pin, pigpio.INPUT)
                self.pi.set_pull_up_down(pin, pigpio.PUD_UP)
                if self._glitch_us and self._glitch_us > 0:
                    self.pi.set_glitch_filter(pin, self._glitch_us)
                self._switch_pins.append(pin)

        self._cbs = []
        self._stopped_reason = None
        self._stopped_which = None  # "Left" or "Right"

        print(f"[INIT] STEP={self.step_pin}, DIR={self.dir_pin}, "
              f"EN={'None (GND)' if self.enable_pin is None else self.enable_pin}, "
              f"L={self.limit_switch_pin_left}, R={self.limit_switch_pin_right}")

    # ---------- internals ----------
    def _build_period_wave(self, half_period_s):
        """Create one STEP period: HIGH for half_period, then LOW for half_period."""
        us = max(2, int(round(half_period_s * 1_000_000)))  # DRV8825 needs ≥~1.9 µs high
        self.pi.wave_clear()
        self.pi.wave_add_generic([
            pigpio.pulse(1 << self.step_pin, 0, us),
            pigpio.pulse(0, 1 << self.step_pin, us),
        ])
        wid = self.pi.wave_create()
        if wid < 0:
            raise RuntimeError("Failed to create waveform")
        return wid, us

    def _install_callbacks(self, pins_with_labels):
        """Install FALLING-edge callbacks to stop motion immediately."""
        self._cbs.clear()
        self._stopped_reason = None
        self._stopped_which = None

        def make_cb(label):
            def _cb(gpio, level, tick):
                if level == 0:  # active LOW
                    if self.pi.wave_tx_busy():
                        self.pi.wave_tx_stop()
                    if self._stopped_reason is None:
                        self._stopped_reason = f"[SAFETY] {label} switch triggered → motion stopped."
                        self._stopped_which = label
            return _cb

        for pin, label in pins_with_labels:
            if pin is None:
                continue
            self._cbs.append(self.pi.callback(pin, pigpio.FALLING_EDGE, make_cb(label)))

    def _clear_callbacks(self):
        for cb in self._cbs:
            try:
                cb.cancel()
            except Exception:
                pass
        self._cbs.clear()

    # ---------- public API ----------
    def move_steps(self, steps, step_delay=0.0005):
        """
        Move by |steps| pulses at frequency = 1/(2*step_delay).
        DIR LOW for forward (steps>=0), HIGH for backward (steps<0).
        Returns dict: {"status": "ok"|"stopped", "which": "Left"/"Right"/None}
        """
        if steps == 0:
            return {"status": "ok", "which": None}

        direction = "forward" if steps >= 0 else "backward"
        self.pi.write(self.dir_pin, 0 if steps >= 0 else 1)

        # Safety callback on the relevant boundary for the chosen direction
        stop_pin = self.limit_switch_pin_right if steps >= 0 else self.limit_switch_pin_left
        stop_label = "Right" if steps >= 0 else "Left"
        self._install_callbacks([(stop_pin, stop_label)])

        wid, us = self._build_period_wave(step_delay)
        count = abs(steps)
        freq_exact = 1_000_000.0 / (2.0 * us)  # compute from integer µs actually used
        print(f"[MOVE] {direction} {count} steps @ {freq_exact:.0f} Hz")

        try:
            # Repeat the single-period wave 'count' times
            chain = [255, 0, wid, 255, 1, count & 0xFF, (count >> 8) & 0xFF]
            self.pi.wave_chain(chain)

            # Wait until complete or a callback stops it
            while self.pi.wave_tx_busy():
                time.sleep(self._monitor_sleep_s)
        finally:
            self._clear_callbacks()
            self.pi.wave_delete(wid)

        if self._stopped_reason:
            print(self._stopped_reason)
            return {"status": "stopped", "which": self._stopped_which}
        return {"status": "ok", "which": None}

    def home(self, step_delay=0.005):
        """
        Home by stepping backward continuously until ANY switch triggers.
        Uses wave_send_repeat and async callbacks on both switches.
        """
        print("[HOME] Starting homing (DIR→HIGH/backward)")
        self.pi.write(self.dir_pin, 1)

        # Callbacks on both switches (whichever is wired)
        pins = [("Left", self.limit_switch_pin_left), ("Right", self.limit_switch_pin_right)]
        self._install_callbacks([(pin, label) for label, pin in pins])

        wid, us = self._build_period_wave(step_delay)
        try:
            self.pi.wave_send_repeat(wid)
            while self.pi.wave_tx_busy():
                time.sleep(self._monitor_sleep_s)
        finally:
            self._clear_callbacks()
            self.pi.wave_delete(wid)

        print(self._stopped_reason or "[HOME] Limit switch triggered; homing complete.")

    def cleanup(self):
        print("[CLEANUP] Releasing GPIO")
        try:
            if self.pi.wave_tx_busy():
                self.pi.wave_tx_stop()
        except Exception:
            pass
        if self.enable_pin is not None:
            self.pi.write(self.enable_pin, 1)  # disable driver (active-low)
        for pin in self._switch_pins:
            self.pi.set_glitch_filter(pin, 0)
        self.pi.stop()


def main():
    try:
        # BCM pins
        STEP_PIN = 6
        DIR_PIN = 5
        ENABLE_PIN = None  # tied to GND
        LIMIT_SWITCH_PIN_LEFT = 17
        LIMIT_SWITCH_PIN_RIGHT = 27

        stepper = StepperControl(
            step_pin=STEP_PIN,
            dir_pin=DIR_PIN,
            enable_pin=ENABLE_PIN,
            limit_switch_pin_left=LIMIT_SWITCH_PIN_LEFT,
            limit_switch_pin_right=LIMIT_SWITCH_PIN_RIGHT,
            glitch_us=2000,
            monitor_sleep_s=0.001
        )

        print("\n--- TEST: Move Forward ---")
        res = stepper.move_steps(400, step_delay=0.001)
        if res["status"] == "stopped":
            print("[ABORT] Limit triggered during forward move.")
            return

        print("\n--- TEST: Move Backward ---")
        res = stepper.move_steps(-400, step_delay=0.001)
        if res["status"] == "stopped":
            print("[ABORT] Limit triggered during backward move.")
            return

        print("\n--- TEST: Homing ---")
        stepper.home(step_delay=0.005)

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
