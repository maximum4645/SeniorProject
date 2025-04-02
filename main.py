#!/usr/bin/env python3
"""
main.py - Basic Autonomous Operation Using Finished Modules

This version uses the ultrasonic sensor and camera capture modules.
It simulates the classification and control steps by simply printing messages.
"""

import time

# Import global settings
from config import DISTANCE_THRESHOLD, POLLING_INTERVAL

# Import finished sensor and camera functions
from sensors.ultrasonic_sensor import initialize as init_ultrasonic, measure_distance
from camera.camera_capture import initialize as init_camera, capture_image

def main():
    # Initialize the ultrasonic sensor and camera
    print("Initializing ultrasonic sensor and camera...")
    init_ultrasonic()
    init_camera()

    print("System started. Monitoring sensor input...")

    while True:
        distance = measure_distance()
        print("Distance: {:.2f} cm".format(distance))
        
        if distance < DISTANCE_THRESHOLD:
            print("Waste detected!")
            
            # Capture an image (but do not save it)
            image = capture_image()
            
            # Simulate classification (dummy result)
            print("Classifying image... (dummy result: plastic)")
            classification = "plastic"
            print("Classification result:", classification)
            
            # Simulate control actions with simple print statements and delays
            print("Moving the box to channel 1 (simulated stepper motor)...")
            time.sleep(1)
            
            print("Opening trapdoor (simulated servo motor)...")
            time.sleep(1)
            
            print("Closing trapdoor (simulated servo motor)...")
            time.sleep(1)
            
            print("Returning box to home position (simulated stepper motor)...")
            time.sleep(1)
            
            # Wait until the waste is cleared before continuing
            while measure_distance() < DISTANCE_THRESHOLD:
                print("Waiting for waste to clear...")
                time.sleep(POLLING_INTERVAL)
        else:
            time.sleep(POLLING_INTERVAL)

if __name__ == "__main__":
    main()
