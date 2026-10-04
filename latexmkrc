# Overleaf builds only the selected document. The main paper and supplement
# import each other's labels, so refresh the other .aux file first. A nested
# latexmk run also tracks edits inside \input files in either document.
unless ($ENV{LARA_XR_SUBBUILD}) {
    my $root = 'main';
    for my $arg (@ARGV) {
        $root = $1 if $arg =~ m{(?:^|/)(main|supplementary)\.tex$};
    }
    my $external = $root eq 'main' ? 'supplementary' : 'main';

    local $ENV{LARA_XR_SUBBUILD} = 1;
    my $result = system('latexmk', '-pdf',
        '-aux-directory=output-subdoc',
        '-output-directory=output-subdoc',
        "$external.tex");
    die "Could not build $external.aux\n" if $result != 0;

    require File::Copy;
    File::Copy::copy("output-subdoc/$external.aux", "$external.aux")
        or die "Could not copy $external.aux\n";
}
