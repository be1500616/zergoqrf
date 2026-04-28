## 1. Profile and Runtime Contract

- 1.1 Define profile mapping for Supabase `dev`/`test`/`prod`.
- 1.2 Define required environment variables and fail-fast startup validation per profile.
- 1.3 Enforce separation of credentials and data across `dev`, `test`, and `prod`.

## 2. Supabase Development and Testing Workflow

- 2.1 Set default developer workflow to Supabase `dev`.
- 2.2 Route CI/integration and destructive tests to Supabase `test` only.
- 2.3 Add migration promotion flow `dev -> test -> prod` with release-gate checks.

## 3. Optional Local Postgres Runtime

- 3.1 Document local Postgres bootstrap command and usage boundaries.
- 3.2 Ensure local profile is optional and does not block normal Supabase-first development.
- 3.3 Define when developers should use local Postgres (offline only, quick schema/testing loop).

## 4. Queueing and Messaging Strategy

- 4.1 Define Postgres-backed queue pattern for current product workflows.
- 4.2 Define queue SLO thresholds (throughput, latency, retry backlog) that trigger RabbitMQ adoption.
- 4.3 Add operational monitoring for queue depth, retry count, and worker lag.

## 5. Security and Validation

- 5.1 Keep RLS verification checks as required release gates for Supabase environments.
- 5.2 Add migration-order audit to prevent weaker policies from reappearing.
- 5.3 Validate OpenSpec change in strict mode and record follow-up decisions.