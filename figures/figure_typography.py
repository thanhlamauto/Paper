"""Shared ICLR-style Times typography and subtle shadows for LARA diagrams."""

import base64
import re
from pathlib import Path

FONT_DIR = Path(__file__).resolve().parent / "fonts" / "nimbus-roman"


def font_weight(weight):
    """Use installed font weights; avoid synthesized extra-bold strokes."""
    return 400 if weight <= 550 else 700


def embedded_font_css():
    """Keep SVGs portable; PDF/PNG rendering uses the bundled fontconfig file."""
    faces = []
    for weight, style, filename in (
        (400, "normal", "Regular"), (700, "normal", "Bold"),
        (400, "italic", "Italic"), (700, "italic", "BoldItalic"),
    ):
        data = base64.b64encode((FONT_DIR / f"NimbusRoman-{filename}.otf").read_bytes()).decode()
        faces.append(
            '@font-face{font-family:"Nimbus Roman";'
            f'font-style:{style};font-weight:{weight};'
            f'src:url("data:font/otf;base64,{data}") format("opentype");}}'
        )
    faces.append('text{font-family:"Nimbus Roman","Times New Roman",Times,serif;font-kerning:normal;}')
    return ('<style type="text/css">' + '\n'.join(faces) + '</style>'
            '<defs><filter id="text-shadow" x="-15%" y="-40%" '
            'width="140%" height="190%" color-interpolation-filters="sRGB">'
            '<feGaussianBlur stdDeviation="0.45"/></filter></defs>')


def with_text_shadow(markup):
    """Blur only an offset shadow copy, keeping foreground PDF text vector."""
    if not markup.startswith('<text '):
        return markup
    markup = re.sub(r'font-weight="(\d+)"',
                    lambda m: f'font-weight="{font_weight(int(m[1]))}"', markup)
    size = float(re.search(r'font-size="([\d.]+)"', markup)[1])
    dx, dy = min(1.5, size * 0.025), min(2.0, size * 0.035)
    shadow = re.sub(r'\sfill="[^"]*"', '', markup)
    return (f'<g aria-hidden="true" fill="#17293f" opacity="0.16" '
            f'transform="translate({dx:.3f} {dy:.3f})" '
            f'filter="url(#text-shadow)">{shadow}</g>' + markup)
