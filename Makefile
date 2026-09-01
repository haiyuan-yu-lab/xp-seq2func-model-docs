.PHONY: check build serve

PYTHON ?= .venv/bin/python

check:
	./scripts/check_docs.sh

build:
	$(PYTHON) -m mkdocs build --strict

serve:
	$(PYTHON) -m mkdocs serve
