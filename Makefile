# Project Variables
PYTHON = python3
VENV = .amazeing
BIN = $(VENV)/bin
PIP = $(BIN)/pip
PY = $(BIN)/python
MAIN = main.py
CONFIG = config.txt

# Mandatory Rules

.PHONY: venv
venv:
	test -d $(VENV) || $(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip

.PHONY: install
install: venv
	$(PIP) install flake8 mypy build setuptools wheel

.PHONY: run
run:
	$(PY) $(MAIN) $(CONFIG)

.PHONY: debug
debug:
	$(PY) -m pdb $(MAIN) $(CONFIG)

.PHONY: clean
clean:
	rm -rf $(VENV)
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .mypy_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

.PHONY: lint
lint:
	$(BIN)/flake8 .
	$(BIN)/mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

.PHONY: lint-strict
lint-strict:
	$(BIN)/flake8 .
	$(BIN)/mypy . --strict

.PHONY: build
build: venv clean-build
	$(PY) -m build
	cp dist/*.whl .
	cp dist/*.tar.gz .

.PHONY: clean-build
clean-build:
	rm -rf build/ dist/ *.egg-info