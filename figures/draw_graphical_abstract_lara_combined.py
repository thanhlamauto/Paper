"""Extend Fig. 1's LARA overview with its training losses, without predictor detail."""
from __future__ import annotations

import base64
from pathlib import Path
from xml.sax.saxutils import escape

from figure_typography import embedded_font_css, font_weight, with_text_shadow

HERE = Path(__file__).resolve().parent
OUT = HERE / "graphical_abstract_lara_combined.svg"
WIDTH, HEIGHT = 3400, 1640
INK = "#253952"
MUTED = "#536782"
COLORS = {
    "neutral": ("#eaf0f5", "#f9fbfd", "#afc1d1", "#8da5b9"),
    "source": ("#d7ecf2", "#f0fbff", "#5ba8be", "#287e9a"),
    "target": ("#fbe0e8", "#fff3f6", "#db809a", "#bd5678"),
    "predict": ("#eadcf7", "#f9f1ff", "#ad84d4", "#8455ae"),
    "align": ("#ffe9d7", "#fff7ed", "#e9a666", "#c7803a"),
    "embed": ("#dff1dd", "#f5fcf2", "#83bb85", "#4e9457"),
}
parts: list[str] = []


def add(markup: str) -> None:
    parts.append(with_text_shadow(markup))


def text(x, y, value, size=34, color=INK, weight=400, anchor="middle"):
    add(
        f'<text x="{x}" y="{y}" text-anchor="{anchor}" fill="{color}" '
        f'font-size="{size}" font-weight="{font_weight(weight)}">{escape(value)}</text>'
    )


def math(x, y, base, sub="", size=50, *, hat=False, stopped=False):
    if hat and base == "A":
        base = "Â"
    prefix, suffix = ("sg(", ")") if stopped else ("", "")
    add(
        f'<text x="{x}" y="{y}" text-anchor="middle" fill="{INK}" '
        f'font-size="{size}" font-weight="700">{prefix}'
        f'<tspan font-style="italic">{escape(base)}</tspan>'
        f'<tspan baseline-shift="sub" font-size="70%">{escape(sub)}</tspan>'
        f'<tspan baseline-shift="baseline">{suffix}</tspan></text>'
    )


def prism(x, y, width, height, kind="neutral", label="", *, size=36,
          selected=False, dashed=False):
    """The same faces, dots, edge colors and shadows as Fig. 1."""
    front, top, side, edge = COLORS[kind]
    depth = 14
    dash = ' stroke-dasharray="10 7"' if dashed else ""
    add(
        f'<g filter="url(#block-shadow)">'
        f'<path d="M{x} {y} l{depth} -{depth} h{width} l-{depth} {depth} Z" '
        f'fill="{top}" stroke="{edge}" stroke-width="1.6"/>'
        f'<path d="M{x+width} {y} l{depth} -{depth} v{height} l-{depth} {depth} Z" '
        f'fill="{side}" stroke="{edge}" stroke-width="1.6"/>'
        f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="5" '
        f'fill="{front}" stroke="{edge}" stroke-width="2.2"{dash}/></g>'
    )
    if selected:
        dot = "#1685a8" if kind == "source" else "#cf476e"
        add(f'<circle cx="{x+35}" cy="{y+height/2}" r="11" '
            f'fill="{dot}" stroke="white" stroke-width="2.2"/>')
    if label:
        text(x+width/2, y+height/2+size/3, label, size, weight=700)


def line(path, *, color=INK, arrow=True, dashed=False, width=3.6):
    marker = ' marker-end="url(#arrow)"' if arrow else ""
    dash = ' stroke-dasharray="9 7"' if dashed else ""
    add(f'<path d="{path}" fill="none" stroke="{color}" stroke-width="{width}" '
        f'stroke-linecap="round" stroke-linejoin="round"{marker}{dash}/>')


