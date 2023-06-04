#!/bin/sh

set -x

cd book
#ls
#cat makefile
make figures
make tables
#make make_pdf
#make -f makefile make_pdf
pdflatex -halt-on-error book.tex
biber
pdflatex -halt-on-error book.tex