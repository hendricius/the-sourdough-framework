FROM ubuntu:latest

LABEL "maintainer"="Hendrik Kleinwächter <hendrik.kleinwaechter@gmail.com>"
LABEL "repository"="https://github.com/hendricius/the-sourdough-framework"
LABEL "homepage"="https://github.com/hendricius/the-sourdough-framework"
LABEL org.opencontainers.image.source="https://github.com/hendricius/the-sourdough-framework"

# Install base depdendencies
RUN apt-get update && \
    apt-get install --yes -y --no-install-recommends \
    make \
    tidy \
    pandoc \
    zip \
    git \
    wget

# Install LaTeX
RUN apt-get install --yes -y --no-install-recommends \
    texlive-full \
    texlive-lang-all

# Install LaTeX extras
RUN apt-get install --yes -y --no-install-recommends \
    latexmk \
    lmodern \
    fonts-lmodern \
    tex-gyre \
    fonts-texgyre \
    dvisvgm \
    context

RUN apt-get autoclean && apt-get --purge --yes autoremove

# Custom TeX packages on latest version
RUN git clone https://github.com/michal-h21/make4ht && \
    cd make4ht && \
    make justinstall SUDO=""

RUN git clone https://github.com/michal-h21/tex4ebook.git && \
    cd tex4ebook && \
    make && \
    make install SUDO=""

# Support to build amazon kindle books
RUN wget https://archive.org/download/kindlegen_linux_2_6_i386_v2_9/kindlegen_linux_2.6_i386_v2_9.tar.gz && \
    tar xzf kindlegen_linux_2.6_i386_v2_9.tar.gz && \
    mv kindlegen /usr/bin

CMD ["/bin/bash"]
