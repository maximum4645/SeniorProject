#!/usr/bin/env python3
"""
check_accuracy.py - Evaluate TFLite model on a directory of labeled images.

Assumes test images are organized under `model/garbage_classification/<class_label>/`.
Calculates overall accuracy and per-class accuracy, printing one line per image.
"""

import os
import sys
import cv2
import numpy as np
from pathlib import Path

# Ensure project root is on sys.path so inference.py can import config.py
SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))  # .../SeniorProject/model
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)                 # .../SeniorProject
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from inference import TFLiteClassifier  # inference.py lives in the same folder

# MODEL_PATH in config.py should be "model/mobilenet_v2.tflite"
# TFLiteClassifier will resolve that under PROJECT_ROOT → SeniorProject/model/…

def load_images_from_folder(root_folder: Path):
    """
    Walk through root_folder, expecting subfolders whose names are class labels.
    Returns a list of (image_path, ground_truth_label) tuples.
    """
    data = []
    for class_dir in root_folder.iterdir():
        if not class_dir.is_dir():
            continue
        class_label = class_dir.name
        for ext in ("*.jpg", "*.jpeg", "*.png", "*.bmp", "*.tiff"):
            for img_path in class_dir.glob(ext):
                data.append((img_path, class_label))
    return data

def main():
    # Initialize classifier (loads TFLite model)
    print("[INFO] Loading TFLite model…")
    classifier = TFLiteClassifier(__import__('config').MODEL_PATH)

    # Directory containing one subfolder per class
    images_root = Path(__file__).resolve().parent / "garbage_classification"
    if not images_root.exists():
        print(f"[ERROR] Images folder not found: {images_root}")
        return

    # Gather (image_path, true_label) pairs
    dataset = load_images_from_folder(images_root)
    if not dataset:
        print(f"[ERROR] No images found under {images_root}")
        return

    total_images = len(dataset)
    print(f"[INFO] Found {total_images} images to evaluate.\n")

    correct_count = 0
    per_class_counts = {}
    per_class_correct = {}

    # Initialize per-class counters
    for _, label in dataset:
        per_class_counts.setdefault(label, 0)
        per_class_correct.setdefault(label, 0)

    # Loop through each image and evaluate
    for idx, (img_path, true_label) in enumerate(dataset, 1):
        img = cv2.imread(str(img_path))
        if img is None:
            print(f"[{idx}/{total_images}] {img_path.name}: unable to read")
            continue

        pred_label, _ = classifier.predict(img)
        per_class_counts[true_label] += 1
        if pred_label == true_label:
            correct_count += 1
            per_class_correct[true_label] += 1

        print(f"[{idx}/{total_images}] {img_path.name}: true={true_label}  pred={pred_label}")

        # Free memory for this iteration
        del img

    # Compute and print overall results
    overall_accuracy = (correct_count / total_images) * 100.0
    print("\n=== Final Results ===")
    print(f"Total images evaluated: {total_images}")
    print(f"Correct predictions:    {correct_count}")
    print(f"Overall accuracy:       {overall_accuracy:.2f}%\n")

    print("Per-class accuracy:")
    for class_label in sorted(per_class_counts.keys()):
        count = per_class_counts[class_label]
        correct = per_class_correct[class_label]
        accuracy = (correct / count * 100.0) if count > 0 else 0.0
        print(f"  {class_label:10s}: {correct:3d}/{count:3d}  ({accuracy:.2f}%)")

if __name__ == "__main__":
    main()
