.PHONY: check build serve llms

PYTHON ?= .venv/bin/python

check:
	./scripts/check_docs.sh

llms:
	$(PYTHON) scripts/generate_llms.py --write

build:
	$(PYTHON) -m mkdocs build --strict

serve:
	$(PYTHON) -m mkdocs serve
