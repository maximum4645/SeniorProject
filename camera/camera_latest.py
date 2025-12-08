#!/usr/bin/env python3
"""
camera_latest.py

Flask interface for monitoring data collection:
- Shows the most recently saved image from IMAGE_SAVE_DIR.
- Displays its human class label (from folder/filename).
- Lets you run AI inference (TFLite) on the latest image via a Classify button.
"""

import os
import sys
from datetime import datetime
from typing import Optional, Tuple

import cv2
from flask import Flask, render_template, send_from_directory, url_for

SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config import IMAGE_SAVE_DIR, CAMERA_RESOLUTION, MODEL_PATH
from model.inference import TFLiteClassifier

app = Flask(__name__)

_classifier: Optional[TFLiteClassifier] = None


def _get_classifier() -> Optional[TFLiteClassifier]:
    """Lazy-load the global TFLite classifier instance."""
    global _classifier
    if _classifier is None:
        try:
            _classifier = TFLiteClassifier(MODEL_PATH)
            print(f"[CAMERA_LATEST] Loaded TFLite model from {MODEL_PATH}")
        except Exception as exc:
            print(f"[CAMERA_LATEST] Failed to load model: {exc}")
            _classifier = None
    return _classifier


def _find_latest_image(root_dir: str) -> Optional[Tuple[str, float]]:
    """Return (full_path, mtime) of the newest image file under root_dir, or None."""
    latest_path: Optional[str] = None
    latest_mtime: float = 0.0

    for dirpath, _, filenames in os.walk(root_dir):
        for name in filenames:
            lower = name.lower()
            if not (lower.endswith(".jpg") or lower.endswith(".jpeg") or lower.endswith(".png")):
                continue

            full_path = os.path.join(dirpath, name)
            try:
                mtime = os.path.getmtime(full_path)
            except OSError:
                continue

            if mtime > latest_mtime:
                latest_mtime = mtime
                latest_path = full_path

    if latest_path is None:
        return None
    return latest_path, latest_mtime


def _extract_class_from_relpath(rel_path: str) -> str:
    """Extract a class label from a relative path like 'plastic/plastic12.jpg'."""
    parts = rel_path.split(os.sep)
    if len(parts) > 1:
        # IMAGE_SAVE_DIR/<class>/<filename>
        return parts[0]

    base = os.path.splitext(parts[0])[0]  # e.g. "plastic12"
    i = len(base) - 1
    while i >= 0 and base[i].isdigit():
        i -= 1
    return base[: i + 1] or base


def _build_base_context() -> Tuple[dict, Optional[str]]:
    """Build the context for latest.html that is common to both routes.

    Returns:
        (context_dict, full_image_path_or_None)
    """
    result = _find_latest_image(IMAGE_SAVE_DIR)
    if result is None:
        ctx = dict(
            latest_url=None,
            latest_time=None,
            latest_class=None,
            ai_label=None,
            ai_confidence=None,
            ai_error=None,
            camera_resolution=CAMERA_RESOLUTION,
        )
        return ctx, None

    full_path, mtime = result
    rel_path = os.path.relpath(full_path, IMAGE_SAVE_DIR)
    img_url = url_for("serve_image", path=rel_path, t=int(mtime))
    ts_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
    cls = _extract_class_from_relpath(rel_path)

    ctx = dict(
        latest_url=img_url,
        latest_time=ts_str,
        latest_class=cls,
        ai_label=None,
        ai_confidence=None,
        ai_error=None,
        camera_resolution=CAMERA_RESOLUTION,
    )
    return ctx, full_path


@app.route("/")
def latest():
    """Show the latest captured image and its human label (no AI yet)."""
    ctx, _ = _build_base_context()
    return render_template("latest.html", **ctx)


@app.route("/classify_latest", methods=["POST"])
def classify_latest():
    """Run TFLite inference on the latest image and show the prediction."""
    ctx, full_path = _build_base_context()
    if full_path is None:
        ctx["ai_error"] = "No images available yet."
        return render_template("latest.html", **ctx)

    classifier = _get_classifier()
    if classifier is None:
        ctx["ai_error"] = "Model is not available (failed to load). See server logs."
        return render_template("latest.html", **ctx)

    image_bgr = cv2.imread(full_path)
    if image_bgr is None:
        ctx["ai_error"] = "Failed to read latest image from disk."
        return render_template("latest.html", **ctx)

    try:
        label, score = classifier.predict(image_bgr)
        ctx["ai_label"] = label
        ctx["ai_confidence"] = score
    except Exception as exc:
        ctx["ai_error"] = f"Inference error: {exc}"

    return render_template("latest.html", **ctx)


@app.route("/images/<path:path>")
def serve_image(path: str):
    """Serve static image files from IMAGE_SAVE_DIR."""
    return send_from_directory(IMAGE_SAVE_DIR, path)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True, use_reloader=False)
