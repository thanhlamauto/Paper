"""Build Figure 9 from the supplied PCA comparison grid.

The selected L1 -> L11 transition is the long-range pair (gap >= 8)
with the largest mean displayed-image similarity gain over the source
among pairs with a visually detailed target map and consistent
predictor/target similarity at every sampled t.
These JPEG correlations are only a reproducible visual selection aid;
they are not representation metrics reported in the paper.
"""

from pathlib import Path
import base64
import io
import os
import subprocess
import sys
import tempfile
from xml.sax.saxutils import escape
import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "figures"))
from figure_typography import embedded_font_css, font_weight, with_text_shadow
SOURCE = ROOT / "figures" / "pca_comparison_grid.pdf"
OUTPUT = ROOT / "figures" / "predictor_output_behavior.pdf"
PAIR = (1, 11)
TIMESTEPS_DESCENDING = (0.9, 0.7, 0.5, 0.3, 0.1)
ROW_STARTS = (452, 632, 811, 990, 1170)
TILE_SIZE = 142


def render_styled_figure(rows):
    """Keep the extracted RGB pixels while changing diagram typography/layout."""
    parts = []

    def add(markup):
        parts.append(with_text_shadow(markup))

    def text(x, y, label, size=36, color="#1a2940", weight=700, anchor="middle", italic=False):
        style = ' font-style="italic"' if italic else ''
        add(f'<text x="{x}" y="{y}" text-anchor="{anchor}" fill="{color}" '
            f'font-size="{size}" font-weight="{font_weight(weight)}"{style}>{escape(label)}</text>')

    colors = {
        "source": ("#d7ecf2", "#f0fbff", "#5ba8be", "#287e9a"),
        "predict": ("#eadcf7", "#f9f1ff", "#ad84d4", "#8455ae"),
        "target": ("#fbe0e8", "#fff3f6", "#db809a", "#bd5678"),
        "neutral": ("#eaf0f5", "#f9fbfd", "#afc1d1", "#8da5b9"),
    }

    def prism(x, y, width, height, kind):
        front, top, side, edge = colors[kind]
        d = 12
        add(f'<g filter="url(#shadow)"><path d="M{x} {y} l{d} -{d} h{width} l-{d} {d} Z" '
            f'fill="{top}" stroke="{edge}" stroke-width="1.5"/>'
            f'<path d="M{x+width} {y} l{d} -{d} v{height} l-{d} {d} Z" '
            f'fill="{side}" stroke="{edge}" stroke-width="1.5"/>'
            f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="5" '
            f'fill="{front}" stroke="{edge}" stroke-width="2"/></g>')

    def state_label(cx, y, index, predicted=False):
        # Align superscript and subscript beside the same A glyph.
        total_width = {"1": 53, "11": 68, "1→11": 111}[index]
        left = cx - total_width / 2
        text(left, y, 'Â' if predicted else 'A', 46, anchor="start", italic=True)
        text(left+34, y+12, index, 30, anchor="start")
        text(left+34, y-26, 't', 29, anchor="start", italic=True)

    add('<svg xmlns="http://www.w3.org/2000/svg" width="2400" height="1300" '
        'viewBox="0 0 2400 1300" font-family="Nimbus Roman,Times New Roman,Times,serif">')
    add(embedded_font_css())
    add('<defs><marker id="arrow" markerWidth="14" markerHeight="14" refX="14" refY="7" '
        'orient="auto" markerUnits="userSpaceOnUse"><path d="M0 0 L14 7 L0 14 Z" fill="#253952"/>'
        '</marker><filter id="shadow" x="-15%" y="-35%" width="140%" height="180%">'
        '<feDropShadow dx="3" dy="5" stdDeviation="3" flood-color="#273b56" flood-opacity="0.14"/>'
        '</filter></defs>')
    add('<rect width="2400" height="1300" fill="white"/>')
    add('<rect x="24" y="24" width="2352" height="1252" rx="24" '
        'fill="#fafafa" stroke="#505050" stroke-width="4.4"/>')
    text(90, 88, 'LARA: predictor-output visualization', 54, '#111111', anchor="start")
    add('<path d="M90 114 H2310" stroke="#606060" stroke-width="2"/>')
    text(315, 178, 'Layer 1 → layer 11', 35, '#536782')
    text(1470, 162, 'Increasing denoising time t', 35, '#536782')
    add('<path d="M680 190 H2260" fill="none" stroke="#253952" stroke-width="3.5" '
        'stroke-linecap="round" marker-end="url(#arrow)"/>')
    add('<rect x="658" y="281" width="1624" height="907" rx="18" '
        'fill="#fcfdff" stroke="#d8e2eb" stroke-width="1.8"/>')
    row_styles = [("Source", "source", "1"),
                  ("Prediction", "predict", "1→11"),
                  ("Target", "target", "11")]
    for row, (label, kind, index) in enumerate(row_styles):
        y = 300 + 304*row
        prism(95, y+55, 440, 150, kind)
        text(315, y+101, label, 42)
        state_label(315, y+166, index, predicted=(kind == "predict"))
    for col, t in enumerate(reversed(TIMESTEPS_DESCENDING)):
        x = 680 + 330*col
        prism(x, 222, 260, 42, "neutral")
        text(x+130, 253, f't = {t:.1f}', 35)
        for row, panel in enumerate(rows[col]):
            y = 300 + 304*row
            assert panel.shape == (TILE_SIZE, TILE_SIZE, 3)
            buffer = io.BytesIO()
            Image.fromarray(panel).save(buffer, format="PNG")
            uri = 'data:image/png;base64,' + base64.b64encode(buffer.getvalue()).decode()
            add(f'<rect x="{x-5}" y="{y-5}" width="270" height="270" rx="5" '
                'fill="white" stroke="#bdccda" stroke-width="1.8" filter="url(#shadow)"/>')
            add(f'<image href="{uri}" x="{x}" y="{y}" width="260" height="260" '
                'image-rendering="optimizeSpeed"/>')
    text(1470, 1240, 'PCA maps at matched timesteps · source, prediction, and actual target',
         30, '#536782', 400)
    add('</svg>')
    svg = OUTPUT.with_suffix('.svg')
    svg.write_text('\n'.join(parts)+'\n')
    env = os.environ.copy()
    env.update(FONTCONFIG_FILE=str(ROOT/'figures/fonts/fonts.conf'), PANGOCAIRO_BACKEND="fc")
    subprocess.run(['rsvg-convert', '-f', 'pdf', '-o', str(OUTPUT), str(svg)], check=True, env=env)
    png = OUTPUT.with_suffix('.png')
    subprocess.run(['rsvg-convert', '-f', 'png', '-w', '7200', '-h', '3900',
                    '-o', str(png), str(svg)], check=True, env=env)
    # Record 300 DPI without changing the rendered pixels.
    with Image.open(png) as rendered:
        rendered.save(png, dpi=(300, 300))
    print(svg)
    print(png)


