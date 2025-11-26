#!/usr/bin/env python3
"""
limit_switch.py  (pigpio)

Interrupt-friendly limit switch helper using pigpio:
- Pull-ups + glitch filter (debounce)
- Polling helpers
- Optional edge callbacks

Requires: sudo pigpiod
"""

from typing import Callable, Optional
import pigpio
from config import LIMIT_SWITCH_PIN_LEFT, LIMIT_SWITCH_PIN_RIGHT

_DEF_DEBOUNCE_US = 5000  # 5 ms typical for mechanical switches

_pi: Optional[pigpio.pi] = None
_glitch_us: int = _DEF_DEBOUNCE_US
_cb_left = None   # type: Optional[object]
_cb_right = None  # type: Optional[object]


def _ensure_pi() -> pigpio.pi:
    global _pi
    if _pi is None:
        _pi = pigpio.pi()
        if not _pi.connected:
            raise RuntimeError("Failed to connect to pigpio daemon. Start with: sudo pigpiod")
    return _pi


def init_limit_switch(debounce_us: int = _DEF_DEBOUNCE_US) -> None:
    global _glitch_us
    _glitch_us = int(debounce_us)

    pi = _ensure_pi()

    for pin in (LIMIT_SWITCH_PIN_LEFT, LIMIT_SWITCH_PIN_RIGHT):
        if pin is None:
            continue
        pi.set_mode(pin, pigpio.INPUT)
        pi.set_pull_up_down(pin, pigpio.PUD_UP)  # active-LOW on press
        pi.set_glitch_filter(pin, _glitch_us)

    print(f"[LIMIT] Initialized. Left={LIMIT_SWITCH_PIN_LEFT}, Right={LIMIT_SWITCH_PIN_RIGHT}, debounce={_glitch_us} us")


def is_left_switch_activated() -> bool:
    if LIMIT_SWITCH_PIN_LEFT is None:
        return False
    pi = _ensure_pi()
    return pi.read(LIMIT_SWITCH_PIN_LEFT) == 0


def is_right_switch_activated() -> bool:
    if LIMIT_SWITCH_PIN_RIGHT is None:
        return False
    pi = _ensure_pi()
    return pi.read(LIMIT_SWITCH_PIN_RIGHT) == 0


def attach_callbacks(on_change: Callable[[str, bool, int], None]) -> None:
    global _cb_left, _cb_right
    pi = _ensure_pi()

    def _wrap(side_label: str):
        def _cb(gpio, level, tick):
            if level == pigpio.TIMEOUT:
                return
            activated = (level == 0)
            try:
                on_change(side_label, activated, tick)
            except Exception as e:
                print(f"[LIMIT] Callback error ({side_label}): {e}")
        return _cb

    detach_callbacks()

    if LIMIT_SWITCH_PIN_LEFT is not None:
        _cb_left = pi.callback(LIMIT_SWITCH_PIN_LEFT, pigpio.EITHER_EDGE, _wrap("Left"))
    if LIMIT_SWITCH_PIN_RIGHT is not None:
        _cb_right = pi.callback(LIMIT_SWITCH_PIN_RIGHT, pigpio.EITHER_EDGE, _wrap("Right"))

    print("[LIMIT] Callbacks attached.")


def detach_callbacks() -> None:
    global _cb_left, _cb_right
    for cb in (_cb_left, _cb_right):
        try:
            if cb is not None:
                cb.cancel()
        except Exception:
            pass
    _cb_left = None
    _cb_right = None


def cleanup_limit_switch() -> None:
    global _pi
    try:
        detach_callbacks()
    except Exception:
        pass

    if _pi is not None:
        for pin in (LIMIT_SWITCH_PIN_LEFT, LIMIT_SWITCH_PIN_RIGHT):
            try:
                if pin is not None:
                    _pi.set_glitch_filter(pin, 0)
            except Exception:
                pass

        try:
            _pi.stop()
        except Exception:
            pass
        finally:
            _pi = None

    print("[LIMIT] Cleaned up.")


if __name__ == "__main__":
    import time

    def printer(side: str, activated: bool, tick: int):
        state = "Activated" if activated else "Not activated"
        print(f"{side}: {state} (tick={tick})")

    try:
        init_limit_switch()
        attach_callbacks(printer)
        print("Monitoring limit switches. Press Ctrl+C to exit.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        cleanup_limit_switch()
