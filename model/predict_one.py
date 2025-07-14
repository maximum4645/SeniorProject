#!/usr/bin/env python3
"""
predict_one.py – Run TFLite model on a single image and print its prediction.

Usage:
    python3 predict_one.py <path_to_image>
"""

import sys
from pathlib import Path

import cv2
import numpy as np

from inference import TFLiteClassifier   # same import style as your other scripts

# Path to your .tflite model, relative to project root
MODEL_RELATIVE_PATH = "model/model_1.tflite"

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <path_to_image>")
        return

    img_path = Path(sys.argv[1])
    if not img_path.exists():
        print(f"[ERROR] Image not found: {img_path}")
        return

    # Read image as BGR
    img = cv2.imread(str(img_path))
    if img is None:
        print(f"[ERROR] Unable to read image: {img_path}")
        return

    # Initialize classifier and run prediction
    classifier = TFLiteClassifier(MODEL_RELATIVE_PATH)
    label, score = classifier.predict(img)

    # Print result
    print(f"Predicted: {label}  (confidence: {score:.2f})")

if __name__ == "__main__":
    main()
