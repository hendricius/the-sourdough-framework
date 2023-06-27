FROM ghcr.io/xu-cheng/texlive-full

WORKDIR /root

RUN apk add make zip tidyhtml git sudo pandoc
RUN wget https://archive.org/download/kindlegen_linux_2_6_i386_v2_9/kindlegen_linux_2.6_i386_v2_9.tar.gz
RUN tar xzf kindlegen_linux_2.6_i386_v2_9.tar.gz
RUN mv kindlegen /usr/bin
RUN git clone https://github.com/michal-h21/tex4ebook.git
WORKDIR /root/tex4ebook
RUN make
RUN make install
WORKDIR /root

WORKDIR /opt/the-sourdough-framework

COPY . .

CMD ["/bin/sh"]
