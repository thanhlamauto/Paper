# IEEE Computer Society manuscript build

Build from the repository root with a LaTeX installation that includes IEEEtran, IEEEtranN, BibTeX, natbib, cleveref, xr-hyper, and the packages named in `ieee_preamble.tex`.

The manuscripts import one another's labels, so a clean build needs both auxiliary files before references settle:

```sh
latexmk -pdf -interaction=nonstopmode -halt-on-error supplementary.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error supplementary.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

The outputs are `main.pdf` and `supplementary.pdf`. The NeurIPS checklist and appendix are excluded from `main.pdf`; the existing appendix content is included in `supplementary.pdf`.
