.PHONY: install lint format test

VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

install:
	python3 -m venv --system-site-packages $(VENV)
	$(PIP) install -e . -q

lint:
	$(VENV)/bin/ruff check src/

format:
	$(VENV)/bin/ruff format src/

test:
	$(VENV)/bin/pytest tests/ -v
