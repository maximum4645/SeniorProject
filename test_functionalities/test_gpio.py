import RPi.GPIO as GPIO
import time

LED_PIN = 7  # Using BCM numbering for GPIO7

GPIO.setmode(GPIO.BOARD)
GPIO.setup(LED_PIN, GPIO.OUT)

try:
    while True:
        GPIO.output(LED_PIN, GPIO.HIGH)  # Turn LED on
        time.sleep(1)
        GPIO.output(LED_PIN, GPIO.LOW)   # Turn LED off
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()

