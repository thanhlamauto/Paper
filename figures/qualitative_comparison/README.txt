Selected qualitative comparison

The PDF contains six manually selected class/seed quartets from protocol B
of the supplied sit_images_for_selection 2 package. The 24 original PNGs
are included in source_images, byte-for-byte unchanged; SHA256 hashes and
the original paths are retained in selected_images.csv.

Protocol B: SiT-XL/2, ImageNet 256x256, deterministic Euler ODE, 250 steps,
CFG 1.8, full-interval guidance over all four latent channels, common VAE.
Each quartet shares the same initial latent. Checkpoints have different
training budgets, as stated in the figure caption. These are curated examples.

Rebuild from the repository root:
  uv run --with matplotlib python scripts/build_qualitative_comparison.py

The script reads the original package when available and otherwise uses
the included selection manifest and source_images. The full candidate
package is not required to reproduce the comparison.
