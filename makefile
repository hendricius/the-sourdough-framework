.DEFAULT_GOAL := pdf

DOCKER_IMAGE := ghcr.io/hendricius/the-sourdough-framework
DOCKER_CMD := docker run --rm -it -v $(PWD):/opt/repo --platform linux/x86_64 $(DOCKER_IMAGE) /bin/bash -c

.PHONY: build_docker_image push_docker_image
.PHONY: print_os_version start_shell printvars show_tools_version mrproper
.PHONY: ebook serif website bake

# Dockers targets
build_docker_image:
	docker build -t $(DOCKER_IMAGE) -f Dockerfile --progress=plain .

push_docker_image: build_docker_image
	docker push $(DOCKER_IMAGE):latest

# Books/website
serif:
	$(DOCKER_CMD) "cd /opt/repo/book && make serif"

ebook:
	$(DOCKER_CMD) "cd /opt/repo/book && make ebook"

pdf:
	$(DOCKER_CMD) "cd /opt/repo/book && make"

bake:
	$(DOCKER_CMD) "cd /opt/repo/book && make bake"

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
