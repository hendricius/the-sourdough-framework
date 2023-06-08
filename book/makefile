# Macros for commands
LATEX := latexmk -cd -pdf -pdflatex="pdflatex -interaction=nonstopmode" -use-make
EBOOK := tex4ebook -d epub -c tex4ebook.cfg
CLEAN := latexmk -cd -c -use-make
EBOOK_CONVERT := kindlegen

# List all files that are dependencies
SRC_FIGURES := $(wildcard figures/fig-*.tex)
# List all files that are dependencies
CHAPTERS = baking basics bread-types flour-types history intro\
		non-wheat-sourdough sourdough-starter storing-bread troubleshooting\
		wheat-sourdough

SRC_TABLES  := $(wildcard tables/tables-*.tex)
SRC_FIGURES := $(wildcard figures/fig-*.tex)

SRC_TEX := $(foreach directory, $(CHAPTERS), $(wildcard $(directory)/*.tex))
SRC_TEX := $(SRC_TEX) book.tex book_sans_serif.tex references.bib

IMAGES := $(wildcard images/*/*.jpg)
IMAGES := $(IMAGES) $(wildcard images/*/*.png)
IMAGES := $(IMAGES) $(foreach directory, $(CHAPTERS), $(wildcard $(directory)/*.jpg))
IMAGES := $(IMAGES) $(foreach directory, $(CHAPTERS), $(wildcard $(directory)/*.png))

TGT_FIGURES := $(patsubst %.tex, %.pdf,$(SRC_FIGURES))
SRC_ALL := $(SRC_TEX) $(SRC_FIGURES) $(SRC_TABLES) tex4ebook.cfg book.mk4 $(IMAGES)

# Default rules for pdf and ebooks, getting overwritten when built in a
# sub-directory
%.pdf: %.tex
	$(LATEX) $<

book_serif/book.pdf: clean_ebook_build $(SRC_ALL)
	$(LATEX) -output-directory=book_serif book.tex

book_sans_serif/book_sans_serif.pdf: clean_ebook_build $(SRC_ALL)
	$(LATEX) -output-directory=book_sans_serif book_sans_serif.tex

epub/book.epub: book.tex $(SRC_ALL)
	$(EBOOK) -f epub $<

epub/book.mobi: epub/book.epub
	$(EBOOK_CONVERT) $< -o $(notdir $@)

epub/book.azw3:  epub/book.epub
	$(EBOOK_CONVERT) $< -o $(notdir $@)

# Not sure if there is a better way with a wildcard?
epub/book_sans_serif.epub: book_sans_serif.tex $(SRC_ALL)
	$(EBOOK) -f epub $<

epub/book_sans_serif.mobi: epub/book_sans_serif.epub
	$(EBOOK_CONVERT) $< -o $(notdir $@)

epub/book_sans_serif.azw3: epub/book_sans_serif.epub
	$(EBOOK_CONVERT) $< -o $(notdir $@)

# Now with the rules
# Expected usual rules first

.PHONY: default
default: build_pdf

.PHONY: all
all: bake

.PHONY: help
help:
	@echo ""
	@echo "default: builds the book in pdf format (serif)"
	@echo ""
	@echo "all: pdf and ebooks serif and sans-serif accessible version, same as build release"
	@echo "bake: same as build all"
	@echo "release_default: same as build all"
	@echo ""
	@echo "clean: delete all intermediate files keep targets (pdf/ebook)"
	@echo "mrproper: delete all generated files intermediate and pdf/ebooks"
	@echo "clean_figures: delete intermediate TikZ files"
	@echo ""
	@echo "build_ebook: builds only the ebook serif and accessible version"
	@echo "build_pdf:builds both serif and accessible pdf"
	@echo ""
	@echo "build_sans_serif_ebook: build accessible ebook only"
	@echo "build_sans_serif_pdf: build accessible pdf only"
	@echo ""
	@echo "figures: build TikZ figures"

# Finally project specif targets
.PHONY: build_pdf
build_pdf: build_serif_pdf build_sans_serif_pdf

.PHONY: build_serif_pdf
build_serif_pdf: book_serif/book.pdf

.PHONY: build_sans_serif_pdf
build_sans_serif_pdf: book_sans_serif/book_sans_serif.pdf

.PHONY: build_ebook
build_ebook: build_serif_ebook build_sans_serif_ebook

.PHONY: build_serif_ebook
build_serif_ebook: $(TGT_FIGURES) epub/book.epub epub/book.mobi epub/book.azw3 | make_release_dir

.PHONY: build_sans_serif_ebook
build_sans_serif_ebook: $(TGT_FIGURES) epub/book_sans_serif.epub \
						epub/book_sans_serif.mobi \
						epub/book_sans_serif.azw3 | make_release_dir

.PHONY: export_figures
# Requires that you have docker running on your computer.
export_figures:
	cd figures/ && bash export_figures.sh

.PHONY: figures
figures: $(SRC_FIGURES)
	$(LATEX) $<

.PHONY: clean_figures
clean_figures:
	$(CLEAN) $(SRC_FIGURES)

.PHONY: clean_ebook_build
clean_ebook_build:
	-rm  book*.aux
	-rm  book*.run.xml
	-rm  book*.bcf
	-rm  book*.blg
	-rm  book*.log
	-rm  book*.4tc
	-rm  book*.4ct
	-rm  book*.dvi
	-rm  book*.epub
	-rm  book.css
	-rm  book_sans_serif.css
	-rm  book*.idv
	-rm  book*.lg
	-rm  book*.ncx
	-rm  book*.tmp
	-rm  book*.xref
	-rm  book*.html
	-rm  book*.fls
	-rm  book*.fdb_latexmk
	-rm  book*.bbl
	-rm  content.opf

.PHONY: clean
clean: clean_ebook_build clean_figures
	$(CLEAN) -output-directory=book_serif book.tex
	$(CLEAN) -output-directory=book_sans_serif book_sans_serif.tex
	-rm  book*/*.bbl
	-rm  book*/*.run.xml
	-rm -rf book*-epub/META-INF
	-rm -rf book*-epub/OEBPS
	-rm  book*-epub/mimetype
	-rm -rf book*-mobi/META-INF
	-rm -rf book*-mobi/OEBPS
	-rm  book*-mobi/mimetype
	-rm  book*-mobi/book.epub
	-rm -rf book*-mobi/META-INF
	-rm -rf book*-azw3/OEBPS
	-rm -rf book*-azw3/META-INF
	-rm  book*-azw3/book.epub
	-rm  book*-azw3/mimetype

.PHONY: mrproper
mrproper: clean
	$(CLEAN) -C $(SRC_FIGURES)
	$(CLEAN) -C -output-directory=book_serif book.tex
	$(CLEAN) -C -output-directory=book_sans_serif book_sans_serif.tex
	-rm figures/*.pdf
	-rm figures/*.png
	rm -rf epub/
	rm -rf release/
	rm -rf release_sans_serif/
	rm -rf book_serif/
	rm -rf book_sans_serif/
	rm -rf book-epub/
	rm -rf book_sans_serif-epub/

.PHONY: bake
bake: release_default release_sans_serif

.PHONY: make_release_dir
make_release_dir:
	mkdir -p release

.PHONY: release_default
release_default: build_pdf build_ebook | make_release_dir
	cp book_serif/book.pdf release/TheBreadCode-The-Sourdough-Framework.pdf
	cp epub/book.mobi release/TheBreadCode-The-Sourdough-Framework.mobi
	cp epub/book.epub release/TheBreadCode-The-Sourdough-Framework.epub
	cp epub/book.azw3 release/TheBreadCode-The-Sourdough-Framework.azw3

.PHONY: release_sans_serif
release_sans_serif: build_sans_serif_pdf build_sans_serif_ebook | make_release_dir
	cp book_sans_serif/book_sans_serif.pdf  release/TheBreadCode-The-Sourdough-Framework-sans-serif.pdf
	cp epub/book_sans_serif.mobi release/TheBreadCode-The-Sourdough-Framework-sans-serif.mobi
	cp epub/book_sans_serif.epub release/TheBreadCode-The-Sourdough-Framework-sans-serif.epub
	cp epub/book_sans_serif.azw3 release/TheBreadCode-The-Sourdough-Framework-sans-serif.azw3
