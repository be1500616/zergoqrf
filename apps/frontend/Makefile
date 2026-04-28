# ZERGO QR Frontend Makefile
# Flutter development and testing commands

.PHONY: help get build test test-unit test-widget test-integration test-golden test-cov clean format lint analyze

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

get: ## Get Flutter dependencies
	flutter pub get

build: ## Build the Flutter app
	flutter build apk --debug

test: ## Run all tests
	flutter test

test-unit: ## Run unit tests only
	flutter test test/unit/

test-widget: ## Run widget tests only
	flutter test test/widget/

test-integration: ## Run integration tests
	flutter test integration_test/

test-golden: ## Run golden tests
	flutter test test/golden/

test-golden-update: ## Update golden files
	flutter test --update-goldens test/golden/

test-cov: ## Run tests with coverage
	flutter test --coverage
	@echo "Coverage report generated in coverage/lcov.info"
	@echo "To generate HTML report, run: genhtml coverage/lcov.info -o coverage/html"

test-cov-html: ## Generate HTML coverage report
	flutter test --coverage
	genhtml coverage/lcov.info -o coverage/html --remove-function-coverage
	@echo "HTML coverage report generated in coverage/html/index.html"

test-watch: ## Run tests in watch mode
	flutter test --watch

format: ## Format code
	dart format lib/ test/ integration_test/

format-check: ## Check code formatting
	dart format --set-exit-if-changed lib/ test/ integration_test/

lint: ## Run linting
	flutter analyze

analyze: ## Run static analysis
	flutter analyze --fatal-infos --fatal-warnings

clean: ## Clean build artifacts
	flutter clean
	rm -rf coverage/

clean-get: clean get ## Clean and get dependencies

dev-setup: get ## Setup development environment
	@echo "Flutter development environment setup complete!"
	@echo "Run 'make test' to run all tests"
	@echo "Run 'make test-cov' for test coverage"

ci-test: format-check analyze test-cov ## Run all CI checks
	@echo "All CI checks passed!"

run-debug: ## Run app in debug mode
	flutter run --debug

run-release: ## Run app in release mode
	flutter run --release

run-web: ## Run app in web mode
	flutter run -d chrome
