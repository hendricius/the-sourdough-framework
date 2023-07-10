DOCKER_IMAGE := ghcr.io/hendricius/the-sourdough-framework

.PHONY: build_pdf
build_pdf: mrproper
	docker run -it -v $(PWD):/opt/repo $(DOCKER_IMAGE) /bin/bash -c "cd /opt/repo/book && make"

.PHONY: bake
bake: mrproper
	docker run -it -v $(PWD):/opt/repo $(DOCKER_IMAGE) /bin/bash -c "cd /opt/repo/book && make bake"

.PHONY: build_docker_image
build_docker_image:
	docker build -t $(DOCKER_IMAGE) -f Dockerfile --progress=plain .

.PHONY: push_docker_image
push_docker_image:
	docker push $(DOCKER_IMAGE):latest

.PHONY: website
website: mrproper
	docker run -it -v $(PWD):/opt/repo $(DOCKER_IMAGE) /bin/bash -c "cd /opt/repo/book && make website"

.PHONY: validate
validate: mrproper
	docker run -it -v $(PWD):/opt/repo $(DOCKER_IMAGE) /bin/bash -c "cd /opt/repo/book && make -j build_pdf build_serif_ebook"

.PHONY: mrproper
mrproper:
	docker run -it -v $(PWD):/opt/repo $(DOCKER_IMAGE) /bin/bash -c "cd /opt/repo/book && make mrproper"

.PHONY: show_tools_version
show_tools_version:
	docker run -it -v $(PWD):/opt/repo $(DOCKER_IMAGE) /bin/bash -c "cd /opt/repo/book && make show_tools_version"

.PHONY: printvars
printvars:
	docker run -it -v $(PWD):/opt/repo $(DOCKER_IMAGE) /bin/bash -c "cd /opt/repo/book && make printvars"

.PHONY: start_shell
start_shell:
	docker run -it -v $(PWD):/opt/repo $(DOCKER_IMAGE) /bin/bash
