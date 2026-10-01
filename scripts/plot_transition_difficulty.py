"""Render Figure 2(b,c) from Supplementary Table 11's reported values.

Run: uv run --with matplotlib python scripts/plot_transition_difficulty.py
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
QUARTILES = ["0–25%", "25–50%", "50–75%", "75–100%"]
PANELS = [
    ("(b) Transition error by layer gap", "Normalized layer-gap quartile",
     [0.025, 0.039, 0.057, 0.152], "#286A99"),
    ("(c) Transition error by source depth", "Normalized source-position quartile",
     [0.060, 0.023, 0.027, 0.110], "#A65D27"),
]

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 8,
    "axes.titlesize": 9, "axes.labelsize": 8,
    "xtick.labelsize": 7.5, "ytick.labelsize": 7.5,
    "pdf.fonttype": 42, "ps.fonttype": 42,
})
fig, axes = plt.subplots(1, 2, figsize=(7.1, 1.95), layout="constrained")
for ax, (title, xlabel, values, color) in zip(axes, PANELS):
    ax.plot(range(4), values, color=color, marker="o", linewidth=1.5,
            markersize=4, zorder=3)
    for x, value in enumerate(values):
        ax.annotate(f"{value:.3f}", (x, value), xytext=(0, 6),
                    textcoords="offset points", ha="center", fontsize=8)
    ax.set(xlabel=xlabel, ylabel="Transition error ↓",
           ylim=(0, 0.18), xlim=(-0.3, 3.3))
    ax.set_xticks(range(4), QUARTILES)
    ax.set_yticks([0, 0.05, 0.10, 0.15], ["0.00", "0.05", "0.10", "0.15"])
    ax.grid(axis="y", color="#DEDEDE", linewidth=0.5, zorder=0)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(length=3, color="#777777")
    ax.set_title(title, fontweight="bold", loc="left", pad=8)
fig.savefig(ROOT / "figures/transition_difficulty.pdf")
plt.close(fig)
