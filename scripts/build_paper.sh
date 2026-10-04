#!/usr/bin/env bash
set -euo pipefail

project_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$project_dir"

# Each document imports labels from the other's .aux file. Build both in
# sequence so a clean checkout resolves cross-document references too.
for document in supplementary main supplementary main; do
    tectonic --synctex --keep-logs --keep-intermediates "$document.tex"
done

if grep -Eq 'Reference .+ undefined|There were undefined references' main.log supplementary.log; then
    echo 'Unresolved LaTeX references remain in main.log or supplementary.log.' >&2
    exit 1
fi
