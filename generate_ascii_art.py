"""
High-Detail ASCII Art Generator for GitHub Dark Theme (#0d1117)
Usage:
    python generate_ascii_art.py [input_image_path] [output_image_path]
Example:
    python generate_ascii_art.py my_photo.jpg ascii-art.png
"""

import sys
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

# Character ramp tailored for dark background (from lowest intensity/dark to highest intensity/bright)
RAMP = " .'`^\",:;Il!i~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"

def generate_ascii(input_path="photo.jpg", output_path="ascii-art.png", target_width_chars=160, contrast=1.4, sharpness=1.5):
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found.")
        print("Please provide a path to your photo, e.g.: python generate_ascii_art.py photo.jpg")
        return

    # 1. Load and enhance source image
    img = Image.open(input_path).convert("L")
    
    # Auto-crop or enhance dynamic range
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(contrast)
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(sharpness)

    # 2. Calculate aspect ratio (characters are ~2x taller than wide)
    orig_w, orig_h = img.size
    aspect = orig_h / orig_w
    target_height_chars = int(target_width_chars * aspect * 0.5)

    img_small = img.resize((target_width_chars, target_height_chars), Image.Resampling.LANCZOS)
    pixels = np.array(img_small, dtype=float)

    # Normalize to ramp range
    p_min, p_max = pixels.min(), pixels.max()
    if p_max > p_min:
        norm = (pixels - p_min) / (p_max - p_min)
    else:
        norm = pixels / 255.0

    ramp_len = len(RAMP) - 1
    indices = (norm * ramp_len).astype(int)

    # 3. Render onto high-res canvas with GitHub dark background (#0d1117)
    try:
        font = ImageFont.truetype("consola.ttf", 14)
    except:
        try:
            font = ImageFont.truetype("cour.ttf", 14)
        except:
            font = ImageFont.load_default()

    bbox = font.getbbox("M")
    char_w = bbox[2] - bbox[0] + 1
    char_h = bbox[3] - bbox[1] + 2

    canvas_w = target_width_chars * char_w + 30
    canvas_h = target_height_chars * char_h + 30

    out_img = Image.new("RGB", (canvas_w, canvas_h), "#0d1117")
    draw = ImageDraw.Draw(out_img)

    for r in range(target_height_chars):
        y = 15 + r * char_h
        for c in range(target_width_chars):
            x = 15 + c * char_w
            ch = RAMP[indices[r, c]]
            val = norm[r, c]
            
            # Subtle gradient: faint blue for midtones, crisp white for highlights
            if val > 0.7:
                color = "#f0f6fc"
            elif val > 0.4:
                color = "#c9d1d9"
            elif val > 0.2:
                color = "#58a6ff"
            else:
                color = "#30363d"

            if ch != " ":
                draw.text((x, y), ch, fill=color, font=font)

    out_img.save(output_path, quality=95)
    print(f"Successfully generated high-detail ASCII art saved to '{output_path}' ({canvas_w}x{canvas_h})")

if __name__ == "__main__":
    inp = sys.argv[1] if len(sys.argv) > 1 else "photo.jpg"
    out = sys.argv[2] if len(sys.argv) > 2 else "ascii-art.png"
    generate_ascii(inp, out)
