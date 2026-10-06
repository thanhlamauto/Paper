"""Alternative editorial-style, vector redraw of fig1.jpeg with 3D blocks."""

from __future__ import annotations

import base64
from pathlib import Path
from xml.sax.saxutils import escape


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PHOTOS = {
    key: "data:image/png;base64," + base64.b64encode((HERE / filename).read_bytes()).decode()
    for key, filename in {
        "clean": "example_dog_clean.png",
        "student": "example_dog_noisy_student.png",
        "ema": "example_dog_noisy_ema.png",
    }.items()
}
OUT = HERE / "fig1_v2.svg"
svg: list[str] = []


def add(s: str) -> None:
    svg.append(s)


def text(x, y, s, size=20, color="#1a2940", weight=500, anchor="middle", extra=""):
    add(f'<text x="{x}" y="{y}" text-anchor="{anchor}" fill="{color}" font-size="{size}" font-weight="{weight}" {extra}>{escape(s)}</text>')


def layer_text(x, y, sub, size=20, color="#1a2940", weight=700):
    """Set layer indices as actual subscripts instead of underscore characters."""
    add(f'<text x="{x}" y="{y}" text-anchor="middle" fill="{color}" font-size="{size}" font-weight="{weight}"><tspan font-style="italic">l</tspan><tspan baseline-shift="sub" font-size="70%">{escape(str(sub))}</tspan></text>')


def layer_pair_text(x, y, size=17, color="#63758b"):
    add(f'<text x="{x}" y="{y}" text-anchor="middle" fill="{color}" font-size="{size}" font-weight="600"><tspan font-style="italic">l</tspan><tspan baseline-shift="sub" font-size="70%">s</tspan><tspan baseline-shift="baseline">, </tspan><tspan font-style="italic">l</tspan><tspan baseline-shift="sub" font-size="70%">t</tspan></text>')


