# Macros for commands {{{
LATEX := latexmk -cd -pdflua -lualatex="lualatex -interaction=nonstopmode" -synctex=1 -use-make
EBOOK := tex4ebook --lua -d epub -f epub -c tex4ebook.cfg -B epub_build
WEBSITE := make4ht --lua -c website.cfg -uf html5+tidy+common_domfilters -B website_build
CLEAN := latexmk -cd -lualatex -c -use-make
CHECK_1 := lacheck
CHECK_2 := chktex
CONVERT_PIC := convert
REDUCE_PIC := -resize '800x800>' \
		-strip -interlace Plane -gaussian-blur 0.05 -quality 85\% \
		-set colorspace Gray -separate -evaluate-sequence Mean
REDUCE_PIC_COLOR := -quality 80\%
RSYNC := rsync -au --exclude 'book.epub' --exclude '*.jpg'
GIT := git --no-pager
SPELL_CHECK := hunspell -t -l -d en_US

# We want bash as shell
SHELL := $(shell if [ -x "$$BASH" ]; then echo $$BASH; \
	 else if [ -x /bin/bash ]; then echo /bin/bash; \
	 else echo sh; fi; fi)

ifdef DEBUG
LATEX += -diagnostics
EBOOK += -a debug
WEBSITE += -a debug
endif
# }}}

# Default target is not all because most of the time we just want a pdf...
# and building everything take a long time.
.DEFAULT_GOAL := serif

# Dependencies {{{
chapters = baking basics bread-types cover flour-types history intro mix-ins\
		non-wheat-sourdough sourdough-starter storing-bread troubleshooting\
		wheat-sourdough glossary

# Tables and TikZ flowcharts/plots/drawings... {{{
src_tables  := $(wildcard tables/table-*.tex)
src_figures := $(wildcard figures/fig-*.tex) figures/flowcharts_tikz.tex figures/vars.tex
src_figures += $(wildcard plots/fig-*.tex) abbreviations.tex colors.tex
src_recipes := $(wildcard recipes/*.tex)
src_plots   := $(wildcard plots/*.table)
# }}}

# Actual book text and LaTeX code {{{
src_tex := $(foreach directory, $(chapters), $(wildcard $(directory)/*.tex))
src_tex += book.tex book_sans_serif.tex colors.tex abbreviations.tex
src_tex += $(src_recipes) supporters.csv references.bib
src_tex += sourdough.sty
# }}}

tgt_figures := $(patsubst %.tex, %.png,$(src_figures))

# Photos {{{
images := $(wildcard images/*/*.jpg)
images += $(wildcard images/*.jpg)
images += $(wildcard images/*.png)
images += $(wildcard images/*/*.png)
images += $(foreach directory, $(chapters), $(wildcard $(directory)/*.jpg))
images += $(foreach directory, $(chapters), $(wildcard $(directory)/*/*.jpg))
images += $(foreach directory, $(chapters), $(wildcard $(directory)/*.png))
images += $(foreach directory, $(chapters), $(wildcard $(directory)/*/*.png))

# Black and White ebook, we will just re-zip directory after converting the
# images to lower resolution and greyscale
bw_images := $(addprefix bw-book-epub/OEBPS/, $(images))

# For lower resolution colour ebook (see below) we will not convert png as it
# only get worst we will copy them instead... so remove them as a dependency.
low_res_images := $(addprefix low-res-book-epub/OEBPS/, $(images))
low_res_images := $(filter-out %.png, $(low_res_images))
# }}}

# All together.
src_all := $(src_tex) $(src_figures) $(src_tables) $(images) $(src_plots)

# Format specific configuration files
ebook_src := $(src_all) tex4ebook.cfg book.mk4 book-ebook.css nameref.4ht

