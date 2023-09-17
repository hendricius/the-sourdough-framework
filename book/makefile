# Macros for commands
LATEX := latexmk -cd -pdflua -lualatex="lualatex -interaction=nonstopmode" -synctex=1 -use-make
EBOOK := tex4ebook --lua -d epub -c tex4ebook.cfg
WEBSITE := make4ht --lua -c website.cfg -a debug -uf html5+tidy+common_domfilters+dvisvgm_hashes
CLEAN := latexmk -cd -lualatex -c -use-make
CHECK_1 := lacheck
CHECK_2 := chktex

ifdef DEBUG
EBOOK += -a debug
WEBSITE += -a debug
endif

website_dir := static_website_html

# List all files that are dependencies
chapters = baking basics bread-types cover flour-types history intro mix-ins\
		non-wheat-sourdough sourdough-starter storing-bread troubleshooting\
		wheat-sourdough

src_tables  := $(wildcard tables/table-*.tex)
src_figures := $(wildcard figures/fig-*.tex) figures/flowcharts_tikz.tex

src_tex := $(foreach directory, $(chapters), $(wildcard $(directory)/*.tex))
src_tex += book.tex book_sans_serif.tex references.bib figures/vars.tex
src_tex += supporters.csv sourdough.sty colors.tex

images := $(wildcard images/*/*.jpg)
images += $(wildcard images/*.jpg)
images += $(wildcard images/*.png)
images += $(wildcard images/*/*.png)
images += $(foreach directory, $(chapters), $(wildcard $(directory)/*.jpg))
images += $(foreach directory, $(chapters), $(wildcard $(directory)/*.png))

src_all := $(src_tex) $(src_figures) $(src_tables) tex4ebook.cfg book.mk4 $(images)

website_src := $(src_all) website.cfg

website_assets := $(wildcard ../website/assets/*)
ruby_src := ../website/modify_build.rb $(website_assets)
ruby_pkg := ../website/Gemfile  ../website/Gemfile.lock

tgt_figures := $(patsubst %.tex, %.png,$(src_figures))

# Default target is not all becuse most of the time we just want a pdf...
# ebook take a long time to build.
.DEFAULT_GOAL := build_ebook

# Default rules for pdf and ebooks, getting overwritten when built in a
# sub-directory
%.pdf: %.tex
	$(LATEX) $<

# TODO: check if it works on github CI
%.png: %.tex
	@echo "\input{./vars.tex}" > $@.in
	# \b is backspace..
	@echo "\\\begin{document}" >> $@.in
	@cat $< >> $@.in
	@echo "\\\end{document}" >> $@.in
	$(LATEX) $@.in
	figures/export_figures.sh $@.pdf

%.xbb: %.jpg
	ebb -x $<

book_serif/book.pdf: $(src_all)
	$(LATEX) -output-directory=book_serif book.tex

book_sans_serif/book_sans_serif.pdf: $(src_all)
	$(LATEX) -output-directory=book_sans_serif book_sans_serif.tex

epub/%.epub: %.tex $(src_all) cover/cover-page.xbb
	$(EBOOK) -f epub $<

# Now with the rules
# Expected usual rules first

.PHONY: all
all: bake

.PHONY: help
help:
	@echo ""
	@echo "default: builds the book in pdf format (serif)"
	@echo ""
	@echo "all: pdf and ebooks serif and sans-serif accessible version, same as"
	@echo "     build release"
	@echo "bake: same as build all"
	@echo ""
	@echo "check: runs static analysis checker on LaTeX source to spot"
	@echo "       programming or typographic mistakes"
	@echo ""
	@echo "clean: delete all intermediate files keep targets (pdf/ebooks/website)"
	@echo "mrproper: delete all generated files intermediate and pdf/ebooks/website"
	@echo "  clean_figures: delete intermediate TikZ files"
	@echo "  clean_website_build: delete intermediate website files"
	@echo "  clean_ebook_build: delete intermediate ebook files"
	@echo ""
	@echo "build_pdf: builds both serif and accessible pdf"
	@echo ""
	@echo "build_ebook: builds only the ebook"
	@echo ""
	@echo "build_sans_serif_pdf: build accessible pdf only"
	@echo ""
	@echo "build_serif_pdf: build serif pdf only"
	@echo ""
	@echo "figures: build TikZ figures"
	@echo ""
	@echo "release_serif: build serif only version of pdf and ebooks"
	@echo "release_sans_serif: build sans-serif/accessible version of pdf"
	@echo ""
	@echo "website: build the static website from LaTeX sources and post-process it"
	@echo "html: build the static website from LaTeX sources _without_ post-processing"
	@echo ""
	@echo "Debug targets:"
	@echo ""
	@echo "quick: compiles serif_pdf but runs lulatex only once"
	@echo ""
	@echo "quick_ebook: compiles serif_ebook but runs lulatex only once"
	@echo ""
	@echo "show_tools_version: Show version of tools used on the build machine"
	@echo ""
	@echo "print-X: print makefile variable X"
	@echo ""
	@echo "printvars: print all variables in the makefile"
	@echo ""
	@echo "set DEBUG i.e make DEBUG=1 build_ebook to add debug flags to commands"


# Finally project specif targets
.PHONY: build_pdf
build_pdf: build_serif_pdf build_sans_serif_pdf

.PHONY: build_serif_pdf
build_serif_pdf: book_serif/book.pdf

.PHONY: build_sans_serif_pdf
build_sans_serif_pdf: book_sans_serif/book_sans_serif.pdf

.PHONY: build_ebook
build_ebook: build_serif_ebook 

.PHONY: build_serif_ebook
build_serif_ebook: epub/book.epub | make_release_dir

.PHONY: export_figures
# Requires that you have docker running on your computer.
export_figures: build_pdf $(tgt_figures)
	cd figures/ && bash export_figures.sh

# Goal is not really to have 0 warning reported but we should check we don't
# add many and if we do, we know they are false positive
PHONY: check
check: $(SRC_TEX)
	@echo "Running: " $(CHECK_1)
	$(CHECK_1) book.tex
	@echo ""
	@echo "Running: " $(CHECK_2)
	$(CHECK_2) book.tex

.PHONY: clean_figures
clean_figures:
	- $(CLEAN) $(patsubst %.tex, %.png.in, $(src_figures))
	- rm $(patsubst %.tex, %.png.pdf, $(src_figures))
	- rm $(patsubst %.tex, %.png.in, $(src_figures))
	- rm $(wildcard figures/*.png.*)
	- rm cover/cover-page.xbb

.PHONY: clean_ebook_build
clean_ebook_build:
	-rm  book*.{4ct,4tc,aux,bbl,bcf,blg,dvi,fdb_latexmk,fls,html}
	-rm  book*.{idv,lg,loc,log,ncx,run.xml,tmp,xref}
	-rm  book*x.svg
	-rm  book.css
	-rm  content.opf

.PHONY: clean_website_build
clean_website_build: clean_ebook_build
	-rm book-*.svg
	-rm book.{loc,dlog}
	-rm $(subst $(website_dir)/,, $(wildcard $(website_dir)/*.html))

.PHONY: clean
clean: clean_ebook_build clean_figures clean_website_build
	$(CLEAN) -output-directory=book_serif book.tex
	$(CLEAN) -output-directory=book_sans_serif book_sans_serif.tex
	-rm  book*/*.{bbl,loc,.run.xml}
	-rm -rf book*-epub/META-INF
	-rm -rf book*-epub/OEBPS
	-rm  book*-epub/mimetype

.PHONY: mrproper
mrproper: clean
	$(CLEAN) -C $(src_figures)
	$(CLEAN) -C -output-directory=book_serif book.tex
	$(CLEAN) -C -output-directory=book_sans_serif book_sans_serif.tex
	-rm figures/*.png
	-rm *.html
	-rm *.svg
	-rm -rf epub/
	-rm -rf release/
	-rm -rf book_serif/
	-rm -rf book_sans_serif/
	-rm -rf book-epub/
	-rm -rf $(website_dir)

.PHONY: bake
bake: release_serif release_sans_serif

.PHONY: make_release_dir
make_release_dir:
	mkdir -p release

.PHONY: release_serif
release_serif: build_serif_pdf build_serif_ebook | make_release_dir
	cp book_serif/book.pdf release/TheBreadCode-The-Sourdough-Framework.pdf
	cp epub/book.epub release/TheBreadCode-The-Sourdough-Framework.epub

.PHONY: release_sans_serif
release_sans_serif: build_sans_serif_pdf | make_release_dir
	cp book_sans_serif/book_sans_serif.pdf  release/TheBreadCode-The-Sourdough-Framework-sans-serif.pdf

# Website stuff
$(website_dir)/book.html: $(website_src) cover/cover-page.xbb
	$(WEBSITE) -d $(website_dir) book.tex

.PHONY: html
html: $(website_dir)/book.html
	cp $< $(website_dir)/index.html

# Because packages will be installed in hard to predict places use a file as
# marker..
../website/_bundle_install_done: $(ruby_pkg)
	- rm ../website/$@
	cd ../website && bundle install
	touch ../website/$@

# TODO: this will run every single time, but is so fast we don't really care
.PHONY: website
website: html ../website/_bundle_install_done $(ruby_src)
	cd ../website && ruby modify_build.rb

# Debug Stuff from now on
.PHONY: quick show_tools_version printvars

# Those 2 targets allow fast debug cycles but not reolvig refrences etc
quick:  # run latex only once no biber, no references etc..
	$(LATEX) -e '$$max_repeat=1' -output-directory=book_serif book.tex

quick_ebook: cover/cover-page.xbb  # run latex only once no biber, refe etc..
	$(EBOOK) --mode draft -f epub book.tex

show_tools_version:  # Show version of tools used on the build machine
	- git log -n 1
	@echo ""
	- latexmk --version
	@echo ""
	- lualatex --version
	@echo ""
	- tex4ebook --version
	@echo ""
	- make4ht --version
	@echo ""
	- tidy -version
	@echo ""
	- kindlegen --version
	@echo ""
	- lacheck --version
	@echo ""
	- chktex --version
	@echo ""
	- make --version
	@echo ""
	- biber -version
	@echo ""
	- ruby --version
	@echo ""

# You can find the value of variable X with the following command:
# make print-X
print-%: ; @echo $* = $($*)  # Print a makefile variable

printvars:  # Print all variables in the makefile
	@$(foreach V,$(sort $(.VARIABLES)), \
	$(if $(filter-out environ% default automatic, \
	$(origin $V)),$(info $V=$($V) ($(value $V)))))
