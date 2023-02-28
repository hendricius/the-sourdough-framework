all:
	biber book
	pdflatex -synctex=1 -interaction=nonstopmode -shell-escape book.tex


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

release:
	rm -rf release
	mkdir release
	cp book.pdf release/TheBreadCode-The-Sourdough-Framework.pdf