def path(d, *, stroke="#253952", width=3, end=True, dash=""):
    marker = ' marker-end="url(#arrow)"' if end else ""
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    add(f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"{marker}{dash_attr}/>')


COLORS = {
    "neutral": ("#eaf0f5", "#f9fbfd", "#afc1d1", "#8da5b9"),
    "source": ("#d7ecf2", "#f0fbff", "#5ba8be", "#287e9a"),
    "target": ("#fbe0e8", "#fff3f6", "#db809a", "#bd5678"),
    "predict": ("#eadcf7", "#f9f1ff", "#ad84d4", "#8455ae"),
    "align": ("#ffe9d7", "#fff7ed", "#e9a666", "#c7803a"),
    "embed": ("#dff1dd", "#f5fcf2", "#83bb85", "#4e9457"),
}


def prism(x, y, w, h=46, kind="neutral", label="", selected=False, dashed=False, font=21):
    front, top, side, edge = COLORS[kind]
    d = 13
    add(f'<g filter="url(#shadow)"><path d="M{x} {y} L{x+d} {y-d} L{x+w+d} {y-d} L{x+w} {y} Z" fill="{top}" stroke="{edge}" stroke-width="1.4"/>')
    add(f'<path d="M{x+w} {y} L{x+w+d} {y-d} L{x+w+d} {y+h-d} L{x+w} {y+h} Z" fill="{side}" stroke="{edge}" stroke-width="1.4"/>')
    dash_attr = ' stroke-dasharray="8 5"' if dashed else ""
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{front}" stroke="{edge}" stroke-width="2"{dash_attr}/></g>')
    if selected:
        dot = "#1685a8" if kind == "source" else "#cf476e"
        add(f'<circle cx="{x+22}" cy="{y+h/2}" r="8" fill="{dot}" stroke="white" stroke-width="2"/>')
    if label:
        center = x+w/2+8 if selected else x+w/2
        if label.startswith("l_"):
            layer_text(center, y+h/2+font/3-2, label[2:], font, "#182a41")
        else:
            text(center, y+h/2+font/3, label, font, "#182a41", 700)


def photo(x, y, key, *, label=""):
    add(f'<rect x="{x-3}" y="{y-3}" width="78" height="70" rx="9" fill="white" stroke="#bdccda" stroke-width="1.4"/>')
    add(f'<svg x="{x}" y="{y}" width="72" height="64" viewBox="0 0 192 192" preserveAspectRatio="xMidYMid slice"><image href="{PHOTOS[key]}" width="192" height="192"/></svg>')
    if label:
        text(x+36, y+84, label, 16, "#536782", 600)


def tower(x, title, highlights, *, dashed=False, bottom_key="student", bottom_label=""):
    text(x+83, 109, title, 22, "#273b56", 700)
    photo(x+47, 120, "clean")
    add(f'<path d="M{x+83} 196 V544" stroke="#c9d7e2" stroke-width="2.3" stroke-dasharray="4 5"/>')
    for i, y in enumerate((202, 276, 350, 424, 498)):
        kind = highlights.get(i, "neutral")
        name = {"source": "l_s", "target": "l_t"}.get(kind, "")
        prism(x, y, 166, 46, kind, name, selected=bool(name), dashed=dashed and bool(name), font=22)
    photo(x+47, 584, bottom_key, label=bottom_label)


def panel(x, w, title, subtitle, accent, dark=False):
    add(f'<rect x="{x}" y="16" width="{w}" height="686" rx="20" fill="#ffffff" stroke="#d8e2eb" stroke-width="1.8"/>')
    add(f'<path d="M{x+20} 16 H{x+w-20} Q{x+w} 16 {x+w} 36 V78 H{x} V36 Q{x} 16 {x+20} 16 Z" fill="{accent}"/>')
    text(x+w/2, 48, title, 31, "#ffffff", 800)
    text(x+w/2, 70, subtitle, 17, "#d8e7f0", 550)


add('<svg xmlns="http://www.w3.org/2000/svg" width="2200" height="830" viewBox="0 0 2200 830" font-family="Verdana,Arial,sans-serif">')
add('<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8.5" refY="5" orient="auto" markerUnits="userSpaceOnUse"><path d="M0 0 L10 5 L0 10 Z" fill="#253952"/></marker><filter id="shadow" x="-15%" y="-35%" width="140%" height="180%"><feDropShadow dx="3" dy="5" stdDeviation="3" flood-color="#273b56" flood-opacity="0.16"/></filter></defs>')
add('<rect width="2200" height="830" fill="#f4f7f9"/>')

panel(18, 744, "01  SRA", "EMA teacher across timesteps", "#1c4965")
panel(780, 572, "02  LayerSync", "One selected internal pair", "#1c4965")
panel(1370, 812, "03  LARA (ours)", "Shared predictor across sampled pairs", "#9a315e")

# SRA
tower(82, "Student (online)", {3:"source"}, bottom_label="t")
tower(565, "EMA teacher", {1:"target"}, bottom_key="ema", bottom_label="t′")
prism(337, 424, 162, 47, "predict", "Projection", font=22)
prism(337, 276, 162, 47, "align", "Align", font=22)
path("M262 447 H330")
path("M418 410 V329")
path("M558 299 H517")
text(410, 665, "t > t′", 17, "#63758b", 600)
add('<g transform="translate(699 125)"><path d="M4 17 v-8 a7 7 0 0 1 14 0 v8" fill="none" stroke="#4a667d" stroke-width="4"/><rect y="16" width="22" height="19" rx="3" fill="#4a667d"/><circle cx="11" cy="25" r="2" fill="white"/></g>')

# LayerSync
tower(817, "Student (online)", {1:"target",3:"source"})
prism(1108, 350, 173, 52, "align", "Align", font=22)
path("M1000 299 H1194 V333")
path("M1000 447 H1050 V376 H1102")

# LARA
tower(1408, "Student (online)", {1:"target",3:"source"}, dashed=True)
prism(1650, 276, 160, 47, "align", "Align", font=22)
prism(1650, 424, 160, 47, "predict", "Predictor", font=22)
prism(1668, 522, 124, 37, "embed", "Layer emb.", font=17)
path("M1591 299 H1643")
path("M1591 447 H1643")
path("M1730 410 V329")
path("M1730 508 V477")
layer_pair_text(1730, 589)

# Sampled-pair inset
add('<rect x="1843" y="200" width="310" height="319" rx="14" fill="#fdf8fa" stroke="#dfc3d0" stroke-width="1.5"/>')
text(1998, 231, "Random layer pairs", 21, "#7b2d50", 750)
text(1998, 253, "examples across steps", 17, "#66798e", 500)
for j, (src, dst) in enumerate(((2,7),(4,10),(6,9))):
    y = 293 + 74*j
    text(1998, y-24, f"Step {j+1}", 18, "#66798e", 650)
    prism(1869, y, 91, 25, "source", f"l_{src}", dashed=True, font=16)
    prism(2043, y, 91, 25, "target", f"l_{dst}", dashed=True, font=16)
    path(f"M1977 {y+12} H2034", width=2.1)
text(1998, 505, "⋯", 24, "#66798e", 700)

# Equal-width legend cells keep each label clear of the preceding 3D block.
add('<rect x="18" y="717" width="2164" height="95" rx="16" fill="#ffffff" stroke="#d8e2eb" stroke-width="1.7"/>')
legend = [("neutral","Transformer block"),("source","Source layer"),("target","Target layer"),("source","Sampled pair"),("predict","Projection / Predictor"),("align","Alignment"),("lock","EMA teacher")]
cell_width = 2164 / len(legend)
for index, (kind, label) in enumerate(legend):
    cx = 18 + cell_width * (index + 0.5)
    if index:
        separator_x = 18 + cell_width * index
        add(f'<path d="M{separator_x} 734 V796" stroke="#e8eef3" stroke-width="1.3"/>')
    if kind == "lock":
        add(f'<g transform="translate({cx-11} 735)"><path d="M4 17 v-8 a7 7 0 0 1 14 0 v8" fill="none" stroke="#4a667d" stroke-width="4"/><rect y="16" width="22" height="19" rx="3" fill="#4a667d"/><circle cx="11" cy="25" r="2" fill="white"/></g>')
    else:
        prism(cx-36, 748, 72, 27, kind, dashed=label=="Sampled pair")
    text(cx, 799, label, 20, "#263951", 650)
add('</svg>')

OUT.write_text("\n".join(svg), encoding="utf-8")
print(OUT)
