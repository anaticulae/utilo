.PHONY: docker-build docker-run build clean

VERSION := $(shell git rev-parse --short HEAD 2>/dev/null || echo "latest")
CURDIR := $(CURDIR)

NAME = utilo
IMAGE := $(NAME):$(VERSION)
IMAGE_BASE := ghcr.io/anaticulae/$(IMAGE)

docker-build:
	docker build -t $(IMAGE_BASE) .

docker-upload:
	docker push $(IMAGE_BASE)

docker-doctest: docker-build
	docker run -v $(CURDIR):/var/workdir $(IMAGE_BASE) "baw test docs"

docker-fasttest: docker-build
	docker run -v $(CURDIR):/var/workdir $(IMAGE_BASE) "baw test fast"

docker-longtest: docker-build
	docker run -v $(CURDIR):/var/workdir $(IMAGE_BASE) "baw test long"

docker-alltest: docker-build
	docker run -v $(CURDIR):/var/workdir $(IMAGE_BASE) "baw test all"

docker-lint: docker-build
	docker run -v $(CURDIR):/var/workdir $(IMAGE_BASE) "baw lint all"

docker-release: docker-build
	@if git describe --exact-match --tags HEAD >/dev/null 2>&1; then\
		echo "Current commit is already tagged. Skipping release."; \
	else \
		docker run \
			-v $(CURDIR):/var/workdir \
			-e GH_TOKEN \
			$(IMAGE_BASE) \
			"baw release --no_test --no_linter"; \
	fi
