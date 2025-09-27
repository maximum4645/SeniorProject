#!/usr/bin/env python3
"""
Wrapper for stepper motor control (pigpio + DRV8825 + NEMA17).

- DMA-timed STEP pulses via pigpio waveforms (no time.sleep bit-banging)
- Asynchronous safety stops via FALLING-edge callbacks with glitch filters
- Public API kept identical to previous wrapper so main.py doesn't change:
    init_stepper(), home_stepper(), move_to_channel(channel), move_back(channel), cleanup_all()
"""

import time
import pigpio
import config_2 as config   # <-- changed to use config_2

# ------------ pigpio-based controller class ------------
class _StepperControlPigpio:
    def __init__(self,
                 step_pin,
                 dir_pin,
                 enable_pin=None,
                 limit_switch_pin_left=None,
                 limit_switch_pin_right=None,
                 glitch_us=2000,
                 monitor_sleep_s=0.001,
                 dir_polarity=+1):
        self.step_pin = step_pin
        self.dir_pin = dir_pin
        self.enable_pin = enable_pin
        self.limit_switch_pin_left = limit_switch_pin_left
        self.limit_switch_pin_right = limit_switch_pin_right
        self._glitch_us = glitch_us
        self._monitor_sleep_s = monitor_sleep_s
        self._dir_polarity = 1 if dir_polarity >= 0 else -1

        self.pi = pigpio.pi()
        if not self.pi.connected:
            raise RuntimeError("pigpio daemon not running. Start with: sudo pigpiod")

        # IO setup
        self.pi.set_mode(self.step_pin, pigpio.OUTPUT)
        self.pi.set_mode(self.dir_pin, pigpio.OUTPUT)
        if self.enable_pin is not None:
            self.pi.set_mode(self.enable_pin, pigpio.OUTPUT)
            self.pi.write(self.enable_pin, 0)  # LOW = driver enabled

        # Limit switches (pull-up, optional glitch filter)
        self._switch_pins = []
        for pin in (self.limit_switch_pin_left, self.limit_switch_pin_right):
            if pin is None:
                continue
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
              f"L={self.limit_switch_pin_left}, R={self.limit_switch_pin_right}, "
              f"glitch={self._glitch_us} us")

    # ---- internals ----
    def _set_dir(self, forward: bool):
        """
        forward=True means 'to the right' mechanically (channel numbers increasing).
        With _dir_polarity = +1, forward -> DIR LOW; backward -> DIR HIGH (your previous convention).
        If polarity is flipped, this mapping inverts.
        """
        logical = 0 if forward else 1
        if self._dir_polarity < 0:
            logical ^= 1
        self.pi.write(self.dir_pin, logical)

    def _build_period_wave(self, half_period_s):
        """
        Create one STEP period: HIGH half, LOW half. Returns (wid, us).
        DRV8825 requires ~1.9 µs min HIGH; enforce >=2 µs.
        """
        us = max(2, int(round(half_period_s * 1_000_000)))
        self.pi.wave_clear()
        self.pi.wave_add_generic([
            pigpio.pulse(1 << self.step_pin, 0, us),
            pigpio.pulse(0, 1 << self.step_pin, us),
        ])
        wid = self.pi.wave_create()
        if wid < 0:
            raise RuntimeError("Failed to create waveform")
        return wid, us

    def _install_callbacks(self):
        """Monitor both limits; stop wave immediately on FALLING (active-LOW)."""
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

        if self.limit_switch_pin_left is not None:
            self._cbs.append(self.pi.callback(self.limit_switch_pin_left,
                                              pigpio.FALLING_EDGE, make_cb("Left")))
        if self.limit_switch_pin_right is not None:
            self._cbs.append(self.pi.callback(self.limit_switch_pin_right,
                                              pigpio.FALLING_EDGE, make_cb("Right")))

    def _clear_callbacks(self):
        for cb in self._cbs:
            try:
                cb.cancel()
            except Exception:
                pass
        self._cbs.clear()

    # ---- public controls ----
    def move_steps(self, steps: int, step_delay: float):
        """
        Move by |steps| pulses at frequency ≈ 1/(2*step_delay).
        Returns dict: {"status": "ok"|"stopped", "which": "Left"/"Right"/None}
        """
        if steps == 0:
            return {"status": "ok", "which": None}

        forward = steps >= 0
        self._set_dir(forward)

        self._install_callbacks()

        wid, us = self._build_period_wave(step_delay)
        count = abs(steps)
        freq_exact = 1_000_000.0 / (2.0 * us)
        print(f"[MOVE] {'forward' if forward else 'backward'} {count} steps @ {freq_exact:.0f} Hz")

        try:
            # chain: transmit wave 'count' times
            chain = [255, 0, wid, 255, 1, count & 0xFF, (count >> 8) & 0xFF]
            self.pi.wave_chain(chain)
            while self.pi.wave_tx_busy():
                time.sleep(self._monitor_sleep_s)
        finally:
            # Force-stop any active transmission even on Ctrl+C
            try:
                if self.pi.wave_tx_busy():
                    self.pi.wave_tx_stop()
            except Exception:
                pass
            self._clear_callbacks()
            try:
                self.pi.wave_delete(wid)
            except Exception:
                pass

        if self._stopped_reason:
            print(self._stopped_reason)
            return {"status": "stopped", "which": self._stopped_which}
        return {"status": "ok", "which": None}

    def home(self, step_delay: float):
        """
        Home by stepping backward (toward the left) continuously until ANY switch triggers.
        Uses wave_send_repeat and async callbacks on both switches.
        """
        print("[HOME] Starting homing (DIR→HIGH/backward by convention)")
        self._set_dir(forward=False)

        self._install_callbacks()
        wid, us = self._build_period_wave(step_delay)
        try:
            self.pi.wave_send_repeat(wid)
            while self.pi.wave_tx_busy():
                time.sleep(self._monitor_sleep_s)
        finally:
            # Stop repeat wave if still running (e.g., Ctrl+C before a switch triggers)
            try:
                if self.pi.wave_tx_busy():
                    self.pi.wave_tx_stop()
            except Exception:
                pass
            self._clear_callbacks()
            try:
                self.pi.wave_delete(wid)
            except Exception:
                pass

        print(self._stopped_reason or "[HOME] Limit switch triggered; homing complete.")

    def cleanup(self):
        print("[CLEANUP] Releasing GPIO")
        try:
            if self.pi.wave_tx_busy():
                self.pi.wave_tx_stop()
        except Exception:
            pass
        if self.enable_pin is not None:
            # disable driver (active-low enable)
            self.pi.write(self.enable_pin, 1)
        for pin in self._switch_pins:
            self.pi.set_glitch_filter(pin, 0)
        self.pi.stop()