website_src := $(src_all) website.cfg style.css
website_dir := static_website_html
website_assets := $(wildcard ../website/assets/*)
ruby_src := ../website/modify_build.rb $(website_assets)
ruby_pkg := ../website/Gemfile ../website/Gemfile.lock
# }}}

# Internal build rules {{{
# Flowcharts {{{
# TODO: check if it works on github CI
%.png: %.tex
	@printf '%s\n' "\input{./vars.tex}" > $@.in
	@printf '%s\n' "\begin{document}" >> $@.in
	@cat $< >> $@.in
	@printf '%s\n' "\end{document}" >> $@.in
	$(LATEX) $@.in
	figures/export_figures.sh $@.pdf

%.xbb: %.jpg
	ebb -x $<
# }}}

# Pdf {{{
# Default rules for pdf, getting overwritten when built in a sub-directory
%.pdf: %.tex
	$(LATEX) $<

book_serif/book.pdf: $(src_all)
	$(LATEX) -output-directory=book_serif book.tex

book_sans_serif/book_sans_serif.pdf: $(src_all)
	$(LATEX) -output-directory=book_sans_serif book_sans_serif.tex
# }}}

# Ebook {{{
###################################
.PHONY: copy_ebook_files copy_ebook_files_low_res
epub/%.epub: %.tex $(ebook_src) cover/cover-page.xbb
	$(EBOOK) $<

copy_ebook_files: ebook
	$(RSYNC) --exclude '*.png' epub_build/book-epub/ bw-book-epub/

# Now that we have built the ebook we will generate 2 more versions
#
# 1) With kindle app on phone we want a colour version with size < 50 MB
# 2) A black-white version for actual eink readers
#
# In both cases we just convert images and repack the ebpub

# We do not convert SVG to B&W or lower res for now as they are super small
# anyway
bw-book-epub/OEBPS/%.jpg: %.jpg
	mkdir -p $(dir $@)
	$(CONVERT_PIC) $< $(REDUCE_PIC) $@

bw-book-epub/OEBPS/%.png: %.png
	mkdir -p $(dir $@)
	$(CONVERT_PIC) $< $(REDUCE_PIC) $@

epub/bw_book.epub: copy_ebook_files $(bw_images)
	cd bw-book-epub; zip -q0X ../epub/bw_book.epub mimetype
	cd bw-book-epub; zip -q9XrD ../epub/bw_book.epub ./

# Now the low res
copy_ebook_files_low_res: ebook
	$(RSYNC) epub_build/book-epub/ low-res-book-epub/

low-res-book-epub/OEBPS/%.jpg: %.jpg
	mkdir -p $(dir $@)
	$(CONVERT_PIC) $< $(REDUCE_PIC_COLOR) $@

epub/low_res_book.epub: copy_ebook_files_low_res $(low_res_images)
	cd low-res-book-epub; zip -q0X ../epub/low_res_book.epub mimetype
	cd low-res-book-epub; zip -q9XrD ../epub/low_res_book.epub ./
# }}}

# Website {{{
###################################
.PHONY: html website
$(website_dir)/book.html: $(website_src) cover/cover-page.xbb
	$(WEBSITE) -d $(website_dir) book.tex

html: $(website_dir)/book.html
	cp $< $(website_dir)/index.html

# Because packages will be installed in hard to predict places use a file as
# marker..
../website/_bundle_install_done: $(ruby_pkg)
	-rm ../website/$@
	cd ../website && bundle install
	touch ../website/$@

# TODO: this will run every single time, but is so fast we don't really care
website: html ../website/_bundle_install_done $(ruby_src)
	cd ../website && ruby modify_build.rb
#}}}

# Figures only {{{
###################################
.PHONY: export_figures
# Requires that you have docker running on your computer.
export_figures: pdf $(tgt_figures)
	cd figures/ && bash export_figures.sh
# }}}
# }}}

# User level targets {{{
# Build targets {{{
.PHONY: all
all: bake

# Finally actual project targets (i.e. build pdf and ebooks)
.PHONY: pdf serif sans_serif ebook

pdf: serif sans_serif
serif: book_serif/book.pdf
sans_serif: book_sans_serif/book_sans_serif.pdf

ebook: epub/book.epub
bw_ebook: epub/bw_book.epub
low_res_ebook: epub/low_res_book.epub
# }}}

# Top level releases rules {{{
.PHONY: bake release_serif release_sans_serif
bake: release_serif release_sans_serif website

release:
	mkdir -p release

release_serif: serif ebook bw_ebook low_res_ebook | release
	cp book_serif/book.pdf release/TheBreadCode-The-Sourdough-Framework.pdf
	cp epub/bw_book.epub release/TheBreadCode-The-Sourdough-Framework-black-and-white.epub
	cp epub/low_res_book.epub release/TheBreadCode-The-Sourdough-Framework.epub
	# Kindle does not allow files larger than 50 MB... so let's check
	@if [ `du -sb epub/low_res_book.epub | cut -f1` -gt 49500000 ]; then \
		echo "ERROR: epub File too big"; \
		exit 1; \
	fi

release_sans_serif: sans_serif | release
	cp book_sans_serif/book_sans_serif.pdf release/TheBreadCode-The-Sourdough-Framework-sans-serif.pdf
# }}}

# Clean up {{{
###################################

# delete generated files
.PHONY: clean_figures clean_ebook_build clean_website_build clean mrproper
clean_figures:
	-$(CLEAN) $(patsubst %.tex, %.png.in, $(src_figures))
	-rm $(patsubst %.tex, %.png.pdf, $(src_figures))
	-rm $(patsubst %.tex, %.png.in, $(src_figures))
	-rm $(wildcard figures/*.png.*)
	-rm cover/cover-page.xbb

clean_ebook_build:
	-rm epub_build/book*.{4ct,4tc,aux,bbl,bcf,blg,dvi,fdb_latexmk,fls,html}
	-rm epub_build/book*.{idv,lg,loc,log,ncx,run.xml,tmp,xref}
	-rm epub_build/{book.css,content.opf} epub_build/book-epub/mimetype
	-rm epub_build/book*x.svg
	-rm -rf epub_build/book-epub/META-INF epub_build/book-epub/OEBPS

clean_website_build:
	-rm website_build/book*.{4ct,4tc,aux,bbl,bcf,blg,dvi,fdb_latexmk,fls,html}
	-rm website_build/book*.{idv,lg,loc,log,ncx,run.xml,tmp,xref}
	-rm website_build/book.{loc,dlog}

clean: clean_ebook_build clean_figures clean_website_build
	$(CLEAN) -output-directory=book_serif book.tex
	$(CLEAN) -output-directory=book_sans_serif book_sans_serif.tex
	-rm book*/*.{bbl,loc,run.xml}

mrproper: clean
	$(CLEAN) -C $(src_figures)
	$(CLEAN) -C -output-directory=book_serif book.tex
	$(CLEAN) -C -output-directory=book_sans_serif book_sans_serif.tex
	-rm figures/*.png
	-rm -rf release/
	-rm -rf book_serif/ book_sans_serif/
	-rm -rf epub/ epub_build/ bw-book-epub/ low-res-book-epub/
	-rm -rf website_build/ $(website_dir)
# }}}

# Help {{{
###################################
.PHONY: help
help:
	@echo ""
	@echo "default: builds the book in pdf format (serif)"
	@echo ""
	@echo "Releases:"
	@echo "  all: pdf serif and sans-serif accessible version, ebooks in colours"
	@echo "     and black&white versions as well as the website"
	@echo ""
	@echo "  bake: same as build all"
	@echo ""
	@echo "  release_serif: build serif only version of pdf and ebook"
	@echo "  release_sans_serif: build sans-serif/accessible version of pdf"
	@echo ""
	@echo "Portable Document Format (pdf):"
	@echo "  sans_serif: build accessible pdf only (same as release_sans_serif)"
	@echo "  serif: build serif pdf only"
	@echo "  pdf: builds both serif and accessible pdf"
	@echo ""
	@echo "Ebooks (epub):"
	@echo "  ebook: builds only the colour ebook"
	@echo "  low_res_ebook: builds the colour ebook in lower resolution"
	@echo "  bw_ebook: builds the low res black & white ebook"
	@echo ""
	@echo "Website:"
	@echo "  website: build the static website from LaTeX sources and post-process it"
	@echo "  html: build the static website from LaTeX sources _without_ post-processing"
	@echo ""
	@echo "Cleanup:"
	@echo "  mrproper: delete all generated files intermediate and pdf/ebooks/website"
	@echo "  clean: delete all intermediate files keep targets (pdf/ebooks/website)"
	@echo "  clean_figures: delete intermediate TikZ files"
	@echo "  clean_website_build: delete intermediate website files"
	@echo "  clean_ebook_build: delete intermediate ebook files"
	@echo ""
	@echo "Debug targets:"
	@echo ""
	@echo "figures: build TikZ figures only"
	@echo ""
	@echo "Quick builds:"
	@echo "  quick: compiles serif but runs lulatex only once"
	@echo "         will halt on first error"
	@echo "  quick_ebook: compiles ebook but runs lulatex only once"
	@echo ""
	@echo "Checks:"
	@echo "  tex-check: runs static analysis checker on LaTeX source to spot"
	@echo "       programming or typographic mistakes"
	@echo "  spell-check: runs a spell checker"
	@echo "  check: runs both checkers"
	@echo ""
	@echo "Dump informations:"
	@echo "  show_tools_version: Show version of tools used on the build machine"
	@echo "  printvars: print all variables in the makefile"
	@echo "  print-X: print makefile variable X"
	@echo ""
	@echo "set DEBUG i.e make DEBUG=1 ebook to add debug flags to commands"
# }}}
# }}}

# Debug Stuff {{{
###################################

# Verify your spelling and TeX warnings {{{
.PHONY: check tex-check spell-check
# Goal is not really to have 0 warning reported but we should check we don't
# add many and if we do, we know they are false positive
check: spell-check tex-check

tex-check: $(src_tex)
	@echo "Running: " $(CHECK_1)
	$(CHECK_1) book.tex
	@echo ""
	@echo "Running: " $(CHECK_2)
	$(CHECK_2) book.tex

# Should be 0 if not and you are really sure update the exception file
spell-check: $(src_tex) spelling_exceptions.txt
	# Generate exceptions this way to avoid false positives
	# hunspell -t -l -d en_US **/*.tex *.csv *.sty *.sty | cut -f 2 -d ':' | sort -u > spelling_exceptions.txt
	$(SPELL_CHECK) -p spelling_exceptions.txt $(src_tex)
#}}}

.PHONY: quick quick_ebook show_tools_version printvars
# Those 2 targets allow fast debug cycles but not resolving references etc
# They also ignore dependencies and run each time you call them.
quick: # run latex only once no biber, no references etc...
	$(LATEX) -e '$$max_repeat=1' -halt-on-error -output-directory=book_serif book.tex

quick_ebook: cover/cover-page.xbb # run latex only once no biber, ref etc...
	$(EBOOK) --mode draft book.tex

show_tools_version: # Show version of tools used on the build machine {{{
	-$(GIT) log -5 --pretty="%h: %s by %an on %as"
	@echo ""
	-uname -a
	@echo ""
	-$(SHELL) --version
	@echo ""
	-@echo "PATH:"
	-@echo $(PATH) | tr ':' '\n'
	@echo ""
	-latexmk --version
	@echo ""
	-lualatex --version
	@echo ""
	-tex4ebook --version
	@echo ""
	-make4ht --version
	@echo ""
	-tidy -version
	@echo ""
	-dvisvgm --version
	@echo ""
	-lacheck | head -5 | tail -1
	@echo ""
	-chktex --version
	@echo ""
	-make --version
	@echo ""
	-biber -version
	@echo ""
	-ruby --version
	@echo ""
	-$(CONVERT_PIC) --version
	@echo ""
	-rsync --version
# }}}

# You can find the value of variable X with the following command:
# make print-X
print-%: ; @echo $* = $($*) # Print a makefile variable

printvars: # Print all variables in the makefile
	@$(foreach V,$(sort $(.VARIABLES)), \
	$(if $(filter-out environ% default automatic, \
	$(origin $V)),$(info $V=$($V) ($(value $V)))))
# }}}
