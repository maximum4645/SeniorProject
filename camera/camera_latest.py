#!/usr/bin/env python3
"""
camera_latest.py

Flask interface for monitoring data collection:
- Shows the most recently saved image from IMAGE_SAVE_DIR.
- Displays its class label (derived from the path/filename).
- Does NOT talk to the camera; it only reads files written by main_button.py.
"""

import os
import sys
from datetime import datetime
from typing import Optional, Tuple

# Same style as camera_interface.py
SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from flask import Flask, render_template, send_from_directory, url_for
from config import IMAGE_SAVE_DIR, CAMERA_RESOLUTION

app = Flask(__name__)


def _find_latest_image(root_dir: str) -> Optional[Tuple[str, float]]:
    """
    Walk IMAGE_SAVE_DIR (and subfolders) and return (full_path, mtime)
    of the newest image file, or None if there are no images yet.
    """
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
    """
    Try to extract the class label from a relative path
    like 'plastic/plastic12.jpg' or 'paper3.jpg'.
    """
    parts = rel_path.split(os.sep)
    if len(parts) > 1:
        # IMAGE_SAVE_DIR/<class>/<filename>
        return parts[0]

    # Fallback: use filename prefix before numeric index
    base = os.path.splitext(parts[0])[0]  # e.g. "plastic12"
    # Strip trailing digits
    i = len(base) - 1
    while i >= 0 and base[i].isdigit():
        i -= 1
    return base[: i + 1] or base


@app.route('/')
def latest():
    """
    Main page:
    - If an image exists, render latest.html with its URL, timestamp, and class.
    - Otherwise render latest.html with empty state.
    """
    result = _find_latest_image(IMAGE_SAVE_DIR)
    if result is None:
        return render_template(
            'latest.html',
            latest_url=None,
            latest_time=None,
            latest_class=None,
            camera_resolution=CAMERA_RESOLUTION,
        )

    full_path, mtime = result
    rel_path = os.path.relpath(full_path, IMAGE_SAVE_DIR)

    img_url = url_for('serve_image', path=rel_path, t=int(mtime))  # t = cache-buster
    ts_str  = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
    cls     = _extract_class_from_relpath(rel_path)

    return render_template(
        'latest.html',
        latest_url=img_url,
        latest_time=ts_str,
        latest_class=cls,
        camera_resolution=CAMERA_RESOLUTION,
    )


@app.route('/images/<path:path>')
def serve_image(path: str):
    """
    Static file handler for captured images under IMAGE_SAVE_DIR.
    """
    return send_from_directory(IMAGE_SAVE_DIR, path)


if __name__ == '__main__':
    # Run manually only when you want to monitor data collection.
    app.run(host='0.0.0.0', port=5001, debug=True, use_reloader=False)

