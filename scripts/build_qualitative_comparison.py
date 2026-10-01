"""Assemble a curated comparison without cropping or modifying source images.

Run: uv run --with matplotlib python scripts/build_qualitative_comparison.py
All selected quartets use protocol B and identical class/initial latent.
"""
import csv
import hashlib
import shutil
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "sit_images_for_selection 2"
OUT = ROOT / "figures/qualitative_comparison"
OUT.mkdir(parents=True, exist_ok=True)
METHODS = ["SiT", "SRA", "LayerSync", "LARA"]
SELECTION = [
    (26, 113, "Common newt", "Complete subject silhouette; visible tail and limbs."),
    (208, 113, "Labrador", "Clear eye and muzzle contours with a clean background."),
    (895, 10007, "Warplane", "Readable wing, fuselage and tail structure."),
    (473, 10007, "Can opener", "Visible cutting wheel and recognizable tool geometry."),
    (905, 113, "Window shade", "Regular vertical slats and a coherent window frame."),
    (750, 10007, "Quilt", "Distinct patchwork motifs and visible fabric folds."),
]
manifest = PACKAGE / "all_images.csv"
if not manifest.exists():
    manifest = OUT / "selected_images.csv"
with manifest.open() as f:
    reader = csv.DictReader(f)
    fields = [name for name in reader.fieldnames if name not in ("column", "selection_reason")]
    records = list(reader)
lookup = {(int(r["class_id"]), int(r["seed"]), r["method"]): r
          for r in records if r["archive_group"] == "B"}
selected = []
source_dir = OUT / "source_images"
source_dir.mkdir(exist_ok=True)

def image_path(record):
    original = PACKAGE / record["path"]
    return original if original.exists() else source_dir / Path(record["path"]).name

for col, (class_id, seed, name, reason) in enumerate(SELECTION, 1):
    group = [lookup[class_id, seed, method] for method in METHODS]
    assert len({r["initial_latent_sha256"] for r in group}) == 1
    assert len({(r["sampler"], r["cfg"], r["steps"], r["guidance_low"],
                 r["guidance_high"], r["vae"]) for r in group}) == 1
    for r in group:
        source = image_path(r)
        assert hashlib.sha256(source.read_bytes()).hexdigest() == r["image_sha256"]
        destination = source_dir / Path(r["path"]).name
        if source.resolve() != destination.resolve():
            shutil.copyfile(source, destination)
        selected.append(dict(column=col, selection_reason=reason,
                             **{name: r[name] for name in fields}))
with (OUT / "selected_images.csv").open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["column", "selection_reason", *fields], lineterminator="\n")
    writer.writeheader()
    writer.writerows(selected)
with (OUT / "selected_pairs.csv").open("w", newline="") as f:
    writer = csv.writer(f, lineterminator="\n")
    writer.writerow(["protocol", "class_id", "class_name", "seed", "selection_reason"])
    writer.writerows(("B", cid, name, seed, reason) for cid, seed, name, reason in SELECTION)

plt.rcParams.update({"font.family": "DejaVu Sans", "pdf.fonttype": 42, "ps.fonttype": 42})
# Image panels have equal square dimensions and preserve the full 256x256 view.
fig = plt.figure(figsize=(7.2, 5.15), facecolor="white")
left, right, top = 0.12, 0.01, 0.905
gap_x, gap_y = 0.006, 0.008
w = (1-left-right-5*gap_x)/6
h = w*7.2/5.15
for i, method in enumerate(METHODS):
    y = top - h - i*(h+gap_y)
    fig.text(left-0.013, y+h/2, method, ha="right", va="center",
             fontsize=8, fontweight="bold" if method == "LARA" else "normal",
             color="#237E74" if method == "LARA" else "#25313C")
    for j, (class_id, seed, name, _) in enumerate(SELECTION):
        ax = fig.add_axes([left+j*(w+gap_x), y, w, h])
        ax.imshow(mpimg.imread(image_path(lookup[class_id, seed, method])),
                  interpolation="none")
        ax.set_axis_off()
        if i == 0:
            ax.set_title(name+f"\nseed {seed}", fontsize=7, pad=5)
fig.text(left, 0.982, "Selected ImageNet comparisons", fontsize=10,
         fontweight="bold", va="top", color="#25313C")
fig.text(left, 0.026,
         "SiT-XL/2 · 256×256 · Euler ODE, 250 steps · CFG 1.8 · same class and initial latent per column\n"
         "Curated examples from protocol B; released checkpoints have different training budgets.",
         fontsize=6.5, color="#45515B", va="bottom", linespacing=1.5)
fig.savefig(OUT / "selected_comparison.pdf")
fig.savefig(OUT / "selected_comparison.png", dpi=240)
plt.close(fig)
print(f"Saved {len(selected)} verified images across {len(SELECTION)} selected quartets to {OUT}")
