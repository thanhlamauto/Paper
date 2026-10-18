#!/usr/bin/env bash
# Rebuild the three LARA diagrams with the bundled ICLR-style Times fonts.
set -euo pipefail

project_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$project_dir"
export FONTCONFIG_FILE="$project_dir/figures/fonts/fonts.conf"
# Use the bundled font files on macOS as well as Linux, without a system install.
export PANGOCAIRO_BACKEND=fc
mkdir -p output/pdf

python3 figures/draw_fig1_v2.py
python3 figures/draw_predictor_arch.py
python3 figures/draw_graphical_abstract_lara_combined.py

render_figure() {
    local figure_name=$1 output_pdf=$2 image_width=$3 image_height=$4
    rsvg-convert -f pdf -o "$output_pdf" "figures/$figure_name.svg"
    rsvg-convert -f png -w "$image_width" -h "$image_height" \
        -o "figures/$figure_name.png" "figures/$figure_name.svg"
    if command -v sips >/dev/null 2>&1; then
        sips -s dpiWidth 300 -s dpiHeight 300 "figures/$figure_name.png" >/dev/null
    fi
}

render_figure fig1_v2 figures/fig1_v2.pdf 6600 2490
render_figure predictor_arch_redrawn figures/predictor_arch_redrawn.pdf 7200 3780
render_figure graphical_abstract_lara_combined output/pdf/graphical_abstract_lara_combined.pdf 10200 4920
