#!/usr/bin/env python3
"""
Debug-friendly inference.py for 6-class TFLite model on Pi Camera.
"""

import os
import sys
import time
import cv2
import numpy as np
from pathlib import Path
from tflite_runtime.interpreter import Interpreter

# Ensure the project root is on sys.path so imports resolve properly
SCRIPT_PATH  = Path(__file__).resolve()
PROJECT_ROOT = SCRIPT_PATH.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from camera.camera_capture import initialize, capture_image
from config import MODEL_PATH

CLASS_NAMES = ['cardboard', 'glass', 'metal', 'paper', 'plastic', 'trash']

def main():
    print("Starting inference process...")

    print("Initializing the camera in STILL mode...")
    cam = initialize(mode="still")
    time.sleep(2.0)

    print("Warming up: discarding a few frames for auto-exposure/white-balance...")
    for i in range(3):
        _ = cam.capture_array()
        print(f"  Discarded warm-up frame {i+1}")

    print("Capturing a single frame now...")
    frame = capture_image()
    print(f"  Frame captured with shape {frame.shape}")

    print("Loading the TFLite model...")
    model_file = PROJECT_ROOT / MODEL_PATH
    if not model_file.exists():
        print(f"ERROR: Model not found at {model_file}", file=sys.stderr)
        sys.exit(1)

    interpreter = Interpreter(model_path=str(model_file))
    interpreter.allocate_tensors()
    inp = interpreter.get_input_details()[0]
    out = interpreter.get_output_details()[0]
    print(f"  Model loaded; input tensor shape = {inp['shape'].tolist()}")

    print("Preprocessing the frame to match model input requirements...")
    shape = inp['shape'].tolist()
    if len(shape) == 4 and shape[3] == 3:
        H, W, nhwc = shape[1], shape[2], True
    elif len(shape) == 4 and shape[1] == 3:
        H, W, nhwc = shape[2], shape[3], False
    else:
        raise RuntimeError(f"Unsupported TFLite input shape: {shape}")

    resized = cv2.resize(frame, (W, H))
    rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
    normalized = (rgb.astype(np.float32) / 255.0 - 0.5) / 0.5

    if nhwc:
        tensor = np.expand_dims(normalized, 0).astype(np.float32)
    else:
        tensor = np.expand_dims(np.transpose(normalized, (2, 0, 1)), 0).astype(np.float32)

    print("Running inference on the preprocessed frame...")
    interpreter.set_tensor(inp['index'], tensor)
    interpreter.invoke()
    predictions = interpreter.get_tensor(out['index'])[0]
    idx = int(np.argmax(predictions))
    confidence = float(predictions[idx])
    label = CLASS_NAMES[idx] if idx < len(CLASS_NAMES) else str(idx)
    print(f"Result -> Predicted: {label}  (confidence: {confidence:.2f})")

    cam.stop()
    print("Camera stopped. Inference complete.")

if __name__ == "__main__":
    main()
