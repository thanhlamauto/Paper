"""Build Figure 7 from the supplied PCA comparison grid.

The selected L1 -> L11 transition is the long-range pair (gap >= 8)
with the largest mean displayed-image similarity gain over the source
among pairs with a visually detailed target map and consistent
predictor/target similarity at every sampled t.
These JPEG correlations are only a reproducible visual selection aid;
they are not representation metrics reported in the paper.
"""

from pathlib import Path
import subprocess
import tempfile

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "figures" / "pca_comparison_grid.pdf"
OUTPUT = ROOT / "figures" / "predictor_output_behavior.pdf"
PAIR = (1, 11)
TIMESTEPS_DESCENDING = (0.9, 0.7, 0.5, 0.3, 0.1)
ROW_STARTS = (452, 632, 811, 990, 1170)
TILE_SIZE = 142


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
    fig = plt.figure(figsize=(9.6, 5.4), facecolor="white")
    axes = fig.subplots(3, 5, gridspec_kw={
        "left": 0.19, "right": 0.99, "bottom": 0.025, "top": 0.80,
        "wspace": 0.065, "hspace": 0.065,
    })
    labels = (
        rf"Source $A_{{{PAIR[0]}}}^{{t}}$",
        rf"Prediction $\widehat{{A}}_{{{PAIR[0]}\to{PAIR[1]}}}^{{t}}$",
        rf"Target $A_{{{PAIR[1]}}}^{{t}}$",
    )
    for row_index, label in enumerate(labels):
        fig.text(0.173, 0.667 - row_index * 0.258, label,
                 ha="right", va="center", fontsize=15, color="#262626")
    for column_index, t in enumerate(reversed(TIMESTEPS_DESCENDING)):
        center = (axes[0, column_index].get_position().x0
                  + axes[0, column_index].get_position().x1) / 2
        fig.text(center, 0.835, rf"$t={t:.1f}$", ha="center", va="center", fontsize=15)
    fig.text(0.19, 0.95, rf"$L_{{{PAIR[0]}}}\rightarrow L_{{{PAIR[1]}}}$", fontsize=16,
             ha="left", va="center", fontweight="bold")
    fig.text(0.58, 0.95, "Increasing $t$: noise $\\rightarrow$ image",
             fontsize=14, ha="center", va="center")
    fig.add_artist(plt.annotate("", xy=(0.97, 0.95), xytext=(0.79, 0.95),
                                xycoords="figure fraction", textcoords="figure fraction",
                                arrowprops={"arrowstyle": "->", "lw": 1.6, "color": "#444444"}))
    for column_index, triplet in enumerate(rows):
        for row_index, panel in enumerate(triplet):
            axis = axes[row_index, column_index]
            axis.imshow(panel, interpolation="nearest")
            axis.set_axis_off()
    fig.savefig(OUTPUT, dpi=300, bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)
    print(OUTPUT)


if __name__ == "__main__":
    main()
