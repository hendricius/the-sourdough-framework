FROM ubuntu:rolling

LABEL "maintainer"="Hendrik Kleinwächter <hendrik.kleinwaechter@gmail.com>"
LABEL "repository"="https://github.com/hendricius/the-sourdough-framework"
LABEL "homepage"="https://github.com/hendricius/the-sourdough-framework"
LABEL org.opencontainers.image.source="https://github.com/hendricius/the-sourdough-framework"

# Print release information if needed
# RUN cat /etc/*release*

# Install base depdendencies
RUN apt-get update && \
    apt-get install --yes -y --no-install-recommends \
    sudo \
    make \
    tidy \
    pandoc \
    zip \
    git \
    wget

# Install base LaTeX system
RUN apt-get install --yes -y --no-install-recommends \
    texlive-full

# Install LaTeX extras
RUN apt-get install --yes -y --no-install-recommends \
    latexmk \
    lmodern \
    fonts-lmodern \
    tex-gyre \
    texlive-pictures \
    fonts-texgyre \
    dvisvgm \
    context \
    python3-pygments \
    python3-setuptools

RUN apt-get install --yes -y --no-install-recommends \
    biber \
    texlive-bibtex-extra \
    openjdk-21-jre-headless \
    ghostscript \
    graphviz

RUN apt-get autoclean && apt-get --purge --yes autoremove

WORKDIR /root

# Latest make4ht and tex4ebook
RUN git clone https://github.com/michal-h21/make4ht && \
    cd make4ht && \
    make justinstall

RUN git clone https://github.com/michal-h21/tex4ebook.git && \
    cd tex4ebook && git checkout v0.3i && \
    make && make install

# Support to build amazon kindle books
RUN wget https://archive.org/download/kindlegen_linux_2_6_i386_v2_9/kindlegen_linux_2.6_i386_v2_9.tar.gz && \
    tar xzf kindlegen_linux_2.6_i386_v2_9.tar.gz && \
    mv kindlegen /usr/bin

CMD ["/bin/bash"]
