"""Match Figure 8's printed titles to Figure 4 without redrawing plot data.

Run: uv run --python 3.12 --with pymupdf --with matplotlib python scripts/style_representation_titles.py
The supplied vector PDFs remain the sources. Only their original title text is
removed; curves, markers, annotations, axes, legends, and font sizes are retained.
"""

from pathlib import Path

import pymupdf as fitz
from matplotlib import font_manager

ROOT = Path(__file__).resolve().parents[1]
FONT_PATH = str(font_manager.findfont(
    font_manager.FontProperties(family="DejaVu Sans", weight="bold")
))
FONT = fitz.Font(fontfile=FONT_PATH)
# Each 648 pt source is printed at about 0.258 scale in its 0.32-textwidth
# panel. A 37 pt source title therefore prints at about 9.5 pt, like Fig. 4.
TITLE_SIZE = 37
TOP_PADDING = 24
PANELS = (
    ("classification", "Classification on Tiny ImageNet", "Tiny ImageNet classification"),
    ("segmentation", "Semantic Segmentation on PASCAL VOC dataset", "PASCAL VOC segmentation"),
    ("alignment", "Alignment to DINOv2-g", "DINOv2-g alignment"),
)

for name, old_title, title in PANELS:
    source_path = ROOT / "figures" / f"representation_{name}.pdf"
    target_path = source_path.with_stem(f"representation_{name}_styled")
    with fitz.open(source_path) as source:
        page = source[0]
        matches = page.search_for(old_title)
        if len(matches) != 1:
            raise ValueError(f"Expected one title in {source_path}, found {len(matches)}")
        page.add_redact_annot(matches[0], fill=False)
        # Preserve vector graphics and images, including those under the text.
        page.apply_redactions(images=0, graphics=0, text=0)
        width, height = page.rect.width, page.rect.height
        with fitz.open() as output:
            result = output.new_page(width=width, height=height + TOP_PADDING)
            result.show_pdf_page(fitz.Rect(0, TOP_PADDING, width, height + TOP_PADDING), source, 0)
            result.insert_font(fontname="PlotTitle", fontfile=FONT_PATH)
            title_width = FONT.text_length(title, fontsize=TITLE_SIZE)
            if title_width > width - 40:
                raise ValueError(f"Title is too wide: {title}")
            result.insert_text(
                ((width - title_width) / 2, 36), title,
                fontname="PlotTitle", fontsize=TITLE_SIZE, color=(0, 0, 0),
            )
            output.subset_fonts()
            output.save(target_path, garbage=4, deflate=True)
    print(target_path)
