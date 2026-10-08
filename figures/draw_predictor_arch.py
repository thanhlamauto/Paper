"""Nested, editable vector rendering of the LARA transition predictor."""

from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape


HERE = Path(__file__).resolve().parent
OUT = HERE / "predictor_arch_redrawn.svg"
items: list[str] = []


def put(s: str) -> None:
    items.append(s)


def label(x, y, s, size=24, color="#1a2940", weight=600, anchor="middle"):
    put(
        f'<text x="{x}" y="{y}" text-anchor="{anchor}" fill="{color}" '
        f'font-size="{size}" font-weight="{weight}">{escape(s)}</text>'
    )


def route(d, color="#253952", width=3.3, arrow=True, dash=""):
    marker = {
        "#253952": "arrow",
        "#c7803a": "arrowWarm",
        "#8da5b9": "arrowBlue",
        "#8455ae": "arrowPurple",
    }.get(color, "arrow")
    end = f' marker-end="url(#{marker})"' if arrow else ""
    pattern = f' stroke-dasharray="{dash}"' if dash else ""
    put(
        f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" '
        f'stroke-linecap="round" stroke-linejoin="round"{end}{pattern}/>'
    )


COLORS = {
    "neutral": ("#eaf0f5", "#f9fbfd", "#afc1d1", "#8da5b9"),
    "source": ("#d7ecf2", "#f0fbff", "#5ba8be", "#287e9a"),
    "target": ("#fbe0e8", "#fff3f6", "#db809a", "#bd5678"),
    "predict": ("#eadcf7", "#f9f1ff", "#ad84d4", "#8455ae"),
    "attention": ("#ffe9d7", "#fff7ed", "#e9a666", "#c7803a"),
    "linear": ("#dff1dd", "#f5fcf2", "#83bb85", "#4e9457"),
    "output": ("#eaf0f5", "#f9fbfd", "#afc1d1", "#8da5b9"),
}


def prism(x, y, w, h, kind, main, sub="", size=23, depth=13):
    front, top, side, edge = COLORS[kind]
    d = depth
    put(
        f'<g filter="url(#shadow)"><path d="M{x} {y} L{x+d} {y-d} '
        f'L{x+w+d} {y-d} L{x+w} {y} Z" fill="{top}" stroke="{edge}" '
        f'stroke-width="1.5"/>'
        f'<path d="M{x+w} {y} L{x+w+d} {y-d} L{x+w+d} {y+h-d} '
        f'L{x+w} {y+h} Z" fill="{side}" stroke="{edge}" stroke-width="1.5"/>'
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" '
        f'fill="{front}" stroke="{edge}" stroke-width="2"/></g>'
    )
    cx = x + w / 2
    if sub:
        label(cx, y + h / 2 - 3, main, size, weight=700)
        label(cx, y + h / 2 + 25, sub, size - 2, weight=550)
    else:
        label(cx, y + h / 2 + size / 3, main, size)


def sum_node(cx, cy, r=25, color="#253952"):
    put(
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="white" '
        f'stroke="{color}" stroke-width="3"/>'
    )
    route(f"M{cx-r+10} {cy} H{cx+r-10}", color, 3, arrow=False)
    route(f"M{cx} {cy-r+10} V{cy+r-10}", color, 3, arrow=False)


def panel(x, y, w, h, title, subtitle, accent, border):
    put(
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="20" '
        f'fill="#ffffff" stroke="{border}" stroke-width="2"/>'
    )
    put(
        f'<path d="M{x+20} {y} H{x+w-20} Q{x+w} {y} {x+w} {y+20} '
        f'V{y+70} H{x} V{y+20} Q{x} {y} {x+20} {y} Z" fill="{accent}"/>'
    )
    label(x+w/2, y+38, title, 30, "#ffffff", 800)
    if subtitle:
        label(x+w/2, y+61, subtitle, 17, "#d8e7f0", 550)


put('<svg xmlns="http://www.w3.org/2000/svg" width="2400" height="1260" viewBox="0 0 2400 1260" font-family="Verdana,Arial,sans-serif">')
put('<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8.5" refY="5" orient="auto" markerUnits="userSpaceOnUse"><path d="M0 0 L10 5 L0 10 Z" fill="#253952"/></marker><marker id="arrowWarm" markerWidth="10" markerHeight="10" refX="8.5" refY="5" orient="auto" markerUnits="userSpaceOnUse"><path d="M0 0 L10 5 L0 10 Z" fill="#c7803a"/></marker><marker id="arrowBlue" markerWidth="10" markerHeight="10" refX="8.5" refY="5" orient="auto" markerUnits="userSpaceOnUse"><path d="M0 0 L10 5 L0 10 Z" fill="#8da5b9"/></marker><marker id="arrowPurple" markerWidth="10" markerHeight="10" refX="8.5" refY="5" orient="auto" markerUnits="userSpaceOnUse"><path d="M0 0 L10 5 L0 10 Z" fill="#8455ae"/></marker><filter id="shadow" x="-15%" y="-35%" width="140%" height="180%"><feDropShadow dx="3" dy="5" stdDeviation="3" flood-color="#273b56" flood-opacity="0.16"/></filter></defs>')
put('<rect width="2400" height="1260" fill="#f4f7f9"/>')

# Match the overview figure: navy process headers, a magenta LARA header,
# and the same semantic colors for source, target, predictor and embeddings.
panel(28, 28, 930, 710, "01  Layer-aware conditioning", "timestep + source + target", "#1c4965", "#d8e2eb")
panel(978, 28, 1394, 710, "02  Conditioned spatial block", "ConvNeXt + periodic attention", "#1c4965", "#d8e2eb")
panel(28, 758, 2344, 474, "03  LARA predictor data path", "SiT-B/2 · 16 × 16 tokens", "#9a315e", "#d8e2eb")

