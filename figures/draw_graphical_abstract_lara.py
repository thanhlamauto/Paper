"""Draw a compact LARA graphical abstract using the visual language of Fig. 1."""

from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape


OUT = Path(__file__).resolve().parent / "graphical_abstract_lara.svg"
svg: list[str] = []


def add(value: str) -> None:
    svg.append(value)


def text(x, y, value, size=32, color="#1a2940", weight=700, anchor="middle"):
    add(
        f'<text x="{x}" y="{y}" text-anchor="{anchor}" fill="{color}" '
        f'font-size="{size}" font-weight="{weight}">{escape(value)}</text>'
    )


COLORS = {
    "neutral": ("#eaf0f5", "#f9fbfd", "#afc1d1", "#8da5b9"),
    "source": ("#d7ecf2", "#f0fbff", "#5ba8be", "#287e9a"),
    "target": ("#fbe0e8", "#fff3f6", "#db809a", "#bd5678"),
    "predict": ("#eadcf7", "#f9f1ff", "#ad84d4", "#8455ae"),
    "align": ("#ffe9d7", "#fff7ed", "#e9a666", "#c7803a"),
}


def prism(x, y, w, h, kind, label, size=32):
    front, top, side, edge = COLORS[kind]
    depth = 9
    add(
        f'<g filter="url(#shadow)">'
        f'<path d="M{x} {y} L{x+depth} {y-depth} L{x+w+depth} {y-depth} '
        f'L{x+w} {y} Z" fill="{top}" stroke="{edge}" stroke-width="1.5"/>'
        f'<path d="M{x+w} {y} L{x+w+depth} {y-depth} '
        f'L{x+w+depth} {y+h-depth} L{x+w} {y+h} Z" '
        f'fill="{side}" stroke="{edge}" stroke-width="1.5"/>'
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" '
        f'fill="{front}" stroke="{edge}" stroke-width="2"/></g>'
    )
    if label:
        text(x + w / 2, y + h / 2 + size / 3, label, size)


def line(d, color="#253952", width=3.2, arrow=True, dashed=False):
    marker = ' marker-end="url(#arrow)"' if arrow else ""
    dash = ' stroke-dasharray="8 7"' if dashed else ""
    add(
        f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" '
        f'stroke-linecap="round" stroke-linejoin="round"{marker}{dash}/>'
    )


def panel(x, width, title, accent):
    add(
        f'<rect x="{x}" y="16" width="{width}" height="391" rx="17" '
        f'fill="white" stroke="#d8e2eb" stroke-width="1.8"/>'
        f'<path d="M{x+17} 16 H{x+width-17} Q{x+width} 16 {x+width} 33 '
        f'V75 H{x} V33 Q{x} 16 {x+17} 16 Z" fill="{accent}"/>'
    )
    text(x + width / 2, 55, title, 35, "white", 800)


add('<svg xmlns="http://www.w3.org/2000/svg" width="1320" height="590" viewBox="0 0 1320 590" font-family="Verdana,Arial,sans-serif">')
add('<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8.5" refY="5" orient="auto" markerUnits="userSpaceOnUse"><path d="M0 0 L10 5 L0 10 Z" fill="#253952"/></marker><filter id="shadow" x="-15%" y="-35%" width="140%" height="180%"><feDropShadow dx="2" dy="3" stdDeviation="2" flood-color="#273b56" flood-opacity="0.16"/></filter></defs>')
add('<rect width="1320" height="590" fill="#f4f7f9"/>')

panel(16, 317, "01  Layer pair", "#1c4965")
panel(347, 558, "02  Shared predictor", "#1c4965")
panel(919, 385, "03  Match target", "#9a315e")

# The DiT stack, sampled source and target, and their two distinct paths.
text(174, 111, "DiT backbone", 30, "#304762")
line("M238 147 V344", "#c7d5e0", 2, False, True)
prism(181, 135, 110, 43, "neutral", "···", 30)
prism(181, 192, 110, 52, "target", "A_b", 35)
prism(181, 263, 110, 43, "neutral", "···", 30)
prism(181, 324, 110, 52, "source", "A_a", 35)
text(158, 226, "target", 27, "#96506b", 600, "end")
text(158, 358, "source", 27, "#287e9a", 600, "end")
prism(39, 323, 94, 51, "neutral", "x_t", 34)
line("M137 348 H172")

# Target bypasses the predictor and serves as a stop-gradient reference.
line("M301 216 H929 V184 H947", "#bd5678", 3.1, True, True)
text(1027, 147, "stop-grad target", 25, "#96506b", 600)
prism(958, 164, 138, 61, "target", "A_b", 35)

# The source is mapped to target-layer coordinates by one shared model.
line("M301 350 H430 V286 H452")
text(626, 115, "condition on timestep + layers", 29, "#536782", 600)
prism(415, 143, 105, 48, "neutral", "e_t", 32)
prism(572, 143, 105, 48, "source", "e_a", 32)
prism(729, 143, 105, 48, "target", "e_b", 32)
line("M625 195 V224", "#8455ae", 3)
prism(458, 236, 336, 100, "predict", "")
text(626, 282, "Gψ", 45)
text(626, 321, "768 → 384 → 768", 27, "#4f3e69", 600)
text(626, 381, "10 spatial blocks · attention at 4, 8", 25, "#536782", 600)
line("M803 286 H870 V348 H946")
text(1027, 301, "prediction", 25, "#96506b", 600)
prism(958, 317, 138, 61, "target", "Â_b", 35)

# Prediction loss compares the two target-space outputs.
line("M1105 195 H1145 V257 H1159")
line("M1105 348 H1145 V289 H1159")
prism(1164, 253, 107, 54, "align", "match", 27)
text(1218, 354, "L_pred", 28, "#9a315e")

# A separate row keeps all training signals visible at submission size.
cards = (
    (16, "#4e9457", "Flow matching", "velocity fit"),
    (340, "#bd5678", "Prediction", "target match"),
    (664, "#8455ae", "Consistency", "direct vs EMA"),
    (988, "#287e9a", "Redundancy", "layer diversity"),
)
for x, accent, heading, detail in cards:
    add(f'<rect x="{x}" y="426" width="316" height="148" rx="15" fill="white" stroke="#d8e2eb" stroke-width="1.8"/>')
    add(f'<rect x="{x+18}" y="449" width="7" height="96" rx="3" fill="{accent}"/>')
    text(x + 41, 490, heading, 31, "#263951", 700, "start")
    text(x + 41, 540, detail, 29, "#536782", 600, "start")

add('</svg>')
OUT.write_text("\n".join(svg), encoding="utf-8")
print(OUT)
