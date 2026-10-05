"""Render Figure 2(b,c) from measured LARA-B 400k layer-pair errors.

Run: uv run --with matplotlib python scripts/plot_transition_difficulty.py
The CSV is produced by scripts/eval_transition_pairs.py on the held-out
49,920-image latent validation set. Pair choices were fixed before evaluation.
"""
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "measurements/lara_b_400k_transition_pairs/pairs.csv"
with DATA.open(newline="") as handle:
    rows = {(int(r["source"]), int(r["target"])): r
            for r in csv.DictReader(handle)}

PANELS = [
    ("(b) Source layer 3: increasing gap", ((3, 4), (3, 6), (3, 9), (3, 12)), "#286A99"),
    ("(c) Gap 2: increasing source depth", ((1, 3), (3, 5), (6, 8), (10, 12)), "#A65D27"),
]

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 8,
    "axes.titlesize": 9, "axes.labelsize": 8,
    "xtick.labelsize": 7.5, "ytick.labelsize": 7.5,
    "pdf.fonttype": 42, "ps.fonttype": 42,
})
fig, axes = plt.subplots(1, 2, figsize=(7.1, 2.05), layout="constrained")
for ax, (title, pairs, color) in zip(axes, PANELS):
    values = [float(rows[pair]["mean"]) for pair in pairs]
    ci95 = [1.96 * float(rows[pair]["se"]) for pair in pairs]
    ax.errorbar(range(4), values, yerr=ci95, color=color, marker="o",
                linewidth=1.5, markersize=4, capsize=2, zorder=3)
    for x, value in enumerate(values):
        ax.annotate(f"{value:.3f}", (x, value), xytext=(0, 6),
                    textcoords="offset points", ha="center", fontsize=8)
    ax.set(xlabel="Source $\\rightarrow$ target layer", ylabel="Direction error $\\downarrow$",
           ylim=(0, 0.085), xlim=(-0.3, 3.3))
    ax.set_xticks(range(4), [f"{a}$\\rightarrow${b}" for a, b in pairs])
    ax.set_yticks([0, 0.02, 0.04, 0.06, 0.08])
    ax.grid(axis="y", color="#DEDEDE", linewidth=0.5, zorder=0)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(length=3, color="#777777")
    ax.set_title(title, fontweight="bold", loc="left", pad=8)
fig.savefig(ROOT / "figures/transition_difficulty.pdf")
fig.savefig(ROOT / "figures/transition_difficulty.png", dpi=240)
plt.close(fig)
