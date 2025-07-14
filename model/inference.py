#!/usr/bin/env python3
"""
inference.py – Loads a TFLite model and exports a function
              `predict(image_array)` that returns (label, confidence).
"""

import sys
import time
import cv2
import numpy as np
from pathlib import Path
from tflite_runtime.interpreter import Interpreter

# Ensure project root is on sys.path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import MODEL_PATH

# If you still want the live‐camera test in this file:
from camera.camera_capture import initialize, capture_image

# Class names must match your TFLite output ordering:
CLASS_NAMES = ['cardboard', 'glass', 'metal', 'paper', 'plastic', 'trash']


class TFLiteClassifier:
    def __init__(self, model_relative_path: str):
        model_file = ROOT / model_relative_path
        if not model_file.exists():
            raise FileNotFoundError(f"Model not found: {model_file}")
        self.interpreter = Interpreter(model_path=str(model_file))
        self.interpreter.allocate_tensors()

        # Cache the input/output tensor details
        inp = self.interpreter.get_input_details()[0]
        out = self.interpreter.get_output_details()[0]
        self.input_index = inp['index']
        self.output_index = out['index']

        # Determine model’s expected H×W × layout (NHWC vs NCHW)
        shape = inp['shape'].tolist()
        if len(shape) == 4 and shape[3] == 3:
            self.model_h, self.model_w, self.is_nhwc = shape[1], shape[2], True
        elif len(shape) == 4 and shape[1] == 3:
            self.model_h, self.model_w, self.is_nhwc = shape[2], shape[3], False
        else:
            raise ValueError(f"Unsupported input shape: {shape}")

    def _preprocess(self, image_bgr: np.ndarray) -> np.ndarray:
        """Resize, BGR→RGB, normalize to [-1,1], and add batch dimension."""
        resized = cv2.resize(image_bgr, (self.model_w, self.model_h))
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        norm = (rgb.astype(np.float32) / 255.0 - 0.5) / 0.5  # MobileNet‐style
        if self.is_nhwc:
            return np.expand_dims(norm, 0).astype(np.float32)  # [1,H,W,3]
        else:
            # transpose to [1,3,H,W]
            return np.expand_dims(np.transpose(norm, (2, 0, 1)), 0).astype(np.float32)

    def predict(self, image_bgr: np.ndarray) -> tuple[str, float]:
        """
        Run inference on a single BGR image array.
        Returns: (label_str, confidence_float).
        """
        tensor = self._preprocess(image_bgr)
        self.interpreter.set_tensor(self.input_index, tensor)
        self.interpreter.invoke()
        # get raw output and convert to probabilities via softmax
        raw = self.interpreter.get_tensor(self.output_index)[0]
        exp = np.exp(raw - np.max(raw))        # for numerical stability
        probs = exp / exp.sum()
        idx = int(np.argmax(probs))
        score = float(probs[idx] * 100.0)      # as a percentage (0–100)
        label = CLASS_NAMES[idx] if idx < len(CLASS_NAMES) else str(idx)
        return label, score


# If you still want a quick “run this to test with the Pi Camera”:
def main():
    # 1) Initialize camera and warm up
    cam = initialize(mode="still")
    time.sleep(2.0)
    for _ in range(3):
        _ = cam.capture_array()

    # 2) Capture one frame and classify
    frame = capture_image()
    classifier = TFLiteClassifier(MODEL_PATH)
    label, score = classifier.predict(frame)
    print(f"Predicted: {label}  (confidence: {score:.2f})")

    cam.stop()


if __name__ == "__main__":
    main()
