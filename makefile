.PHONY: build_book
build_book: build_docker_image
	docker run -it -v $(PWD):/opt/repo the-sourdough-framework /bin/bash -c "cd /opt/repo/book && make build_pdf"

.PHONY: release
release: build_docker_image
	docker run -it -v $(PWD):/opt/repo the-sourdough-framework /bin/bash -c "cd /opt/repo/book && make build_pdf"

.PHONY: build_docker_image
build_docker_image:
	docker build -t the-sourdough-framework -f Dockerfile .
