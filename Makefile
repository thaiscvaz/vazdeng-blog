.PHONY: help validate validate-strict validate-file dev build clean

POSTS_DIR := content/blog
PY := python

help:
	@echo "Targets:"
	@echo "  validate         Roda validate_post.py em todos os posts (gate score >= 8)"
	@echo "  validate-strict  Igual, mas warnings tambem reprovam"
	@echo "  validate-file F=path/to/index.md  Valida arquivo unico"
	@echo "  dev              hugo server local (porta 1313)"
	@echo "  build            hugo build em public/"
	@echo "  clean            Remove public/ e resources/_gen/"

validate:
	$(PY) scripts/validate_post.py $(POSTS_DIR)

validate-strict:
	$(PY) scripts/validate_post.py $(POSTS_DIR) --strict

validate-file:
	@if [ -z "$(F)" ]; then echo "Uso: make validate-file F=content/blog/.../index.md"; exit 1; fi
	$(PY) scripts/validate_post.py $(F)

dev:
	hugo server --buildDrafts --buildFuture -p 1313

build:
	hugo --minify

clean:
	rm -rf public resources/_gen
