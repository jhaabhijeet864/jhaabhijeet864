#!/usr/bin/env python3
"""
Converts ASCII art or portrait images into a self-typing vector SVG with terminal chrome:
- Fits exact 840 x 880 canvas (matching stats.svg)
- Renders terminal window controls and title bar
- Synchronized SMIL <clipPath> row wipe animation with edge-riding cursor
- Plays once top-to-bottom over ~6 seconds, then freezes
- Persistent blinking cursor prompt at bottom: jhaabhijeet864@github:~$ whoami Abhijeet Jha
- Compatible with GitHub's SVG rendering engine (no JS required)
"""
import html
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TXT_DEFAULT = os.path.join(HERE, "..", "ascii-art.txt")
IMG_DEFAULT = os.path.join(HERE, "..", "source-prepped.png")
OUT_DEFAULT = os.path.join(HERE, "..", "ascii.svg")

RAMP = " .`:-=+*cs#%@"

CANVAS_W = 840
CANVAS_H = 880
PAD = 20
TITLEBAR_H = 30
STATUS_H = 30

BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
TITLE_TEXT = "#7d8590"
INK = "#c9d1d9"
CURSOR = "#c9d1d9"


def load_lines(src_path):
    # Try reading as text first
    if os.path.exists(src_path) and (src_path.endswith(".txt") or not src_path.lower().endswith((".png", ".jpg", ".jpeg"))):
        for enc in ["utf-16le", "utf-8", "latin-1"]:
            try:
                with open(src_path, "r", encoding=enc, errors="ignore") as f:
                    lines = [l.rstrip("\r\n\ufeff") for l in f.readlines()]
                if lines and any(l.strip() for l in lines):
                    max_len = max(len(l) for l in lines)
                    # Normalize line lengths
                    padded = [l.ljust(max_len) for l in lines]
                    return padded
            except Exception:
                continue

    # Image sampling fallback
    try:
        from PIL import Image, ImageEnhance
        im = Image.open(src_path).convert("L")
        cols = 140
        rows = 78
        im = ImageEnhance.Contrast(im).enhance(1.15)
        im = im.resize((cols, rows), Image.Resampling.LANCZOS)
        px = im.load()
        lines = []
        for y in range(rows):
            chars = []
            for x in range(cols):
                lum = px[x, y] / 255.0
                lum = pow(lum, 1.15)
                if lum >= 0.82:
                    chars.append(" ")
                else:
                    idx = int((1.0 - lum) * (len(RAMP) - 1) + 0.5)
                    idx = max(0, min(len(RAMP) - 1, idx))
                    chars.append(RAMP[idx])
            lines.append("".join(chars))
        return lines
    except Exception as e:
        print(f"Error loading source image/text: {e}", file=sys.stderr)
        return []


def generate_svg(lines, out_path):
    if not lines:
        print("No ASCII lines found to render.", file=sys.stderr)
        sys.exit(1)

    rows_count = len(lines)
    cols_count = len(lines[0])

    art_w = CANVAS_W - PAD * 2
    art_h = CANVAS_H - TITLEBAR_H - STATUS_H - PAD

    cell_w = art_w / cols_count
    cell_h = art_h / rows_count
    font_size = cell_h * 0.88

    row_dur = 5.8 / rows_count
    stagger = row_dur

    art_top = TITLEBAR_H + 8

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" height="{CANVAS_H}" '
        f'viewBox="0 0 {CANVAS_W} {CANVAS_H}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
        '<defs>',
        f'<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">',
        f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>',
        '</linearGradient>',
        '</defs>',
        f'<rect width="{CANVAS_W}" height="{CANVAS_H}" rx="12" fill="url(#bg)"/>',
        f'<rect x="0.5" y="0.5" width="{CANVAS_W-1}" height="{CANVAS_H-1}" rx="12" fill="none" stroke="{FRAME}"/>',
        f'<line x1="0" y1="{TITLEBAR_H}" x2="{CANVAS_W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>',
    ]

    # Mac dots
    for i, dotcol in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        parts.append(f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dotcol}"/>')
    parts.append(f'<text x="{CANVAS_W/2}" y="{TITLEBAR_H/2 + 4}" fill="{TITLE_TEXT}" font-size="12" '
                 f'text-anchor="middle">jhaabhijeet864@github: ~$ ./portrait.sh</text>')

    # Rows with SMIL animation
    for ry, line in enumerate(lines):
        y = art_top + ry * cell_h + cell_h * 0.74
        row_y = art_top + ry * cell_h
        delay = ry * stagger
        safe = html.escape(line)
        text = (f'<text xml:space="preserve" x="{PAD}" y="{y:.1f}" fill="{INK}" '
                f'font-size="{font_size:.1f}" textLength="{art_w}" lengthAdjust="spacing">{safe}</text>')

        parts.append(
            f'<clipPath id="r{ry}"><rect x="{PAD}" y="{row_y:.1f}" height="{cell_h}" width="0">'
            f'<animate attributeName="width" from="0" to="{art_w}" begin="{delay:.3f}s" '
            f'dur="{row_dur:.2f}s" fill="freeze"/></rect></clipPath>'
        )
        parts.append(f'<g clip-path="url(#r{ry})">{text}</g>')
        parts.append(
            f'<rect y="{row_y+1:.1f}" width="{cell_w}" height="{max(1.0, cell_h-2):.1f}" fill="{CURSOR}" opacity="0">'
            f'<animate attributeName="x" from="{PAD}" to="{PAD+art_w}" begin="{delay:.3f}s" '
            f'dur="{row_dur:.2f}s" fill="freeze"/>'
            f'<set attributeName="opacity" to="0.85" begin="{delay:.3f}s"/>'
            f'<set attributeName="opacity" to="0" begin="{delay+row_dur:.3f}s"/></rect>'
        )

    # Status line
    status_line_y = art_top + rows_count * cell_h + 8
    status_y = status_line_y + 18
    parts.append(f'<line x1="0" y1="{status_line_y:.1f}" x2="{CANVAS_W}" y2="{status_line_y:.1f}" stroke="{FRAME}"/>')
    parts.append(f'<text x="{PAD}" y="{status_y:.1f}" fill="{TITLE_TEXT}" font-size="13">'
                 f'jhaabhijeet864@github:~$ whoami <tspan fill="{INK}">Abhijeet Jha</tspan></text>')
    
    status_chars = len("jhaabhijeet864@github:~$ whoami Abhijeet Jha ")
    parts.append(f'<rect x="{PAD + status_chars * 13 * 0.58:.1f}" y="{status_y-12:.1f}" width="8" height="14" fill="{INK}">'
                 f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" dur="1s" repeatCount="indefinite"/></rect>')

    parts.append("</svg>")
    svg = "".join(parts)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Generated {out_path} ({len(svg)} bytes; {CANVAS_W}x{CANVAS_H})")


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else (TXT_DEFAULT if os.path.exists(TXT_DEFAULT) else IMG_DEFAULT)
    out = sys.argv[2] if len(sys.argv) > 2 else OUT_DEFAULT
    lines = load_lines(src)
    generate_svg(lines, out)


if __name__ == "__main__":
    main()