def photo(x, y, filename, width=130, height=115):
    uri = "data:image/png;base64," + base64.b64encode((HERE/filename).read_bytes()).decode()
    add(f'<rect x="{x-4}" y="{y-4}" width="{width+8}" height="{height+8}" '
        'rx="10" fill="white" stroke="#bdccda" stroke-width="1.6"/>')
    add(f'<svg x="{x}" y="{y}" width="{width}" height="{height}" '
        'viewBox="0 0 192 192" preserveAspectRatio="xMidYMid slice">'
        f'<image href="{uri}" width="192" height="192"/></svg>')


add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
    f'viewBox="0 0 {WIDTH} {HEIGHT}" font-family="Nimbus Roman,Times New Roman,Times,serif">')
add(embedded_font_css())
add('<defs><marker id="arrow" markerWidth="14" markerHeight="14" refX="12" refY="7" '
    'orient="auto" markerUnits="userSpaceOnUse"><path d="M0 0 L14 7 L0 14 Z" '
    f'fill="{INK}"/></marker>'
    '<filter id="block-shadow" x="-15%" y="-35%" width="140%" height="180%">'
    '<feDropShadow dx="3" dy="5" stdDeviation="3" flood-color="#273b56" '
    'flood-opacity="0.16"/></filter></defs>')
add(f'<rect width="{WIDTH}" height="{HEIGHT}" fill="white"/>')
add(f'<rect x="24" y="24" width="3352" height="{HEIGHT-48}" rx="26" '
    'fill="#fafafa" stroke="#505050" stroke-width="4"/>')
text(75, 102, "LARA: Layer-Aware Representation Alignment", 61, "#111111", 700, "start")
text(77, 151, "One shared predictor across randomly sampled layer pairs", 32, "#454545", 400, "start")
line("M75 181 H3325", color="#606060", arrow=False, width=1.8)

# Raise the LARA overview to sit directly beneath the main heading.
add('<g transform="translate(0 -220)">')

# The three LARA objectives share one boundary.
add('<rect x="650" y="510" width="2650" height="1230" rx="24" '
    'fill="#fffcfd" stroke="#505050" stroke-width="3"/>')
add('<rect x="2730" y="480" width="510" height="60" rx="10" fill="#fafafa"/>')
text(2985, 526, "LARA objectives", 42, "#111111", 700)
line("M1870 552 V1694", color="#d4ccd1", arrow=False, width=1.8)
line("M1910 1130 H3260", color="#d4ccd1", arrow=False, width=1.8)

# Fig. 1's online backbone and sampled source/target retain their visual identity.
text(350, 585, "Diffusion Transformer", 37, weight=700)
line("M155 640 H135 V1430 H155", color="#8da5b9", arrow=False, width=2.4)
add(f'<text x="95" y="1035" text-anchor="middle" fill="{MUTED}" '
    'font-size="29" font-weight="400" transform="rotate(-90 95 1035)">'
    'Transformer blocks</text>')
line("M350 633 V1430", color="#b5c6d4", arrow=False, dashed=True, width=2.8)
for y, kind, sub in ((640, "neutral", ""), (815, "target", "b"),
                     (990, "neutral", ""), (1165, "source", "a"),
                     (1340, "neutral", "")):
    prism(180, y, 340, 90, kind, selected=bool(sub), dashed=bool(sub))
    if sub:
        math(363, y+63, "A", sub, 55)
text(350, 791, "Target layer b", 29, "#96506b")
text(350, 1141, "Source layer a", 29, "#287e9a")
photo(285, 1535, "example_dog_noisy_student.png")
add(f'<text x="350" y="1705" text-anchor="middle" fill="{INK}" '
    'font-size="34" font-weight="400">Noisy input'
    '<tspan dx="10" font-style="italic">x</tspan>'
    '<tspan baseline-shift="sub" font-size="70%">t</tspan></text>')
line("M350 1515 V1450")

# Prediction is the original source -> predictor -> alignment branch of Fig. 1.
text(710, 585, "01  Prediction", 43, "#111111", 700, "start")
text(710, 635, "1 random pair (a, b) per training iteration", 33, "#7b2d50", 700, "start")
text(1110, 785, "Match the target", 32, MUTED)
prism(900, 815, 420, 90, "align")
math(1110, 879, "L", "pred", 56)
prism(900, 1165, 420, 90, "predict", "Shared predictor Gψ", size=40)
prism(950, 1340, 320, 80, "embed", "Time + layer emb.", size=33)
line("M548 860 H882")
text(710, 830, "sg", 31, "#96506b", 700)
line("M548 1210 H882")
line("M1110 1135 V925")
math(1218, 1053, "A", "a→b", 39, hat=True)
line("M1110 1310 V1275")
text(1110, 1465, "Condition on timestep and layer depths", 29, MUTED)

