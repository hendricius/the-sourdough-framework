PHONY: build_pdf
build_pdf: build_docker_image
	docker run -it -v $(PWD):/opt/repo the-sourdough-framework /bin/bash -c "cd /opt/repo/book && make build_pdf"

.PHONY: bake
bake: build_docker_image
	docker run -it -v $(PWD):/opt/repo the-sourdough-framework /bin/bash -c "cd /opt/repo/book && make bake"

.PHONY: build_docker_image
build_docker_image:
	docker build -t the-sourdough-framework -f Dockerfile .
