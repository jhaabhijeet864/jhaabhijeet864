#!/usr/bin/env python3
"""
Renders a live stats & streak card SVG from data/contributions.json.
Canvas size is 840 x 880 (identical to ascii.svg) so the two SVGs achieve
perfect 1:1 pixel parity when placed side by side at equal widths (420px each).

Features:
- Terminal window chrome with Mac dots and title bar
- 6 stat tiles (current streak, longest streak, total contributions, active days, peak day, avg/active day)
- Animated monthly contributions bar chart with height scaling
- Zero external service dependencies
"""
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "data", "contributions.json")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "stats.svg")

BG = "#0d1117"
BG2 = "#111722"
TILE = "#161b22"
FRAME = "#30363d"
MUTED = "#7d8590"
INK = "#e6edf3"
GREEN = "#39d353"
BAR = "#26a641"
ACCENT = "#58a6ff"

W, H = 840, 880
PAD = 20
TITLEBAR_H = 30
COLS, ROWS = 2, 3
GAP = 16
TILE_W = (W - PAD * 2 - GAP * (COLS - 1)) / COLS
TILE_H = 145
TILES_TOP = TITLEBAR_H + PAD + 4
CHART_TOP = TILES_TOP + ROWS * TILE_H + (ROWS - 1) * GAP + GAP

TILE_STAGGER = 0.12
SLIDE_DUR = 0.45
BAR_START = TILE_STAGGER * COLS * ROWS + 0.3
BAR_STAGGER = 0.05
BAR_DUR = 0.6


def short_date(d_str):
    if not d_str:
        return "—"
    try:
        return datetime.date.fromisoformat(d_str).strftime("%b %d")
    except Exception:
        return d_str


def span_text(s):
    if not s or not s.get("length"):
        return "—"
    return f"{short_date(s.get('start'))} – {short_date(s.get('end'))}"


