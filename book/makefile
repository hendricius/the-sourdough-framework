.PHONY: build_pdf
build_pdf: clean figures tables
	pdflatex book.tex
	biber book
	pdflatex book.tex

# setup_default_build:
# 	sed -i '.bak' 's#^\\usepackage{helvet}#%\\usepackage{helvet}#g' book.tex
# 	sed -i '.bak' 's#^\\renewcommand{\\familydefault}{\\sfdefault}#%\\renewcommand{\\familydefault}{\\sfdefault}#g' book.tex


.PHONY: clean_figures
clean_figures:
	cd figures
	rm -rf figures/*.aux
	rm -rf figures/*.fdb_latexmk
	rm -rf figures/*.fls
	rm -rf figures/*.log
	rm -rf figures/*.pdf
	rm -rf figures/*.png

.PHONY: export_figures
# Requires that you have docker running on your computer.
export_figures:
	cd figures/ && bash export_figures.sh

.PHONY: figures
figures: clean_figures
	cd figures && find . -name "fig-*.tex" -exec pdflatex '{}' \;

.PHONY: tables
tables:
	cd tables && find . -name "table-*.tex" -exec pdflatex '{}' \;

.PHONY: clean
clean: clean_figures
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
	rm -rf book-azw3/
	rm -rf book.azw3
	rm -f *.pdf
	rm -f output.log
	rm -f content.opf
	find . -name "*.xbb" | xargs rm -f
	rm -rf release/
	rm -rf release_sans_serif/

.PHONY: release_default
release_default: clean build_pdf make_release_dir build_ebook
	cp book.pdf release/TheBreadCode-The-Sourdough-Framework.pdf
	cp book-mobi/book.mobi release/TheBreadCode-The-Sourdough-Framework.mobi
	cp book-epub/book.epub release/TheBreadCode-The-Sourdough-Framework.epub
	cp book-azw3/book.azw3 release/TheBreadCode-The-Sourdough-Framework.azw3

.PHONY: release_default
release: release_default release_sans_serif

.PHONY: make_release_dir
make_release_dir:
	mkdir -p release

.PHONY: release_sans_serif
release_sans_serif: make_release_dir
	# For the sans serif version we are just going
	# to copy all the files into a new folder and
	rm -rf release_sans_serif/
	mkdir /tmp/release_sans_serif
	cp -R * /tmp/release_sans_serif
	mv /tmp/release_sans_serif .
	# The next part will uncomment the sans serif font in the book.tex
	#
	# Note that the OS X sed behaves a little different
	# than the gnu sed. If you are on OS X you might
	# have to install gnu sed for this to work. Or you can
	# use sed -i '.bak' restofcommand. OS X wants to have
	# a backup file listed before replacing the contents
	# of a file.
	sed -i 's#%\\usepackage{helvet}#\\usepackage{helvet}#g' release_sans_serif/book.tex
	sed -i 's#%\\renewcommand{\\familydefault}{\\sfdefault}#\\renewcommand{\\familydefault}{\\sfdefault}#g' release_sans_serif/book.tex
	cd release_sans_serif && $(MAKE) release_default
	cp release_sans_serif/release/TheBreadCode-The-Sourdough-Framework.pdf  release/TheBreadCode-The-Sourdough-Framework-sans-serif.pdf
	cp release_sans_serif/release/TheBreadCode-The-Sourdough-Framework.mobi release/TheBreadCode-The-Sourdough-Framework-sans-serif.mobi
	cp release_sans_serif/release/TheBreadCode-The-Sourdough-Framework.epub release/TheBreadCode-The-Sourdough-Framework-sans-serif.epub
	cp release_sans_serif/release/TheBreadCode-The-Sourdough-Framework.azw3 release/TheBreadCode-The-Sourdough-Framework-sans-serif.azw3

.PHONY: build_ebook
build_ebook: make_release_dir
	find . -name "*.jpg" | xargs ebb -x
	find . -name "*.png" | xargs ebb -x
	tex4ebook -c tex4ebook.cfg -f epub book.tex
	tex4ebook -c tex4ebook.cfg -f mobi book.tex
	tex4ebook -c tex4ebook.cfg -f azw3 book.tex