# ------------ module-level singleton & API (kept stable for main.py) ------------
_stepper = None

def _effective_steps_per_rev():
    micro = getattr(config, "MICROSTEPPING", 1)
    base = getattr(config, "STEPPER_STEPS_PER_REV", 200)
    try:
        return int(base) * int(micro)
    except Exception:
        return 200  # safe fallback

def _steps_for_distance_cm(distance_cm: float):
    """
    Convert linear travel (cm) to step count, using config TRAVEL_PER_REV_CM.
    """
    travel_per_rev_cm = getattr(config, "TRAVEL_PER_REV_CM", None)
    if not travel_per_rev_cm or travel_per_rev_cm <= 0:
        # Fallback compute if user didn't precompute in config:
        pitch_mm = getattr(config, "BELT_PITCH_MM", 2)
        teeth    = getattr(config, "PULLEY_TEETH", 20)
        travel_per_rev_cm = (teeth * pitch_mm) / 10.0  # mm -> cm
    steps_per_rev = _effective_steps_per_rev()
    steps = distance_cm / float(travel_per_rev_cm) * steps_per_rev
    return int(round(steps))

def init_stepper():
    """Initialize the stepper controller (pigpio)."""
    global _stepper
    if _stepper is not None:
        return _stepper

    step_pin = getattr(config, "STEPPER_STEP_PIN", 6)
    dir_pin  = getattr(config, "STEPPER_DIR_PIN", 5)
    en_pin   = getattr(config, "STEPPER_ENABLE_PIN", None)
    l_pin    = getattr(config, "LIMIT_SWITCH_PIN_LEFT", None)
    r_pin    = getattr(config, "LIMIT_SWITCH_PIN_RIGHT", None)

    glitch_us = getattr(config, "PIGPIO_GLITCH_US", 2000)
    monitor_s = getattr(config, "PIGPIO_MONITOR_SLEEP_S", 0.001)
    dir_pol   = getattr(config, "STEPPER_DIR_POLARITY", +1)

    _stepper = _StepperControlPigpio(
        step_pin=step_pin,
        dir_pin=dir_pin,
        enable_pin=en_pin,
        limit_switch_pin_left=l_pin,
        limit_switch_pin_right=r_pin,
        glitch_us=glitch_us,
        monitor_sleep_s=monitor_s,
        dir_polarity=dir_pol,
    )
    return _stepper

def home_stepper():
    """Perform homing routine using async limit callbacks."""
    if _stepper is None:
        raise RuntimeError("Stepper not initialized. Call init_stepper() first.")
    step_delay = getattr(config, "HOME_STEP_DELAY_S", 0.001)
    _stepper.home(step_delay=step_delay)

def move_to_channel(channel: int):
    """
    Move from home (channel 1 origin) to the requested channel position to the right.
    """
    if _stepper is None:
        raise RuntimeError("Call init_stepper() first.")

    spacing = getattr(config, "CHANNEL_SPACING_CM", 20)
    distance_cm = spacing * max(0, int(channel) - 1)
    steps = _steps_for_distance_cm(distance_cm)
    step_delay = getattr(config, "STEPPER_STEP_DELAY_S", 0.0008)

    # Frequency info (approx) for logging
    half_us = max(2, int(round(step_delay * 1_000_000)))
    freq_hz = 1_000_000.0 / (2.0 * half_us)

    print(f"[STEP] channel {channel}: {distance_cm:.2f} cm → {steps} steps @ ~{freq_hz:.0f} Hz")
    return _stepper.move_steps(steps, step_delay=step_delay)

def move_back(channel: int):
    """
    Move left toward home by (channel position - 5 cm), then caller should call home_stepper().
    """
    if _stepper is None:
        raise RuntimeError("Call init_stepper() first.")

    spacing = getattr(config, "CHANNEL_SPACING_CM", 20)
    distance_cm = max(0.0, spacing * max(0, int(channel) - 1) - 5.0)  # leave ~5 cm for clean homing
    steps = _steps_for_distance_cm(distance_cm)
    step_delay = getattr(config, "STEPPER_STEP_DELAY_S", 0.0008)

    half_us = max(2, int(round(step_delay * 1_000_000)))
    freq_hz = 1_000_000.0 / (2.0 * half_us)

    print(f"[STEP] back from channel {channel}: {distance_cm:.2f} cm → {steps} steps @ ~{freq_hz:.0f} Hz")
    return _stepper.move_steps(-steps, step_delay=step_delay)

def cleanup_all():
    """Cleanup pigpio resources and disable driver if applicable."""
    global _stepper
    if _stepper is not None:
        try:
            _stepper.cleanup()
        finally:
            _stepper = None