def main():
    if not os.path.exists(SRC):
        print(f"Error: {SRC} not found. Run fetch_contributions.py first.", file=sys.stderr)
        sys.exit(1)

    with open(SRC, "r", encoding="utf-8") as f:
        data = json.load(f)

    cur = data["current_streak"]
    lng = data["longest_streak"]
    best = data["best_day"]
    n_days = len(data["days"])
    active_days = data["active_days"]

    tiles = [
        ("CURRENT STREAK", cur["length"], " days", span_text(cur), GREEN),
        ("LONGEST STREAK", lng["length"], " days", span_text(lng), INK),
        ("CONTRIBUTIONS", data["total_contributions"], "", "in the past year", INK),
        ("ACTIVE DAYS", active_days, f" / {n_days}", f"{active_days / n_days:.0%} of year", INK),
        ("PEAK DAY", best["count"], " commits", short_date(best.get("date")), INK),
        ("AVG / ACTIVE DAY", data["avg_per_active_day"], "", "contributions", INK),
    ]

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
        '<style>',
        f'.t{{opacity:0;animation:in {SLIDE_DUR}s ease-out both}}',
        '@keyframes in{0%{opacity:0;transform:translateY(14px)}100%{opacity:1;transform:translateY(0)}}',
        f'.b{{transform-box:fill-box;transform-origin:bottom;transform:scaleY(0);animation:grow {BAR_DUR}s ease-out both}}',
        '@keyframes grow{to{transform:scaleY(1)}}',
        '@media (prefers-reduced-motion: reduce){.t,.b{opacity:1!important;transform:none!important;animation:none!important}}',
        '</style>',
        '<defs>',
        f'<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">',
        f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>',
        '</linearGradient>',
        '</defs>',
        f'<rect width="{W}" height="{H}" rx="12" fill="url(#bg)"/>',
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="{FRAME}"/>',
        f'<line x1="0" y1="{TITLEBAR_H}" x2="{W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>',
    ]

    for i, dot in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        parts.append(f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dot}"/>')
    parts.append(f'<text x="{W/2}" y="{TITLEBAR_H/2 + 4}" fill="{MUTED}" font-size="12" '
                 f'text-anchor="middle">jhaabhijeet864@github: ~/stats --live</text>')

    # 6 Stat Tiles
    for i, (label, val, suffix, caption, accent) in enumerate(tiles):
        col = i % COLS
        row = i // COLS
        x = PAD + col * (TILE_W + GAP)
        y = TILES_TOP + row * (TILE_H + GAP)
        delay = i * TILE_STAGGER

        val_str = f"{val:,.1f}" if isinstance(val, float) else f"{int(round(val)):,}"
        parts.append(
            f'<g class="t" style="animation-delay:{delay:.2f}s">'
            f'<rect x="{x}" y="{y}" width="{TILE_W}" height="{TILE_H}" rx="8" '
            f'fill="{TILE}" stroke="{FRAME}" stroke-width="1"/>'
            f'<text x="{x + 18}" y="{y + 26}" fill="{MUTED}" font-size="11" font-weight="600" letter-spacing="1">{label}</text>'
            f'<text x="{x + 18}" y="{y + 82}" font-size="36" font-weight="700" fill="{accent}">'
            f'{val_str}<tspan font-size="16" font-weight="400" fill="{MUTED}">{suffix}</tspan></text>'
            f'<text x="{x + 18}" y="{y + 116}" fill="{MUTED}" font-size="12">{caption}</text>'
            f'</g>'
        )

    # Monthly bar chart
    chart_h = H - CHART_TOP - PAD
    parts.append(
        f'<g class="t" style="animation-delay:{ROWS*COLS*TILE_STAGGER:.2f}s">'
        f'<rect x="{PAD}" y="{CHART_TOP}" width="{W - PAD*2}" height="{chart_h}" rx="8" '
        f'fill="{TILE}" stroke="{FRAME}" stroke-width="1"/>'
        f'<text x="{PAD + 18}" y="{CHART_TOP + 24}" fill="{MUTED}" font-size="11" font-weight="600" letter-spacing="1">'
        f'MONTHLY CONTRIBUTIONS ACTIVITY</text>'
        f'</g>'
    )

    monthly = data.get("monthly", [])[-12:]  # Last 12 months
    if monthly:
        max_m = max((m["total"] for m in monthly), default=1) or 1
        n_m = len(monthly)
        inner_pad_x = 24
        inner_w = W - PAD*2 - inner_pad_x*2
        bar_gap = 12
        bar_w = (inner_w - bar_gap * (n_m - 1)) / n_m
        graph_top = CHART_TOP + 42
        graph_bottom = CHART_TOP + chart_h - 32
        avail_h = graph_bottom - graph_top

        for j, m_data in enumerate(monthly):
            bx = PAD + inner_pad_x + j * (bar_w + bar_gap)
            m_ratio = m_data["total"] / max_m
            bh = max(4, int(avail_h * m_ratio))
            by = graph_bottom - bh
            bar_color = ACCENT if m_data["total"] == max_m else BAR
            b_delay = BAR_START + j * BAR_STAGGER

            m_name = m_data["month"].split("-")[1]
            try:
                m_label = datetime.date(2026, int(m_name), 1).strftime("%b")
            except Exception:
                m_label = m_name

            parts.append(
                f'<g class="t" style="animation-delay:{b_delay:.2f}s">'
                f'<text x="{bx + bar_w/2}" y="{by - 6}" fill="{MUTED}" font-size="10" text-anchor="middle">{m_data["total"]}</text>'
                f'<rect class="b" x="{bx}" y="{by}" width="{bar_w}" height="{bh}" rx="3" fill="{bar_color}" '
                f'style="animation-delay:{b_delay:.2f}s"/>'
                f'<text x="{bx + bar_w/2}" y="{graph_bottom + 18}" fill="{MUTED}" font-size="11" text-anchor="middle">{m_label}</text>'
                f'</g>'
            )

    parts.append("</svg>")
    svg = "".join(parts)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Generated {OUT} ({len(svg)} bytes; {W}x{H})")


if __name__ == "__main__":
    main()
