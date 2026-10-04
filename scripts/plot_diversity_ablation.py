"""Reproduce the diversity ablation figure from supplied SVGs and reported metrics.

Run: uv run --with matplotlib python scripts/plot_diversity_ablation.py
The CSV transcribes the four-run results supplied by the author. SVG cell
colors are preserved exactly; no matrix values or color normalization are
inferred from the rendered colors. The 8x condition has metrics but no SVG.
"""
import csv
from pathlib import Path
import xml.etree.ElementTree as ET

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize

ROOT = Path(__file__).resolve().parents[1]
with (ROOT / "figures/diversity_ablation_metrics.csv").open() as f:
    rows = list(csv.DictReader(f))
colors = ["#687686", "#237E74", "#C08235", "#99506C"]
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 8,
    "axes.titlesize": 9, "axes.labelsize": 8,
    "xtick.labelsize": 7.5, "ytick.labelsize": 7.5,
    "pdf.fonttype": 42, "ps.fonttype": 42,
})
fig = plt.figure(figsize=(7.15, 2.4), layout="constrained")
gs = fig.add_gridspec(1, 3, wspace=0.05)
heatmap_axes = []
for i, (row, descriptor) in enumerate(zip(rows[:3], ["No diversity loss", "Best FID / sFID", ""])):
    ax = fig.add_subplot(gs[0, i])
    heatmap_axes.append(ax)
    lambda_div = float(row["lambda_div"])
    svg = ET.parse(ROOT / "rebuttal image" / row["heatmap"]).getroot()
    for cell in svg.iter("{http://www.w3.org/2000/svg}rect"):
        ax.add_patch(Rectangle((float(cell.attrib["x"]), float(cell.attrib["y"])),
                               float(cell.attrib["width"]), float(cell.attrib["height"]),
                               facecolor=cell.attrib["fill"], edgecolor="none"))
    ax.set(xlim=(0, 12), ylim=(12, 0), aspect="equal", xlabel="Layer", ylabel="Layer")
    ticks = [0.5, 3.5, 7.5, 11.5]
    ax.set_xticks(ticks, [1, 4, 8, 12])
    ax.set_yticks(ticks, [1, 4, 8, 12])
    ax.set_title(f"({chr(97+i)}) $\\lambda_{{\\mathrm{{div}}}}={lambda_div:g}$\n{descriptor}",
                 fontweight="bold", color=colors[i], pad=7)
    ax.tick_params(length=0)
    for spine in ax.spines.values():
        spine.set_color("#CFD5DA")

# The SVGs contain colors, not the original numeric normalization. Use a
# shared qualitative key rather than inventing numerical scale endpoints.
colorbar = fig.colorbar(
    ScalarMappable(norm=Normalize(0, 1), cmap="Blues"),
    ax=heatmap_axes, location="right", fraction=0.024, pad=0.02,
    shrink=0.74, aspect=22,
)
colorbar.set_ticks([0, 1], labels=["Low", "High"])
colorbar.set_label("Correlation", labelpad=3)
colorbar.ax.tick_params(length=0, pad=3)
colorbar.outline.set_edgecolor("#CFD5DA")
colorbar.outline.set_linewidth(0.5)

fig.savefig(ROOT / "figures/diversity_ablation.pdf")
plt.close(fig)
