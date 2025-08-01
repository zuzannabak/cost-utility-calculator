# Build PDF with XeLaTeX (no pdfLaTeX ever)
$pdf_mode = 1;
$pdflatex = 'xelatex -synctex=1 -interaction=nonstopmode -file-line-error %O %S';
$bibtex   = 'bibtex %O %S';      # default
$clean_ext .= ' %R.synctex.gz';  # clean SyncTeX on latexmk -C