# Layer-aware conditioning.
prism(86, 176, 275, 85, "neutral", "Timestep t", "backbone embed e_t", size=23)
prism(86, 303, 275, 85, "source", "Source layer a", "embedding e_a", size=23)
prism(86, 430, 275, 85, "target", "Target layer b", "embedding e_b", size=23)
put('<circle cx="108" cy="345" r="10" fill="#1685a8" stroke="white" stroke-width="2"/>')
put('<circle cx="108" cy="472" r="10" fill="#cf476e" stroke="white" stroke-width="2"/>')
route("M375 218 H425 L467 342", arrow=False)
route("M375 345 H460", arrow=False)
route("M375 472 H425 L467 353", arrow=False)
sum_node(495, 347, 28)
route("M527 347 H604")
prism(614, 305, 265, 85, "predict", "Condition vector", size=23)
route("M746 396 V455")
prism(625, 467, 245, 77, "predict", "AdaLN / FiLM", size=23)
put('<rect x="88" y="588" width="790" height="92" rx="14" fill="#f9f1ff" stroke="#d7c4e8" stroke-width="1.6"/>')
label(483, 626, "Depth-conditioned vector modulates all predictor blocks", 22, "#7b2d50", 700)
label(483, 657, "Target-layer activation is a stop-gradient reference", 18, "#63758b", 500)

# Detailed normal spatial block, bottom to top.
label(1355, 123, "NORMAL BLOCK", 20, "#60758c", 750)
prism(1222, 594, 270, 62, "neutral", "Input tokens", size=22)
prism(1222, 510, 270, 62, "neutral", "Layer norm", size=22)
prism(1222, 426, 270, 62, "predict", "Scale + shift 1", size=21)
prism(1222, 307, 270, 86, "neutral", "ConvNeXt block", size=22)
sum_node(1357, 258, 24)
prism(1222, 149, 270, 64, "neutral", "Normal output", size=22)
route("M1357 590 V578")
route("M1357 506 V494")
route("M1357 422 V399")
route("M1357 303 V288")
route("M1357 230 V219")
route("M1218 625 H1135 V258 H1327", color="#8da5b9", width=3, dash="8 7")
label(1055, 442, "residual", 17, "#63758b", 600)

# Every fourth block adds an attention stage.
label(2047, 123, "EVERY 4TH BLOCK", 20, "#c7803a", 750)
route("M1506 181 H1882", color="#c7803a", width=3.5)
prism(1891, 149, 270, 64, "neutral", "Normal output", size=22)
route("M2026 218 V230", color="#c7803a")
prism(1891, 239, 270, 62, "neutral", "Layer norm", size=22)
route("M2026 307 V319", color="#c7803a")
prism(1891, 328, 270, 62, "attention", "Scale + shift 2", size=21)
route("M2026 396 V408", color="#c7803a")
prism(1891, 417, 270, 70, "attention", "MHSA", size=23)
route("M2026 493 V505", color="#c7803a")
prism(1891, 514, 270, 62, "attention", "Output projection", size=21)
route("M2026 582 V591", color="#c7803a")
sum_node(2026, 620, 24, color="#c7803a")
route("M2026 647 V656", color="#c7803a")
prism(1891, 665, 270, 55, "neutral", "Conv + attn output", size=20)
route("M2175 181 H2250 V620 H2058", color="#c7803a", width=3, dash="8 7")
label(2306, 442, "residual", 17, "#c7803a", 600)

# One condition generates both channel-wise modulations.
prism(1573, 505, 232, 60, "predict", "Condition vector", size=20)
route("M1689 571 V581", color="#8455ae")
prism(1573, 590, 232, 60, "predict", "MLP → γ, β", size=20)
route("M1566 619 H1533 V457 H1506", color="#8455ae", width=2.8)
route("M1818 619 H1855 V359 H1883", color="#8455ae", width=2.8)
label(1550, 444, "γ1, β1", 16, "#8455ae", 650)
label(1840, 347, "γ2, β2", 16, "#8455ae", 650)

# Original SiT-B/2 data path and attention schedule.
prism(88, 925, 260, 110, "neutral", "Input x", "[B, 256, 768]", size=27)
prism(420, 925, 255, 110, "linear", "Linear", "+ reshape", size=26)
prism(765, 906, 460, 150, "predict", "Conditioned spatial blocks", "× 10", size=26, depth=18)
prism(1315, 925, 225, 110, "neutral", "Layer norm", size=25)
prism(1620, 925, 255, 110, "linear", "Linear", "+ reshape", size=26)
prism(1970, 925, 310, 110, "target", "Output y", "[B, 256, 768]", size=27)
route("M365 980 H411")
route("M692 980 H756")
route("M1247 980 H1306")
route("M1557 980 H1611")
route("M1892 980 H1961")
label(719, 1081, "[B, 256, 384]", 20, "#63758b", 650)
put('<rect x="799" y="1094" width="395" height="62" rx="12" fill="#f9f1ff" stroke="#d7c4e8" stroke-width="1.5"/>')
label(997, 1121, "Attention after blocks 4 and 8", 19, "#7b2d50", 700)
label(997, 1147, "same vector injected at each block", 16, "#63758b", 500)
label(1203, 1199, "Shared predictor Gψ maps source tokens to target-layer coordinates", 24, "#263951", 600)

put('</svg>')
OUT.write_text("\n".join(items), encoding="utf-8")
print(OUT)
