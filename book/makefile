all:
	pdflatex book.tex
	biber book
	pdflatex book.tex
	pdflatex book.tex

fast:
	pdflatex book.tex

clean:
	rm book.blg
	rm book.bbl
	rm book.aux
	rm book.out
	rm book.toc
	rm book.run.xml
	rm book.bcf
	rm book.pdf
	rm book.log
