#!/usr/bin/env python3
"""
ir_breakbeam.py  (pigpio)

IR break-beam helper with both polling and optional interrupt usage.

Public API (unchanged for main.py):
    init_ir_breakbeam()
    is_beam_intact() -> bool
    is_beam_broken() -> bool
    cleanup()

Optional:
    attach_callback(fn)   # fn(level: str, tick: int)
    detach_callback()

Requires: sudo pigpiod
"""

from typing import Callable, Optional
import pigpio
from config import BREAKBEAM_PIN

_DEF_GLITCH_US = 0  # set to e.g. 2000 for 2 ms debounce if you see spurious edges

# Module state (avoid annotating with pigpio.callback at import time)
_pi: Optional[pigpio.pi] = None
_cb = None  # type: Optional[object]
_glitch_us: int = _DEF_GLITCH_US


def _ensure_pi() -> pigpio.pi:
    global _pi
    if _pi is None:
        _pi = pigpio.pi()
        if not _pi.connected:
            raise RuntimeError("pigpio daemon not running. Start with: sudo pigpiod")
    return _pi


def init_ir_breakbeam(glitch_us: int = _DEF_GLITCH_US) -> None:
    global _glitch_us
    _glitch_us = int(glitch_us)

    pi = _ensure_pi()
    pi.set_mode(BREAKBEAM_PIN, pigpio.INPUT)
    pi.set_pull_up_down(BREAKBEAM_PIN, pigpio.PUD_UP)  # idle HIGH = beam intact
    pi.set_glitch_filter(BREAKBEAM_PIN, _glitch_us)
    print(f"[IR] Initialized pin {BREAKBEAM_PIN}, glitch={_glitch_us} us")


def is_beam_intact() -> bool:
    pi = _ensure_pi()
    return pi.read(BREAKBEAM_PIN) == 1


def is_beam_broken() -> bool:
    pi = _ensure_pi()
    return pi.read(BREAKBEAM_PIN) == 0


def attach_callback(on_change: Callable[[str, int], None]) -> None:
    global _cb
    pi = _ensure_pi()
    detach_callback()

    def _cb_fn(gpio, level, tick):
        if level == pigpio.TIMEOUT:
            return
        state = "broken" if level == 0 else "intact"
        try:
            on_change(state, tick)
        except Exception as e:
            print(f"[IR] Callback error: {e}")

    _cb = pi.callback(BREAKBEAM_PIN, pigpio.EITHER_EDGE, _cb_fn)
    print("[IR] Callback attached.")


def detach_callback() -> None:
    global _cb
    if _cb is not None:
        try:
            _cb.cancel()
        except Exception:
            pass
        _cb = None


def cleanup() -> None:
    global _pi
    try:
        detach_callback()
    except Exception:
        pass

    if _pi is not None:
        try:
            _pi.set_glitch_filter(BREAKBEAM_PIN, 0)
        except Exception:
            pass
        try:
            _pi.stop()
        except Exception:
            pass
        finally:
            _pi = None

    print("[IR] Cleaned up.")


if __name__ == "__main__":
    import time

    def printer(level_str: str, tick: int):
        print(f"Beam {level_str} (tick={tick})")

    try:
        init_ir_breakbeam(glitch_us=2000)
        print("Initial state:", "intact" if is_beam_intact() else "broken")
        attach_callback(printer)
        print("Monitoring IR break-beam. Press Ctrl+C to exit.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()
