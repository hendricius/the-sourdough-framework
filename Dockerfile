FROM debian:trixie

LABEL "maintainer"="Hendrik Kleinwächter <hendrik.kleinwaechter@gmail.com>"
LABEL "repository"="https://github.com/hendricius/the-sourdough-framework"
LABEL "homepage"="https://github.com/hendricius/the-sourdough-framework"
LABEL org.opencontainers.image.source="https://github.com/hendricius/the-sourdough-framework"

# Print release information if needed
RUN cat /etc/*release*

# Install base depdendencies
RUN apt-get update && \
    apt-get install --yes -y --no-install-recommends \
    sudo \
    make \
    tidy \
    pandoc \
    dvisvgm \
    zip \
    git \
    wget \
    ruby3.1 \
    ruby-dev \
    imagemagick \
    build-essential

# Install TeX
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    texlive-full \
    texlive-luatex

WORKDIR /root

# Install ruby for the website build process
RUN gem install bundler
COPY website/Gemfile.lock /root
COPY website/Gemfile /root
COPY website/.ruby-version /root
RUN bundle install

CMD ["/bin/bash"]
