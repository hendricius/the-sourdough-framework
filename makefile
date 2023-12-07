.DEFAULT_GOAL := build_pdf

DOCKER_IMAGE := ghcr.io/hendricius/the-sourdough-framework
DOCKER_CMD := docker run -it -v $(PWD):/opt/repo $(DOCKER_IMAGE) /bin/bash -c

.PHONY: bake build_pdf build_docker_image push_docker_image validate website
.PHONY: print_os_version start_shell printvars show_tools_version mrproper

# Dockers targets
build_docker_image:
	docker build -t $(DOCKER_IMAGE) -f Dockerfile --progress=plain .

push_docker_image: build_docker_image
	docker push $(DOCKER_IMAGE):latest

# Books/website
build_serif_pdf:
	$(DOCKER_CMD) "cd /opt/repo/book && make build_serif_pdf"

build_ebook:
	$(DOCKER_CMD) "cd /opt/repo/book && make build_ebook"

build_pdf:
	$(DOCKER_CMD) "cd /opt/repo/book && make"

bake:
	$(DOCKER_CMD) "cd /opt/repo/book && make -j bake"

website:
	$(DOCKER_CMD) "cd /opt/repo/book && make website"

mrproper:
	$(DOCKER_CMD) "cd /opt/repo/book && make mrproper"

# Debug helpers
show_tools_version:
	$(DOCKER_CMD) "cd /opt/repo/book && make show_tools_version"

printvars:
	$(DOCKER_CMD) "cd /opt/repo/book && make printvars"

print_os_version:
	$(DOCKER_CMD) "cat /etc/*release"

start_shell:
	docker run -it -v $(PWD):/opt/repo $(DOCKER_IMAGE) /bin/bash
