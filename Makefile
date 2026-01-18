#* Variables
SHELL := /usr/bin/env bash
PYTHON := python
PYTHONPATH := `pwd`

#* UV
.PHONY: uv-download
uv-download:
	brew install uv
	uv --version

#* Installation
.PHONY: install
install:
	uv sync
	-uv run mypy --install-types --non-interactive ./

.PHONY: pre-commit-install
pre-commit-install:
	uv run pre-commit install

#* Formatters
.PHONY: codestyle
codestyle:
	uv run pyupgrade --exit-zero-even-if-changed --py38-plus **/*.py
	uv run isort --settings-path pyproject.toml ./
	uv run black --config pyproject.toml ./

.PHONY: formatting
formatting: codestyle

#* Linting
.PHONY: test
test:
	PYTHONPATH=$(PYTHONPATH) uv run pytest -c pyproject.toml --cov-report=html --cov=qualifire tests/
	uv run coverage-badge -o assets/images/coverage.svg -f

.PHONY: check-codestyle
check-codestyle:
	uv run isort --diff --check-only --settings-path pyproject.toml ./
	uv run black --diff --check --config pyproject.toml ./
	uv run darglint --verbosity 2 qualifire tests

.PHONY: mypy
mypy:
	uv run mypy --config-file pyproject.toml ./

.PHONY: check-safety
check-safety:
	uv run safety check --full-report
	uv run bandit -ll --skip B113 --recursive qualifire tests

.PHONY: lint
lint: test check-codestyle mypy check-safety

.PHONY: update-dev-deps
update-dev-deps:
	uv add --dev bandit@latest darglint@latest "isort[colors]@latest" mypy@latest pre-commit@latest pydocstyle@latest pylint@latest pytest@latest pyupgrade@latest safety@latest coverage@latest coverage-badge@latest pytest-html@latest pytest-cov@latest
	uv add --dev --prerelease=allow black@latest


#* Cleaning
.PHONY: pycache-remove
pycache-remove:
	find . | grep -E "(__pycache__|\.pyc|\.pyo$$)" | xargs rm -rf

.PHONY: dsstore-remove
dsstore-remove:
	find . | grep -E ".DS_Store" | xargs rm -rf

.PHONY: mypycache-remove
mypycache-remove:
	find . | grep -E ".mypy_cache" | xargs rm -rf

.PHONY: ipynbcheckpoints-remove
ipynbcheckpoints-remove:
	find . | grep -E ".ipynb_checkpoints" | xargs rm -rf

.PHONY: pytestcache-remove
pytestcache-remove:
	find . | grep -E ".pytest_cache" | xargs rm -rf

.PHONY: build-remove
build-remove:
	rm -rf build/ dist/

.PHONY: cleanup
cleanup: pycache-remove dsstore-remove mypycache-remove ipynbcheckpoints-remove pytestcache-remove

#* Build
.PHONY: build
build:
	uv build

.PHONY: build-wheel
build-wheel:
	uv build --wheel

.PHONY: build-sdist
build-sdist:
	uv build --sdist
