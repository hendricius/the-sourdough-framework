.DEFAULT_GOAL := pdf

DOCKER_IMAGE := ghcr.io/hendricius/the-sourdough-framework
DOCKER_CMD := docker run --rm -it -v $(PWD):/opt/repo --platform linux/x86_64 $(DOCKER_IMAGE) /bin/bash -c

.PHONY: build_docker_image push_docker_image
.PHONY: print_os_version start_shell printvars show_tools_version mrproper
.PHONY: ebook serif website bake pr

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

# Push this branch and open a pull request against main, never a push to main:
# make pr [TITLE="..." BODY=file.md]
pr:
	@branch=$$(git rev-parse --abbrev-ref HEAD); \
	if [ "$$branch" = "main" ]; then echo "On main, which is not pushed to. Branch first: git switch -c <what-it-does>"; exit 1; fi; \
	git push -u origin "$$branch" && (gh pr view --json url -q .url 2>/dev/null || \
	  gh pr create --base main --head "$$branch" $(if $(TITLE),--title "$(TITLE)" --body-file "$(BODY)",--fill))
