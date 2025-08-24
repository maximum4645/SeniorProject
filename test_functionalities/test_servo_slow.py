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


def slew_to(servo_obj, target_deg, dps=APPARENT_SPEED_DPS, update_hz=UPDATE_HZ, clamp=(0.0, 180.0)):
    """
    Move a positional hobby servo to `target_deg` at approx `dps` degrees/sec.
    Simple linear ramp; blocks until finished.

    Notes:
      - On the very first command, servo_obj.angle may be None. In that case
        we set the target directly (no ramp), then future moves will ramp.
    """
    lo, hi = clamp
    target = float(max(lo, min(hi, target_deg)))

    start = servo_obj.angle
    if start is None:
        servo_obj.angle = target
        return
    start = float(start)

    total = abs(target - start)
    if total < 1e-3 or dps <= 0.0:
        servo_obj.angle = target
        return

    dt = 1.0 / float(update_hz)
    step = dps * dt
    steps = max(1, int(total / step))

    for i in range(1, steps + 1):
        u = i / float(steps)
        current = start + (target - start) * u
        servo_obj.angle = current
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
    SERVO_3_OPEN   = 100

    #    Channel 7: mounted oppositely, so moves from ~180° (closed) to ~90° (open)
    SERVO_7_CLOSED = 0
    SERVO_7_OPEN   = 110

    print(f"Starting slow servo test at ~{APPARENT_SPEED_DPS}°/s. Press Ctrl+C to stop.")

    try:
        while True:
            # Move servos to the "closed" position slowly
            slew_to(servo3, SERVO_3_CLOSED)
            slew_to(servo7, SERVO_7_CLOSED)
            print("Flaps closed")
            time.sleep(1)

            # Move servos to the "open" position slowly
            slew_to(servo3, SERVO_3_OPEN)
            slew_to(servo7, SERVO_7_OPEN)
            print("Flaps open")
            time.sleep(1)

    except KeyboardInterrupt:
        print("Interrupted by user. Stopping servo signals.")
    finally:
        pca.deinit()


if __name__ == "__main__":
    main()
