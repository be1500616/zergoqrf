# Capability: Multi-Tenant RLS Posture

## ADDED Requirements

### Requirement: RLS is the default on tenant-scoped tables

Every table in the tenant-scope list MUST have `rowsecurity = true` and at least one non-restrictive policy (`FOR SELECT`, `FOR ALL`, etc.) attached. The build MUST fail if either is missing.

The tenant-scope list at the time of this change is in `tests/fixtures/rls_tenant_scope.json`:

`restaurants`, `categories`, `menu_items`, `tables`, `qr_codes`, `orders`, `order_items`, `carts`, `cart_items`, `transactions`, `order_tracking`.

#### Scenario: a new tenant table is added without RLS

- **GIVEN** a developer adds `public.discounts` and forgets `alter table ... enable row level security`
- **WHEN** `make rls-check` runs (locally or in CI)
- **THEN** the command fails with a message naming the table, the missing flag, and the policy that should be added

#### Scenario: a tenant table has RLS but no policy

- **GIVEN** a developer adds `enable row level security` but forgets to add a `create policy`
- **WHEN** `make rls-check` runs
- **THEN** the command fails with a message naming the table and stating that `pg_policies` is empty for it

### Requirement: Cross-tenant isolation by RLS, not by application code

A user with a valid JWT for tenant A MUST NOT see, mutate, or delete rows belonging to tenant B. Enforcement MUST be at the database via RLS. The backend MUST NOT depend on application-layer filtering alone.

#### Scenario: owner A reads only own restaurant

- **GIVEN** two restaurants exist, owned by user A and user B respectively
- **WHEN** a user-scoped Supabase client authenticated as A calls `from('restaurants').select('*')`
- **THEN** the result set contains only A's restaurant row; the `service_role` connection is unaffected and still returns both rows for admin work

#### Scenario: cross-tenant write is denied

- **GIVEN** restaurant A's owner is authenticated
- **WHEN** they try to insert a `menu_items` row with `restaurant_id = B's restaurant id`
- **THEN** the insert is rejected by the `with check` clause of the RLS policy, and the API returns a 403-equivalent error to the client

### Requirement: RLS posture check is the local-run gate

`make rls-check` MUST run the `scripts/check_rls.py` script. The script connects with the service role, queries `pg_tables` for the tenant-scope list, asserts `rowsecurity = true` and `pg_policies` non-empty for each, and exits non-zero on the first violation with a single readable message.

#### Scenario: posture check in local dev

- **GIVEN** a developer runs `make rls-check` against `supabase start`
- **WHEN** the script connects and runs its assertions
- **THEN** the result is green (no violations) or red (one violation printed, exit code 1)

### Requirement: RLS posture check is the CI gate (parked follow-up)

Promotion of the integration with CI is a separate small change. When promoted, the check MUST run as a blocking job in CI, gated on a reachable `DATABASE_URL` and the active profile being `test` or `prod`. The local-run gate is the primary defense in this change.

#### Scenario: posture check in CI (when promoted)

- **GIVEN** the CI workflow is updated
- **WHEN** the `rls-posture` job runs
- **THEN** the check applies against a fresh schema, runs the posture assertions, and reports pass/fail with the offending table name

### Requirement: Tenant-scope list is data, not code

The tenant-scope table list MUST live in `tests/fixtures/rls_tenant_scope.json`. The script reads it; the test reads it. The list is the single source of truth for which tables are checked.

#### Scenario: a new tenant table is added to the list

- **GIVEN** a developer adds `refunds` to `tests/fixtures/rls_tenant_scope.json`
- **WHEN** `make rls-check` runs
- **THEN** the script checks `refunds` along with the rest of the list, and the test `test_rls_tenant_isolation.py` confirms the new entry is loaded

#### Scenario: a non-tenant table is added to the list by mistake

- **GIVEN** a developer adds `public.supabase_migrations` to the tenant-scope list
- **WHEN** `make rls-check` runs
- **THEN** the script either asserts RLS on a Supabase-internal schema (which is correct) or fails because the table is not in the developer's schema. The error message names the table and points at the list file.

### Requirement: `test_rls_tenant_isolation.py` covers the script

`tests/test_rls_tenant_isolation.py` MUST be a Tier A test. It covers the script's pure-Python paths: argument parsing, scope loading, query construction, and the violation message format. It MUST NOT require a live DB.

#### Scenario: the script's query construction regresses

- **GIVEN** a developer changes the SQL query in `scripts/check_rls.py`
- **WHEN** `pytest` runs
- **THEN** `test_rls_tenant_isolation.py` catches the regression in the query string and reports the diff
