# ZERGO QR Backend Makefile
# Development and testing commands

.PHONY: help install install-dev test test-cov test-unit test-integration lint format clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install production dependencies
	pip install -e .

install-dev: ## Install development dependencies
	pip install -e ".[dev]"

test: ## Run all tests
	pytest -v

test-cov: ## Run tests with coverage
	pytest --cov=app --cov-report=term-missing --cov-report=html:htmlcov --cov-fail-under=90 -v

test-unit: ## Run unit tests only
	pytest -v -m unit

test-integration: ## Run integration tests only
	pytest -v -m integration

test-watch: ## Run tests in watch mode
	pytest-watch

lint: ## Run linting
	flake8 app tests
	mypy app

format: ## Format code
	black app tests
	isort app tests

format-check: ## Check code formatting
	black --check app tests
	isort --check-only app tests

clean: ## Clean up generated files
	rm -rf __pycache__ .pytest_cache .coverage htmlcov .mypy_cache
	rm -rf *.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

dev-setup: install-dev ## Setup development environment
	@echo "Development environment setup complete!"
	@echo "Run 'make test' to run tests"
	@echo "Run 'make test-cov' to run tests with coverage"

ci-test: format-check lint test-cov ## Run all CI checks
