"""Render real SRA PCA outputs in the paper's shared diagram style."""

from pathlib import Path
from xml.sax.saxutils import escape
import base64
import json
import numpy as np
from PIL import Image
from figure_typography import embedded_font_css, font_weight, with_text_shadow

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "measurements" / "sit_xl2_pca"
meta = json.loads((DATA / "metadata.json").read_text())
parts = []


def add(markup):
    parts.append(with_text_shadow(markup))


def text(x, y, label, size=34, color="#1a2940", weight=700, extra=""):
    add(f'<text x="{x}" y="{y}" text-anchor="middle" fill="{color}" '
        f'font-size="{size}" font-weight="{font_weight(weight)}" {extra}>{escape(label)}</text>')


def line(x1, y1, x2, y2):
    add(f'<path d="M{x1} {y1} L{x2} {y2}" fill="none" stroke="#253952" '
        'stroke-width="3.5" stroke-linecap="round" marker-end="url(#arrow)"/>')


def layer_tag(x, label):
    y, w, h, d = 225, 218, 46, 9
    add(f'<g filter="url(#shadow)"><path d="M{x} {y} l{d} -{d} h{w} l-{d} {d} Z" '
        'fill="#f9fbfd" stroke="#8da5b9" stroke-width="1.5"/>'
        f'<path d="M{x+w} {y} l{d} -{d} v{h} l-{d} {d} Z" '
        'fill="#afc1d1" stroke="#8da5b9" stroke-width="1.5"/>'
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" '
        'fill="#eaf0f5" stroke="#8da5b9" stroke-width="1.8"/></g>')
    text(x+w/2, y+34, label, 34)


def pca_tile(x, y, path):
    pixels = np.array(Image.open(path).convert("RGB"))
    assert pixels.shape == (16, 16, 3)
    add(f'<rect x="{x-5}" y="{y-5}" width="220" height="220" rx="5" '
        'fill="white" stroke="#bdccda" stroke-width="1.8" filter="url(#shadow)"/>')
    # Exact 8-bit PCA colors in vector cells, avoiding image interpolation.
    add(f'<g transform="translate({x} {y}) scale(13.125)" shape-rendering="crispEdges">')
    for row in range(16):
        for col in range(16):
            r, g, b = pixels[row, col]
            add(f'<rect x="{col}" y="{row}" width="1" height="1" fill="#{r:02x}{g:02x}{b:02x}"/>')
    add('</g>')


add('<svg xmlns="http://www.w3.org/2000/svg" width="2400" height="1420" '
    'viewBox="0 0 2400 1420" font-family="Nimbus Roman,Times New Roman,Times,serif">')
add(embedded_font_css())
add('<defs><marker id="arrow" markerWidth="14" markerHeight="14" refX="14" refY="7" '
    'orient="auto" markerUnits="userSpaceOnUse"><path d="M0 0 L14 7 L0 14 Z" fill="#253952"/>'
    '</marker><filter id="shadow" x="-15%" y="-35%" width="140%" height="180%">'
    '<feDropShadow dx="3" dy="5" stdDeviation="3" flood-color="#273b56" flood-opacity="0.14"/>'
    '</filter></defs>')
add('<rect width="2400" height="1420" fill="#f4f7f9"/>')
add('<rect x="24" y="24" width="2352" height="1372" rx="24" fill="white" '
    'stroke="#d8e2eb" stroke-width="2"/>')
add('<path d="M48 24 H2352 Q2376 24 2376 48 V114 H24 V48 Q24 24 48 24 Z" fill="#1c4965"/>')
text(1200, 84, '(a) PCA across depth and denoising time', 46, 'white')
text(1445, 162, 'Increasing block depth', 35, '#536782')
line(620, 190, 2280, 190)
text(192, 270, 'Input image', 34, '#536782')
uri = 'data:image/png;base64,' + base64.b64encode((DATA/'input_goose.png').read_bytes()).decode()
add('<rect x="70" y="299" width="244" height="244" rx="9" fill="#eaf0f5" '
    'stroke="#8da5b9" stroke-width="2" filter="url(#shadow)"/>')
add(f'<image href="{uri}" x="78" y="307" width="228" height="228"/>')
text(192, 595, 'Goose', 32, '#63758b', 400)
text(462, 260, 'Timestep', 34, '#536782')
line(355, 335, 355, 1300)
text(303, 905, 'Denoising time t', 36, '#536782', 700,
     'transform="rotate(90 303 905)"')
add('<rect x="593" y="289" width="1725" height="1038" rx="18" '
    'fill="#fcfdff" stroke="#d8e2eb" stroke-width="1.8"/>')

for col, layer in enumerate(meta['layers']):
    layer_tag(616+240*col, f'Block {layer}')
for row, t in enumerate(meta['timesteps']):
    y = 310 + 260*row
    text(462, y+105, f't = {t:.2f}', 38)
    for col, layer in enumerate(meta['layers']):
        pca_tile(620+240*col, y, DATA/'maps'/f't_{t:.2f}_layer_{layer:02d}.png')
text(1445, 1370, 'Frozen SiT-XL/2 · 16 × 16 tokens · RGB: first three principal components',
     29, '#536782', 400)
add('</svg>')
target = HERE / 'PCA.svg'
target.write_text('\n'.join(parts)+'\n')
print(target)
