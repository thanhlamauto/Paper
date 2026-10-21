#!/usr/bin/env bash
# Render measured PCA maps with bundled paper fonts.
set -euo pipefail
project_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$project_dir"
export FONTCONFIG_FILE="$project_dir/figures/fonts/fonts.conf"
export PANGOCAIRO_BACKEND=fc
pca_python=${PCA_PYTHON:-python3}
"$pca_python" figures/draw_pca_depth_time.py
rsvg-convert -f pdf -o figures/PCA.pdf figures/PCA.svg
# SVG shadows otherwise become 54 full-page raster/mask pairs in Cairo's PDF.
# Crop only their transparent padding; retain all vector text and PCA cells.
"$pca_python" scripts/optimize_pdf_alpha_images.py figures/PCA.pdf
rsvg-convert -f png -w 7200 -h 4260 -o figures/PCA.png figures/PCA.svg
if command -v sips >/dev/null 2>&1; then
    sips -s dpiWidth 300 -s dpiHeight 300 figures/PCA.png >/dev/null
fi
