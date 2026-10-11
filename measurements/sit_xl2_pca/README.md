# SiT-XL/2 PCA visualization

This directory records the real features used in Figure 2(a). It uses the official
pretrained SiT-XL/2 256px checkpoint with the baseline implementation and PCA code
from [SRA's pca-vis](https://github.com/vvvvvjdy/SRA/tree/main/pca-vis), pinned to
revision `1723f85069408f6df7d11db35549575c97bfa5b2`.
The upstream MIT license is included in `source/LICENSE`. The VAE revision is
pinned, and subsequent runs verify the checkpoint's SHA-256 against this run.

The goose input is the exact 142 × 142 thumbnail embedded in the previous
`figures/PCA.svg`, resized to 256 × 256 by SRA's input transform. Its original
pixels are preserved in `input_goose.png`. The ImageNet class index is 99.

## Recompute on Modal

```sh
modal run --profile thanhlamtba31 scripts/modal_sit_pca.py
```

Models are cached on a dedicated Modal volume. Downloading uses a CPU function;
feature extraction uses one L4 GPU. The app stops after its local entrypoint
finishes. No training is performed.

## Protocol

- A frozen official SiT-XL/2 processes 256 × 256 pixels through the SD VAE.
- One seeded VAE posterior sample and one Gaussian noise tensor are shared across
  all rows. Seed: 20261011.
- The linear path is `x_t = t*x_0 + (1-t)*epsilon`: `t` increases from noise to
  image. Rows are `t = 0.30, 0.50, 0.70, 0.90`, corresponding to noise coefficients
  `0.70, 0.50, 0.30, 0.10`.
- Layers 1, 3, 8, 13, 18, 23, and 28 are indexed from one, after their blocks.
- The unmodified SRA baseline applies spatial min-max normalization per channel.
- Unmodified `pcav.pca_v` fits three components independently in each cell and
  min-max scales each component into RGB. Each cell has its own PCA basis; equal
  RGB colors across different cells need not indicate the same feature direction.
- This corrects SRA's legacy baseline timestep input and shares random draws
  across rows. Both changes are documented in `metadata.json`.

`metadata.json` records checkpoint/input hashes, exact revisions, package versions,
precision, the device, and run time. `features_and_pca.npz` contains normalized
tokens, RGB maps, the sampled image latent, and the shared noise. `maps/` contains
the 28 exact 16 × 16 visualizations, and `vae_reconstruction.png` is a sanity check
of the input encoding.

## Render in the paper style

```sh
python figures/draw_pca_depth_time.py
FONTCONFIG_FILE="$PWD/figures/fonts/fonts.conf" PANGOCAIRO_BACKEND=fc \
  rsvg-convert -f pdf -o figures/PCA.pdf figures/PCA.svg
FONTCONFIG_FILE="$PWD/figures/fonts/fonts.conf" PANGOCAIRO_BACKEND=fc \
  rsvg-convert -f png -w 7200 -h 4260 -o figures/PCA.png figures/PCA.svg
```

Rendering requires NumPy and Pillow. Each RGB patch is a vector square in the SVG
and PDF, preserving PCA colors without interpolation. Typography, navy headers,
prism labels, and subtle shadows use the same design as Figures 1 and 3.
