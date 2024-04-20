.PHONY: help check-bootstrap-dependencies check-poetry check-tools check-docker bootstrap setup install update format poetry-check lint-check format-check type-check lint unit unit-coverage gcp-authenticate

POETRY_VERSION?=1.6
PYTHON_VERSION?=$(shell cat .python-version | tr -d '[:space:]')
NEXT_POETRY_VERSION:=$(shell echo $(POETRY_VERSION) | awk -F. '{print $$1 "." $$2+1}')
POETRY?=poetry@$(POETRY_VERSION)
VENV?=.venv
VENV_ACTIVATE=$(VENV)/bin/activate

RED="\033[0;31m"
CYAN="\033[36m"
NC="\033[0m"

## help: Prints the names and descriptions of all targets
help:
	@grep -E '## .*$$' $(MAKEFILE_LIST) | grep -v '@grep' | awk 'BEGIN {FS = ": "}; {sub(/^## /, "", $$1); printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

# check-bootstrap-dependencies: Check if bootstrap dependencies are installed
check-bootstrap-dependencies:
	@which pyenv >/dev/null || (echo $(RED)"Error: pyenv not found install this https://github.com/pyenv/pyenv and then do: make bootstrap"$(NC); exit 1)
	@which pipx >/dev/null || (echo $(RED)"Error: pipx not found https://pypa.github.io/pipx/installation/"$(NC); exit 1)

# check-poetry: Check if poetry is installed
check-poetry:
	@which $(POETRY) >/dev/null || (echo $(RED)"Error: $(POETRY) not found, try doing: make setup"$(NC); exit 1)

check-tools:
	@which gcloud > /dev/null || (echo $(RED)"Error: gcloud is not installed. Please install it from https://cloud.google.com/sdk/docs/quickstarts"$(NC); exit 1)
	@which gsutil > /dev/null || (echo $(RED)"Error: gsutil is not installed. Please install it from https://cloud.google.com/storage/docs/gsutil_install"$(NC); exit 1)
	@which docker > /dev/null || (echo $(RED)"Error: docker is not installed. Please install this and ensure its running"$(NC); exit 1)

check-docker:
	@echo "Checking if Docker CLI is available..."
	@which docker > /dev/null || (echo "Docker CLI not found. Please install Docker https://www.docker.com/get-started/"$(NC); exit 1;)
	@echo "Docker CLI is available."
	@echo "Checking if Docker is running..."
	@docker ps > /dev/null 2>&1 || (echo $(RED)"Error: Docker is not running. Please start the Docker daemon."$(NC); exit 1;)
	@echo "Docker is running."

## bootstrap: Install Python version and pipx
bootstrap:
	pyenv install $(PYTHON_VERSION)
	pyenv local $(PYTHON_VERSION)
	pip install --user pipx # installing pipx for external applications
	pipx ensurepath

## setup: Install poetry
setup: check-bootstrap-dependencies
	pipx install --suffix="@$(POETRY_VERSION)" "poetry>=$(POETRY_VERSION),<$(NEXT_POETRY_VERSION)"

$(VENV_ACTIVATE):
	$(POETRY) self add poetry-pre-commit-plugin
	$(POETRY) install --no-root
	$(POETRY) run pre-commit install -t pre-push

install: $(VENV_ACTIVATE)
	$(POETRY) install --no-root --sync

update: $(VENV_ACTIVATE)
	$(POETRY) lock
	$(POETRY) install --no-root
	@echo Dont forget to commit the updated lock file

format: $(VENV_ACTIVATE)
	$(POETRY) run ruff check --fix --exit-zero .
	$(POETRY) run ruff format .

poetry-check: $(VENV_ACTIVATE)
	$(POETRY) check

lint-check: $(VENV_ACTIVATE)
	$(POETRY) run ruff check .

format-check: $(VENV_ACTIVATE)
	$(POETRY) run ruff format --check .

type-check:
	$(POETRY) run mypy .

## lint: Run all lint checks
lint: poetry-check lint-check format-check type-check

## unit: Run unit tests
unit: $(VENV_ACTIVATE)
	$(POETRY) run pytest tests/unit

## unit-coverage: Run unit tests with coverage report
unit-coverage: $(VENV_ACTIVATE)
	$(POETRY) run coverage run -m pytest tests/unit
	$(POETRY) run coverage report
	$(POETRY) run coverage html

## gcp-authenticate: Authenticate with GCP, use this before running composer commands
gcp-authenticate:
	gcloud auth application-default login
	gcloud auth login

## dagster-start: Start the dagsetr deployment environment
dagster-start: $(VENV_ACTIVATE)
	$(POETRY) run dagster dev
