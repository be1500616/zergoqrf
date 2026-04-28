# Test Plan: Story 0.1 - Development Environment Setup

This document outlines the test plan for validating the development environment setup as described in Story 0.1.

## 1. Scope

This test plan covers all acceptance criteria outlined in Story 0.1, including the Docker environment, frontend setup, database configuration, and developer tooling.

## 2. Test Objectives

- Verify that the Docker environment can be started with a single command.
- Confirm that all services (backend, database, Redis) are running correctly.
- Validate that the backend provides a health check endpoint.
- Ensure the database is correctly seeded with initial data.
- Verify that the frontend development server runs on the correct port.
- Confirm that hot reload is functional for both backend and frontend.
- Validate that all developer tooling (linters, formatters, pre-commit hooks) is correctly configured.

## 3. Test Strategy

The testing will be conducted through a combination of manual checks and guided command-line execution. The QA agent will provide instructions, and the user will execute the commands and report the results.

## 4. Test Cases

| Test Case ID | Acceptance Criterion | Test Steps | Expected Result |
|--------------|----------------------|------------|-----------------|
| TC-001       | AC #5, #1, #2, #3, #4 | 1. Run `make dev`. | All Docker containers start without errors. |
| TC-002       | AC #8, #21           | 1. Run `curl http://localhost:8000/healthz`. | The command returns a `{"status": "ok"}` JSON response. |
| TC-003       | AC #13, #14          | 1. Inspect the logs of the `db` container. | The logs show that the migrations and seed data were successfully applied. |
| TC-004       | AC #10, #23          | 1. Run `make test`. | All tests pass successfully. |
| TC-005       | AC #7, #8, #9        | 1. Follow the instructions in `docs/flutter_setup.md` to run the frontend. | The Flutter web server starts on `localhost:3000`. |
| TC-006       | AC #17, #18, #19     | 1. Make a minor code change and attempt to commit it. | The pre-commit hooks run and enforce code formatting and linting. |