# Keep Fig. 1's random-pair inset: each row is a different training iteration.
add('<rect x="1455" y="790" width="355" height="650" rx="18" '
    'fill="#fdf8fa" stroke="#dfc3d0" stroke-width="1.8"/>')
text(1632, 845, "Random layer pairs", 31, "#7b2d50", 700)
text(1632, 885, "examples across iterations", 25, MUTED)
for iteration, source, target in ((1, 2, 7), (2, 4, 10), (3, 6, 9)):
    y = 970 + (iteration-1)*155
    text(1632, y-29, f"Iteration {iteration}", 28, MUTED, 700)
    prism(1495, y, 100, 47, "source", dashed=True)
    prism(1680, y, 100, 47, "target", dashed=True)
    math(1545, y+33, "A", str(source), 30)
    math(1730, y+33, "A", str(target), 30)
    line(f"M1624 {y+23.5} H1662", width=3)
text(1632, 1409, "…", 38, MUTED, 700)

# Direct prediction agrees with an EMA continuation of the cached a -> b state.
text(1920, 585, "02  Transition consistency", 43, "#111111", 700, "start")
text(3250, 585, "a < b < c", 34, MUTED, 400, "end")
text(1920, 635, "Predictor-only update", 31, MUTED, 400, "start")
text(2062, 680, "Detached source", 29, MUTED)
prism(1945, 720, 235, 90, "source")
math(2062, 783, "A", "a", 43, stopped=True)
text(2512, 680, "Online prediction", 29, MUTED)
prism(2290, 720, 445, 90, "predict", "Online: a → c", size=39)
line("M2210 765 H2272")
prism(1945, 930, 235, 90, "target")
math(2062, 993, "A", "a→b", 45, hat=True)
text(2062, 900, "Cached prediction", 29, MUTED)
prism(2290, 930, 445, 90, "predict", "EMA: b → c", size=39)
line("M2512 830 V898", dashed=True, width=2.6)
text(2548, 872, "EMA update", 28, MUTED, 400, "start")
line("M2210 975 H2272")
text(2240, 945, "sg", 29, "#8455ae", 700)
prism(2950, 825, 280, 105, "align")
math(3090, 895, "L", "cons", 56)
line("M2765 765 H2835 V860 H2932")
line("M2765 975 H2870 V900 H2932")
text(2850, 1030, "Target (sg)", 29, "#8455ae", 700)

# Redundancy uses an independently sampled layer pair, once per iteration.
text(1920, 1205, "03  Redundancy", 43, "#111111", 700, "start")
text(1920, 1256, "1 random pair (i, j) per training iteration", 33, "#7b2d50", 700, "start")
text(1920, 1300, "Sampled independently of (a, b)", 30, MUTED, 400, "start")
add('<rect x="1980" y="1340" width="430" height="300" rx="18" fill="#fcfdff" '
    'stroke="#9eafbf" stroke-width="1.8" stroke-dasharray="10 8"/>')
prism(2050, 1380, 270, 85, "source", dashed=True)
math(2185, 1440, "A", "i", 52)
prism(2050, 1530, 270, 85, "target", dashed=True)
math(2185, 1590, "A", "j", 52)
prism(2950, 1435, 280, 105, "align")
math(3090, 1505, "L", "div", 56)
line("M2350 1422.5 H2800 V1470 H2932")
line("M2350 1572.5 H2870 V1510 H2932")

add("</g>")
text(77, 1585, "sg: stop-gradient", 29, MUTED, 400, "start")
text(3325, 1585, "EMA: moving-average predictor", 29, MUTED, 400, "end")
add("</svg>")
OUT.write_text("\n".join(parts), encoding="utf-8")
print(OUT)
