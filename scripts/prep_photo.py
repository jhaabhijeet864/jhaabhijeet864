#!/usr/bin/env python3
"""
Prepares a raw photo for clean ASCII vector conversion:
1. Removes the background (using rembg if available, or alpha channel)
2. Applies bilateral filtering to eliminate noise and skin textures while preserving edges
3. Stretches tone range so background/skin lands near white and hair/contours stay dark
4. Darkens thin ridge linework (Difference-of-Gaussians) so facial features don't get lost
5. Composites onto pure white and saves a square-cropped source-prepped.png

Usage:
    python scripts/prep_photo.py <input_photo.png> [output_prepped.png]
"""
import os
import sys

import cv2
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
INP = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "source-photo.png")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "source-prepped.png")

LINE_WEIGHT = 0.6


def prep_image(input_path, output_path):
    if not os.path.exists(input_path):
        print(f"Error: Input photo '{input_path}' not found.", file=sys.stderr)
        return

    # Cutout
    try:
        from rembg import remove
        cut = remove(Image.open(input_path).convert("RGBA"))
    except ImportError:
        print("Note: rembg not installed. Reading RGBA directly.")
        cut = Image.open(input_path).convert("RGBA")

    rgb = np.array(cut.convert("RGB"))
    alpha = np.array(cut.split()[-1])
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

    # Smooth texture, preserve edges
    smooth = gray
    for _ in range(3):
        smooth = cv2.bilateralFilter(smooth, 9, 40, 9)

    # Tone stretch over subject
    mask_indices = alpha > 128
    if np.any(mask_indices):
        lo, hi = np.percentile(smooth[mask_indices], [2, 92])
        if hi > lo:
            tone = np.clip((smooth.astype(np.float32) - lo) / (hi - lo), 0, 1)
        else:
            tone = smooth.astype(np.float32) / 255.0
    else:
        tone = smooth.astype(np.float32) / 255.0

    # Ridge darkening (Difference of Gaussians)
    fine = cv2.GaussianBlur(smooth, (0, 0), 1.5).astype(np.float32)
    coarse = cv2.GaussianBlur(smooth, (0, 0), 6).astype(np.float32)
    lines = np.clip((coarse - fine) / 40.0, 0, 1)
    out = np.clip(tone - LINE_WEIGHT * lines, 0, 1) * 255.0

    # Paste onto white
    mask = cv2.GaussianBlur(alpha.astype(np.float32) / 255.0, (0, 0), 1.0)
    out = out * mask + 255.0 * (1.0 - mask)

    ys, xs = np.where(alpha > 20)
    if len(xs) > 0 and len(ys) > 0:
        side = max(xs.max() - xs.min(), ys.max() - ys.min()) + 60
        cx, cy = (xs.min() + xs.max()) // 2, (ys.min() + ys.max()) // 2
        canvas = np.full((side, side), 255, np.uint8)
        x0, y0 = cx - side // 2, cy - side // 2
        sx0, sy0 = max(x0, 0), max(y0, 0)
        sx1, sy1 = min(x0 + side, out.shape[1]), min(y0 + side, out.shape[0])
        canvas[sy0 - y0:sy1 - y0, sx0 - x0:sx1 - x0] = out[sy0:sy1, sx0:sx1].astype(np.uint8)
    else:
        canvas = out.astype(np.uint8)

    Image.fromarray(canvas, mode="L").save(output_path)
    print(f"Prepped photo saved to {output_path} ({canvas.shape})")


if __name__ == "__main__":
    prep_image(INP, OUT)
