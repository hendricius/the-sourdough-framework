FROM registry.gitlab.com/islandoftex/images/texlive

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
    wget \
    ruby3.1 \
    ruby-dev \
    build-essential

WORKDIR /root

# Install ruby for the website build process
RUN gem install bundler
COPY website/Gemfile.lock /root
COPY website/Gemfile /root
COPY website/.ruby-version /root
RUN bundle install

# Install support to build amazon kindle books
RUN wget https://archive.org/download/kindlegen_linux_2_6_i386_v2_9/kindlegen_linux_2.6_i386_v2_9.tar.gz && \
    tar xzf kindlegen_linux_2.6_i386_v2_9.tar.gz && \
    mv kindlegen /usr/bin

CMD ["/bin/bash"]
