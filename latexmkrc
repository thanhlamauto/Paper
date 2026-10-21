# Build xr-hyper's external document automatically on Overleaf and with latexmk.
# Adapted from Overleaf's xr/latexmk example (John Collins):
# https://www.overleaf.com/learn/how-to/Cross_referencing_with_the_xr_package_in_Overleaf

add_cus_dep('tex', 'aux', 0, 'lara_external_document');

sub lara_external_document {
    my ($document) = @_;
    # tex_basename is the source name; root_filename may be "output" on Overleaf.
    return 0 if $document eq $tex_basename;
    return 0 unless $document eq 'main' || $document eq 'supplementary';

    my $subdir = 'output-subdoc';
    my $parent_aux = "$aux_dir1$root_filename.aux";
    my $parent_alias = "$tex_basename.aux";
    # References are reciprocal. Give the child the parent's latest labels,
    # including when Overleaf uses -jobname=output and a separate output folder.
    if (-e $parent_aux && $parent_aux ne $parent_alias) {
        copy($parent_aux, $parent_alias)
            or die "Cannot copy $parent_aux to $parent_alias: $!";
    }

    my $engine = $pdf_mode == 4 ? '-pdflua'
               : $pdf_mode == 5 ? '-pdfxe' : '-pdf';
    # -norc disables this rule in the child, preventing main <-> supp recursion.
    my $status = system('latexmk', '-norc', $engine,
                        '-interaction=nonstopmode', '-halt-on-error',
                        "-outdir=$subdir", "$document.tex");
    return $status if $status;
    copy("$subdir/$document.aux", "$document.aux")
        or die "Cannot copy external labels for $document: $!";
    rdb_add_generated("$document.aux");

    # Watch included files too: appendix edits must refresh labels even when
    # supplementary.tex itself has not changed. Exclude generated aux/log files.
    my @inputs = ('refs.bib');
    if (open(my $fls, '<', "$subdir/$document.fls")) {
        while (my $line = <$fls>) {
            next unless $line =~ /^INPUT (.+)\s*$/;
            my $input = $1;
            $input =~ s/\s+$//;
            $input =~ s{^\./}{};
            next if $input =~ m{^/} || $input =~ m{^\Q$subdir\E/};
            next if $input =~ /\.(?:aux|bbl|out|log|fls|fdb_latexmk)$/;
            push @inputs, $input if -f $input;
        }
        close($fls);
    }
    # A changed parent label/page number must also reach the supplementary PDF.
    push @inputs, $parent_aux if -e $parent_aux;
    rdb_ensure_files_here(@inputs);
    return 0;
}
