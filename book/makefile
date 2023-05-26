LATEX := latexmk -cd -pdf -pdflatex="pdflatex -interaction=nonstopmode" -use-make
CLEAN := latexmk -cd -c
PROPER := latexmk -cd -C

%.pdf: %.tex
	$(LATEX) $<

SRC_FIGURES := $(wildcard figures/fig-*.tex)
TGT_FIGURES := $(patsubst %.tex,%.pdf, $(SRC_FIGURES))

SRC_TABLES := $(wildcard tables/table-*.tex)
TGT_TABLES := $(patsubst %.tex,%.pdf, $(SRC_TABLES))

.PHONY: build_pdf
build_pdf: $(TGT_FIGURES) $(TGT_TABLES) book.tex
	$(LATEX) book.tex

# setup_default_build:
# 	sed -i '.bak' 's#^\\usepackage{helvet}#%\\usepackage{helvet}#g' book.tex
# 	sed -i '.bak' 's#^\\renewcommand{\\familydefault}{\\sfdefault}#%\\renewcommand{\\familydefault}{\\sfdefault}#g' book.tex

.PHONY: clean_tables
clean_tables:
	$(CLEAN) $(SRC_TABLES)

.PHONY: proper_tables
proper_tables: clean_tables
	$(PROPER) $(SRC_TABLES)
	- rm -f tables/*.png

.PHONY: clean_figures
clean_figures:
	$(CLEAN) $(SRC_FIGURES)

.PHONY: proper_figures
proper_figures: clean_figures
	$(PROPER) $(SRC_FIGURES)
	- rm -f figures/*.png

.PHONY: export_figures
# Requires that you have docker running on your computer.
export_figures:
	cd figures/ && bash export_figures.sh

# TODO figures/vars.tex is not seen as a dependency
figures/%.pdf: figures/fig-%.tex
.PHONY: figures
figures: $(TGT_FIGURES)

# TODO tables/vars.tex is not seen as a dependency
tables/%.pdf: tables/table-%.tex
.PHONY: tables
tables: $(TGT_TABLES)

.PHONY: mrproper
mrproper: clean
	$(PROPER) book.tex
	- rm -rf release/
	- rm -rf release_sans_serif/
	- rm -rf book-epub/
	- rm -rf book-epub3/
	- rm -rf book-mobi/
	- rm -rf book-azw3/

.PHONY: clean
clean: clean_figures
	$(CLEAN) book.tex
	- rm -f book.bbl
	- rm -f book.run.xml
	- rm -f book.mobi
	- rm -f book.4ct
	- rm -f book.4tc
	- rm -f book.epub
	- rm -f book.css
	- rm -f book.idv
	- rm -f book.lg
	- rm -f book.ncx
	- rm -f book.tmp
	- rm -f book.xref
	- rm -f book*.svg
	- rm -f book*.html
	- rm -f book*.xhtml
	- rm -rf book.azw3
	- rm -f content.opf
	- find . -name "*.xbb" | xargs rm -f

.PHONY: release_default
release_default: mrproper build_pdf make_release_dir build_ebook
	cp book.pdf release/TheBreadCode-The-Sourdough-Framework.pdf
	cp book-mobi/book.mobi release/TheBreadCode-The-Sourdough-Framework.mobi
	cp book-epub/book.epub release/TheBreadCode-The-Sourdough-Framework.epub
	cp book-azw3/book.azw3 release/TheBreadCode-The-Sourdough-Framework.azw3

.PHONY: bake
bake: release_default release_sans_serif

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
	tex4ebook -c tex4ebook.cfg -f epub book.tex
	tex4ebook -c tex4ebook.cfg -f mobi book.tex
	# not sure why, but I hvae to generate the mobi twice for the
	# release command to properly work.
	tex4ebook -c tex4ebook.cfg -f mobi book.tex
	tex4ebook -c tex4ebook.cfg -f azw3 book.tex
