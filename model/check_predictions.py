#!/usr/bin/env python3
"""
check_predictions.py - Evaluate TFLite model on a directory of labeled images,
                       and separate correctly and incorrectly classified images into folders.

Assumes images are organized under subdirectories of `garbage_classification/` named after class labels.
Creates `sorted/correct/<label>/` and `sorted/wrong/<label>/` and copies images accordingly,
renaming wrong images to include their predicted label.
"""

import shutil
from pathlib import Path
import cv2
import numpy as np
from inference import TFLiteClassifier

# Path to TFLite model (uses MODEL_PATH from config via TFLiteClassifier)
MODEL_RELATIVE_PATH = "model/mobilenet_v2.tflite"

def load_images_from_folder(root_folder: Path):
    """
    Walk through root_folder, expecting subfolders whose names are class labels.
    Returns a list of tuples: (image_path, ground_truth_label).
    """
    data = []
    for class_dir in root_folder.iterdir():
        if not class_dir.is_dir():
            continue
        class_label = class_dir.name
        # Accept common image extensions
        for ext in ("*.jpg", "*.jpeg", "*.png", "*.bmp", "*.tiff"):
            for img_path in class_dir.glob(ext):
                data.append((img_path, class_label))
    return data

def main():
    # Initialize classifier
    classifier = TFLiteClassifier(MODEL_RELATIVE_PATH)

    # Directory containing subfolders for each class
    images_root = Path(__file__).resolve().parent / "garbage_classification"
    if not images_root.exists():
        print(f"[ERROR] Images folder not found: {images_root}")
        return

    # Load image paths and their ground-truth labels
    dataset = load_images_from_folder(images_root)
    if not dataset:
        print(f"No images found under {images_root}")
        return

    # Prepare output directories
    output_root = Path(__file__).resolve().parent / "sorted"
    if output_root.exists():
        shutil.rmtree(output_root)
    correct_root = output_root / "correct"
    wrong_root   = output_root / "wrong"
    correct_root.mkdir(parents=True, exist_ok=True)
    wrong_root.mkdir(parents=True, exist_ok=True)

    total_images      = len(dataset)
    correct_count     = 0
    per_class_counts  = {}
    per_class_correct = {}

    # Initialize per-class counters
    for _, label in dataset:
        per_class_counts.setdefault(label, 0)
        per_class_correct.setdefault(label, 0)

    # Iterate over all images
    for img_path, true_label in dataset:
        # Read image as BGR
        img = cv2.imread(str(img_path))
        if img is None:
            print(f"[WARNING] Unable to read image: {img_path}")
            continue

        # Run inference
        pred_label, _ = classifier.predict(img)

        # Update counters
        per_class_counts[true_label] += 1
        if pred_label == true_label:
            correct_count += 1
            per_class_correct[true_label] += 1
            dest_dir  = correct_root / true_label
            dest_name = img_path.name
        else:
            dest_dir  = wrong_root / true_label
            dest_name = f"{img_path.stem}_{pred_label}{img_path.suffix}"

        dest_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(img_path, dest_dir / dest_name)

    # Compute and print results
    overall_accuracy = correct_count / total_images * 100.0
    print(f"\n=== Results ===")
    print(f"Total images evaluated: {total_images}")
    print(f"Correct predictions:    {correct_count}")
    print(f"Overall accuracy:       {overall_accuracy:.2f}%\n")

    print("Per-class accuracy:")
    for class_label in sorted(per_class_counts.keys()):
        count   = per_class_counts[class_label]
        correct = per_class_correct[class_label]
        accuracy = (correct / count * 100.0) if count > 0 else 0.0
        print(f"  {class_label:10s}: {correct:3d}/{count:3d}  ({accuracy:.2f}%)")

if __name__ == "__main__":
    main()