def extract_grid():
    with tempfile.TemporaryDirectory() as directory:
        prefix = Path(directory) / "grid"
        subprocess.run(
            ["pdfimages", "-f", "1", "-l", "1", "-j", str(SOURCE), str(prefix)],
            check=True,
        )
        images = list(Path(directory).glob("grid-*.jpg"))
        if len(images) != 1:
            raise ValueError(f"Expected one embedded grid image, found {len(images)}")
        return np.asarray(Image.open(images[0]).convert("RGB"))


def tile_starts(grid):
    colored = np.min(grid[500], axis=1) < 220
    starts = np.flatnonzero(colored & ~np.roll(colored, 1))
    starts = [int(x) for x in starts if x > 50]
    if len(starts) != 84:
        raise ValueError(f"Expected 84 grid panels, found {len(starts)}")
    return starts


def pearson(a, b):
    return float(np.corrcoef(a.reshape(-1), b.reshape(-1))[0, 1])


def main():
    grid = extract_grid()
    starts = tile_starts(grid)
    pairs = [
        (a, b)
        for a in (1, 5, 9, 13, 17, 21)
        for b in range(a + 2, min(a + 10, 27) + 1, 2)
    ]

    def panels(pair):
        index = pairs.index(pair)
        return [
            [
                grid[y : y + TILE_SIZE, starts[3 * index + k] : starts[3 * index + k] + TILE_SIZE]
                for k in range(3)
            ]
            for y in ROW_STARTS
        ]

    eligible = []
    for pair in pairs:
        if pair[1] - pair[0] < 8:
            continue
        triplets = panels(pair)
        predicted = [pearson(p.astype(float), g.astype(float)) for _, p, g in triplets]
        source = [pearson(s.astype(float), g.astype(float)) for s, _, g in triplets]
        gain = np.mean(np.array(predicted) - np.array(source))
        image_side_target = triplets[0][2].astype(float)
        visible_detail = (
            np.mean(np.abs(np.diff(image_side_target, axis=0)))
            + np.mean(np.abs(np.diff(image_side_target, axis=1)))
        )
        if min(predicted) >= 0.90 and gain >= 0.05 and visible_detail >= 9:
            eligible.append((gain, pair))
    selected = max(eligible)[1]
    if selected != PAIR:
        raise ValueError(f"Selection changed: expected {PAIR}, found {selected}")
    print(f"Selected L{PAIR[0]} -> L{PAIR[1]} (visual selection score {max(eligible)[0]:.3f})")

    rows = list(reversed(panels(PAIR)))  # t increases from noise toward image.
    render_styled_figure(rows)
    print(OUTPUT)


if __name__ == "__main__":
    main()
