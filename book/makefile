.PHONY: build_pdf
build_pdf: clean figures
	pdflatex book.tex
	biber book
	pdflatex book.tex

.PHONY: figures
figures:
	cd figures && find . -name "fig-*.tex" -exec pdflatex '{}' \; && cd ../

.PHONY: clean
clean:
	rm -f book.blg
	rm -f book.bbl
	rm -f book.aux
	rm -f book.out
	rm -f book.toc
	rm -f book.run.xml
	rm -f book.bcf
	rm -f book.pdf
	rm -f book.log
	rm -f book.mobi
	rm -f book.4ct
	rm -f book.4tc
	rm -f book.dvi
	rm -f book.epub
	rm -f book.css
	rm -f book.fdb_latexmk
	rm -f book.fls
	rm -f book.idv
	rm -f book.lg
	rm -f book.ncx
	rm -f book.tmp
	rm -f book.xref
	rm -f book*.svg
	rm -f book*.html
	rm -f book*.xhtml
	rm -rf book-epub/
	rm -rf book-epub3/
	rm -rf book-mobi/
	rm -f *.pdf
	rm -f output.log
	rm -f content.opf
	rm -rf figures/*.aux
	rm -rf figures/*.fdb_latexmk
	rm -rf figures/*.fls
	rm -rf figures/*.log
	rm -rf figures/*.pdf
	rm -rf figures/*.png
	find . -name "*.xbb" | xargs rm
	rm -rf release/

.PHONY: release
release: clean build_pdf make_release_dir build_ebook
	cp book.pdf release/TheBreadCode-The-Sourdough-Framework.pdf

.PHONY: make_release_dir
make_release_dir:
	mkdir -p release

.PHONY: build_ebook
build_ebook: build_pdf make_release_dir
	find . -name "*.jpg" | xargs ebb -x
	find . -name "*.png" | xargs ebb -x
	tex4ebook -f epub3 -d release book.tex
	tex4ebook -f mobi -d release book.tex

