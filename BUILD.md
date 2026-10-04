# IEEE Computer Society manuscript build

Build from the repository root with a LaTeX installation that includes IEEEtran, IEEEtranN, BibTeX, natbib, cleveref, and the packages named in `ieee_preamble.tex`.

The main paper and Supplementary are one document. Build only `main.tex`:

```sh
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

Alternatively, run `bash scripts/build_paper.sh` with Tectonic. The output is `main.pdf`, with Supplementary Material after the references. On Overleaf, select `main.tex` as the main file.
