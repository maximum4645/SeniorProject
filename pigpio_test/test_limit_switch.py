#!/usr/bin/env python3
import pigpio, time

LIMIT_SWITCH_PIN_LEFT  = 17
LIMIT_SWITCH_PIN_RIGHT = 27
DEBOUNCE_US = 5000  # 5 ms, tune 2000–10000 if needed

def setup_gpio(pi):
    for pin in (LIMIT_SWITCH_PIN_LEFT, LIMIT_SWITCH_PIN_RIGHT):
        pi.set_mode(pin, pigpio.INPUT)
        pi.set_pull_up_down(pin, pigpio.PUD_UP)
        pi.set_glitch_filter(pin, DEBOUNCE_US)

def which_pin(gpio):
    return "Left" if gpio == LIMIT_SWITCH_PIN_LEFT else "Right"

def switch_callback(gpio, level, tick):
    if level == pigpio.TIMEOUT: return
    side = "Left" if gpio == LIMIT_SWITCH_PIN_LEFT else "Right"
    if level == 0:
        print(f"{side}: Activated")
    elif level == 1:
        print(f"{side}: Not activated")

def main():
    pi = pigpio.pi()
    if not pi.connected:
        print("Failed to connect to pigpio daemon. Is it running? (sudo pigpiod)")
        return

    setup_gpio(pi)
    print(f"Starting limit switch test (interrupt-driven). Monitoring pins {LIMIT_SWITCH_PIN_LEFT} (left) and {LIMIT_SWITCH_PIN_RIGHT} (right).")
    print("Press the switches; Ctrl+C to exit.")

    cb_left  = pi.callback(LIMIT_SWITCH_PIN_LEFT,  pigpio.EITHER_EDGE, switch_callback)
    cb_right = pi.callback(LIMIT_SWITCH_PIN_RIGHT, pigpio.EITHER_EDGE, switch_callback)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        cb_left.cancel()
        cb_right.cancel()
        pi.stop()

if __name__ == '__main__':
    main()
