# Diagram fonts

The three LARA diagrams use Nimbus Roman (regular, bold, italic, and bold italic),
a Times-compatible family matching the Times typography in the ICLR template.
The font files, upstream revision, and redistribution license are bundled under
`nimbus-roman/`. The previous Comfortaa family remains available in `comfortaa/`.

From the repository root, run:

```sh
bash scripts/build_figures.sh
```

This rebuilds the editable SVGs, PDFs, and high resolution PNGs. SVGs embed the
font files for browser viewing. The rendering script uses the bundled fontconfig
configuration and Pango's FreeType backend, so rendering uses Nimbus Roman on
macOS and Linux without installing it globally. PDFs embed subsets of the fonts.
Text has a faint offset shadow; only the shadow copy is blurred, while foreground
text remains vector in PDF exports.
