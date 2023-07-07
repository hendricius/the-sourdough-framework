DOCKER_IMAGE := ghcr.io/hendricius/the-sourdough-framework

.PHONY: build_pdf
build_pdf: build_docker_image
	docker run -it -v $(PWD):/opt/repo $(DOCKER_IMAGE) /bin/bash -c "cd /opt/repo/book && make"

.PHONY: bake
bake: build_docker_image
	docker run -it -v $(PWD):/opt/repo $(DOCKER_IMAGE) /bin/bash -c "cd /opt/repo/book && make bake"

.PHONY: build_docker_image
build_docker_image:
	docker build -t $(DOCKER_IMAGE) -f Dockerfile .

.PHONY: push_docker_image
push_docker_image:
	docker push $(DOCKER_IMAGE):latest

.PHONY: website
website:
	docker run -it -v $(PWD):/opt/repo $(DOCKER_IMAGE) /bin/bash -c "cd /opt/repo/book && make website"
