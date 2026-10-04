#!/usr/bin/env bash
set -euo pipefail

project_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$project_dir"

tectonic --synctex --keep-logs --keep-intermediates main.tex

if grep -Eq 'Reference .+ undefined|There were undefined references' main.log; then
    echo 'Unresolved LaTeX references remain in main.log.' >&2
    exit 1
fi
