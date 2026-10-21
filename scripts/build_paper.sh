#!/usr/bin/env bash
set -euo pipefail

project_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$project_dir"

# Bootstrap both .aux files, then rebuild until references between the PDFs settle.
# xr-hyper imports only labels; each PDF keeps its own BibTeX reference list.
previous_aux_state=''
references_stable=false
for pass in 1 2 3 4; do
    echo "Building main and supplementary (round $pass)..."
    tectonic --synctex --keep-logs --keep-intermediates main.tex
    tectonic --synctex --keep-logs --keep-intermediates supplementary.tex

    current_aux_state=$(python3 -c 'import hashlib; from pathlib import Path; print(hashlib.sha256(Path("main.aux").read_bytes()+Path("supplementary.aux").read_bytes()).hexdigest())')
    if [[ "$current_aux_state" == "$previous_aux_state" ]]; then
        references_stable=true
        break
    fi
    previous_aux_state=$current_aux_state
done

if [[ "$references_stable" != true ]]; then
    echo 'Cross-document references did not stabilize after four build rounds.' >&2
    exit 1
fi

for document in main supplementary; do
    if grep -Eq 'Reference .+ undefined|Citation .+ undefined|There were undefined (references|citations)|LABELS NOT IMPORTED|There were multiply-defined labels' "$document.log"; then
        echo "Unresolved or duplicate LaTeX references/citations remain in $document.log." >&2
        exit 1
    fi
done

mkdir -p output/pdf
cp main.pdf supplementary.pdf output/pdf/
echo 'Built output/pdf/main.pdf and output/pdf/supplementary.pdf.'
