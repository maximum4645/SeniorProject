#!/usr/bin/env python3
"""
test_servo_slow.py

This script controls two SG90-like servos on channels 3 and 7 of a PCA9685 board.
It uses the adafruit_motor.servo module to automatically convert angles into the
correct PWM signal. The servo on channel 3 moves between 0° (closed) and 90° (open),
while the servo on channel 7 (mounted oppositely) moves between 180° (closed) and 90° (open).

Pulse width range is set to 500–2400 µs, which corresponds to typical SG90 specs.

Change APPARENT_SPEED_DPS to make the motion slower/faster. The first move to a position
may "snap" if the library doesn't know the current angle; subsequent moves will ramp.
"""

import time
import board
import busio
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo

# ===== User-tunable speed (degrees per second) =====
APPARENT_SPEED_DPS = 45.0   # Lower = slower, e.g., 30.0 for very slow

# ===== Update rate for ramping (matches 50 Hz servo refresh well) =====
UPDATE_HZ = 50.0            # 50 updates/sec -> ~20 ms per step


def slew_to_together(pairs, dps=APPARENT_SPEED_DPS, update_hz=UPDATE_HZ, clamp=(0.0, 180.0)):
    """
    Move multiple servos simultaneously to their targets at approx `dps`.
    `pairs` is a list of (servo_obj, target_deg).
    """
    lo, hi = clamp
    dt = 1.0 / float(update_hz)

    plan = []
    max_steps = 0

    for s, tgt in pairs:
        tgt = float(max(lo, min(hi, float(tgt))))
        start = s.angle

        if start is None:
            # First command unknown -> jump to target once (no ramp)
            s.angle = tgt
            steps = 0
            start = tgt
        else:
            start = float(start)
            total = abs(tgt - start)
            if total < 1e-3 or dps <= 0.0:
                s.angle = tgt
                steps = 0
            else:
                step = dps * dt
                steps = max(1, int(total / step))

        plan.append((s, start, tgt, steps))
        if steps > max_steps:
            max_steps = steps

    for i in range(1, max_steps + 1):
        for s, start, tgt, steps in plan:
            if steps == 0:
                continue
            u = min(1.0, i / float(steps))
            current = start + (tgt - start) * u
            s.angle = current
        time.sleep(dt)


def main():
    # 1) Initialize the I2C bus and PCA9685
    i2c = board.I2C()  # Requires I2C to be enabled on the Pi
    pca = PCA9685(i2c)
    pca.frequency = 50  # 50 Hz is standard for SG90 servos

    # 2) Create servo objects on channels 3 and 7
    #    Using 500 µs for min_pulse and 2400 µs for max_pulse (per SG90 datasheet)
    servo3 = servo.Servo(pca.channels[3], min_pulse=500, max_pulse=2400)
    servo7 = servo.Servo(pca.channels[7], min_pulse=500, max_pulse=2400)

    # 3) Define the positions for each servo (tune these if your endpoints buzz or bind)
    #    Channel 3: moves from ~0° (closed) to ~90° (open)
    SERVO_3_CLOSED = 0
    SERVO_3_OPEN   = 90

    #    Channel 7: mounted oppositely, so moves from ~180° (closed) to ~90° (open)
    SERVO_7_CLOSED = 0
    SERVO_7_OPEN   = 90

    print(f"Starting slow servo test at ~{APPARENT_SPEED_DPS}°/s. Press Ctrl+C to stop.")

    try:
        while True:
            # Move servos to the "closed" position slowly (simultaneous)
            slew_to_together([
                (servo3, SERVO_3_CLOSED),
                (servo7, SERVO_7_CLOSED),
            ])
            print("Flaps closed")
            time.sleep(1)

            # Move servos to the "open" position slowly (simultaneous)
            slew_to_together([
                (servo3, SERVO_3_OPEN),
                (servo7, SERVO_7_OPEN),
            ])
            print("Flaps open")
            time.sleep(1)

    except KeyboardInterrupt:
        print("Interrupted by user. Stopping servo signals.")
    finally:
        pca.deinit()


if __name__ == "__main__":
    main()
