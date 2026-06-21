# ZERGO Backend Capability Audit & Roadmap

**Date:** 2026-06-20
**Scope:** `apps/backend` (FastAPI + Supabase)
**Purpose:** Establish what's actually built, what's reachable, and what to ship next.

---

## Executive Summary

The ZERGO backend has substantial code already written — **82% of feature folders have business logic** (use cases + repositories), and the test suite holds ~165 tests across 30 files. But only **36% of features are reachable from the running API** because six feature routers exist, are tested, and are simply not mounted in `app/main.py`.

The dominant pattern is **"built-but-unwired"**: complete routers, complete use cases, complete repos, complete tests — but no path from the URL to the code. The single highest-leverage move is to mount the missing routers.

There is also a small amount of **dead code** (SQLAlchemy stack declared but never imported) and **duplicate routers** (`auth_router.py` and `supabase_auth_router.py`, both present, only one mounted). These should be removed or committed to.

### Headline numbers

| Metric | Value |
|---|---|
| Feature folders | 11 |
| Reachable from API today | 4 (36%) |
| With business logic implemented | 9 (82%) |
| With tests | 7 (64%) |
| Endpoint definitions total | ~78 |
| Endpoint definitions mounted | ~15 |
| Test files | 30 |
| Estimated tests | ~165 |
| Persistence: Supabase / SQLAlchemy | 14 / 1 (dead) |

---

## 1. Capability Matrix

Status legend:
- **SHIPPED** — router mounted, use cases + repo + tests in place
- **PARTIAL** — use cases and repo exist, but the mounted router bypasses them
- **STUB** — minimal router, no use cases, no domain
- **BUILT, UNWIRED** — full implementation (router, use cases, repo, often tests), but `app/main.py` doesn't include the router

| Feature | Mounted | Endpoints | Use cases | Repo | Tests | Status |
|---|---|---:|---|---|---|---|
| `auth` | ✅ (legacy only) | 5 + 10 | 9 | 2 | ~70 | SHIPPED — duplicate router unresolved |
| `public_menu` | ✅ | 6 | 2 | 1 | ~10 | SHIPPED |
| `orders` | ✅ | 1 | 4 | 2 | ~25 | PARTIAL — RPC shim, use cases dead |
| `menu` | ✅ | 1 | 1 | 1 | 0 | STUB — router bypasses repo |
| `admin` | ✅ | 1 | 0 | 0 | 0 | STUB — inline insert, duplicates restaurants |
| `restaurants` | ❌ | 12 | 2 | 1 | ~20 | BUILT, UNWIRED |
| `tables` | ❌ | 13 | 5 | 1 | ~9 | BUILT, UNWIRED |
| `cart` | ❌ | 13 | 3 | 2 | ~25 | BUILT, UNWIRED |
| `qr` | ❌ | 4 | 3 | 2 | ~8 | BUILT, UNWIRED |
| `order_tracking` | ❌ | 9 | 3 | 2 | 0 | BUILT, UNWIRED — has `_Noop*Service` classes |
| `transaction_management` | ❌ | 12 | 6 | 1 | 0 | BUILT, UNWIRED — no payment gateway adapter |

### Feature details

#### `auth` — SHIPPED (with duplication)
- **Mounted:** yes, in `app/main.py:49` via `auth_router` (prefix `/api/v1/auth`)
- **Endpoints:** 5 in `auth_router.py` (signup, signin, anonymous-session, refresh, /me) + 10 in `supabase_auth_router.py` (email/phone/verify/refresh/me/profile/signout/validate-restaurant-code)
- **Use cases:** 9 files in `application/use_cases/`
- **Repository:** `auth_repos_impl.py` + `supabase_auth_repository.py`
- **Tests:** 6 top-level auth files + `tests/features/auth/test_supabase_auth_router.py` + `tests/integration/test_auth_security_fixes.py` + `test_real_supabase_auth.py`
- **Issues:**
  - `main.py` imports `auth_router` only; `supabase_auth_router` is built and tested but **not mounted**
  - `auth_router.py:270-277` `GET /me` returns 501
  - `auth_repos.py` has 30+ `pass` placeholders (abstract interface methods)
- **Next step:** Pick one canonical auth surface, mount it, delete the other

#### `public_menu` — SHIPPED
- **Mounted:** yes (`app/main.py:52`, prefix `/api/v1`)
- **Endpoints:** 6 (`GET /{restaurant_code}`, search, featured, plus category/menu paths)
- **Use cases:** `get_public_menu.py`, `search_menu_items.py`
- **Repository:** `public_menu_repos_impl.py`
- **Tests:** `tests/api/test_public_menu_api.py` (~8), `tests/integration/test_public_menu_integration.py` (~2)
- **Issues:** none critical
- **Next step:** verify search relevance + RLS on public access

#### `orders` — PARTIAL
- **Mounted:** yes (`app/main.py:51`, prefix `/api/v1/orders`)
- **Endpoints:** 1 (`POST /`) — RPC-backed shim
- **Use cases:** 4 (`order_creation_use_cases.py`, `order_status_use_cases.py`, `payment_collection_use_cases.py`, `restaurant_orders_use_cases.py`) — **none wired to the mounted router**
- **Repository:** `order_repos_impl.py` (Supabase); `order_models.py` (SQLAlchemy, unused)
- **Tests:** covered transitively via cart tests (~25 across cart+orders)
- **Issues:** the mounted router calls `supabase.rpc("create_order_from_cart", ...)` directly, bypassing the 4 use cases
- **Next step:** Either wire the use cases or delete them — pick one

#### `menu` — STUB
- **Mounted:** yes (`app/main.py:50`, prefix `/api/v1/menu`)
- **Endpoints:** 1 (`GET /items`) — placeholder
- **Use cases:** `menu_publishing_use_case.py`
- **Repository:** `menu_repos_impl.py` — **defined but not wired to router**
- **Tests:** none
- **Issues:** mounted router is a 24-line placeholder; the real use case + repo exist but are bypassed
- **Next step:** replace the stub router with one that delegates to `GetMenuUseCase` against `menu_repos_impl`

#### `admin` — STUB
- **Mounted:** yes (`app/main.py:53-58`, prefix `/api/v1/admin`)
- **Endpoints:** 1 (`POST /restaurants`)
- **Use cases:** none
- **Repository:** none
- **Tests:** none
- **Issues:** entire router is a 19-line inline handler that does `sb.table("restaurants").insert(payload.model_dump()).execute()` with no auth, no DTO, no use case — functionally a duplicate of `restaurants/presentation/restaurant_router.register_restaurant`
- **Next step:** Decide what admin actually means (system control panel? restaurant impersonation? data fixes?) and either build it or delete it

#### `restaurants` — BUILT, UNWIRED
- **Mounted:** **no**
- **Endpoints:** 12 (registration, get/update restaurant, business hours, settings, staff CRUD)
- **Use cases:** `create_restaurant.py`, `create_staff.py`
- **Repository:** `restaurant_repos_impl.py`
- **Tests:** extensive (~20 across `test_restaurant_api_comprehensive.py`, `test_restaurant_endpoints.py`, `test_restaurant_registration.py`, `test_restaurant_api_simple.py`)
- **Issues:** none critical; one `pass` in exception path (`create_restaurant.py:160`)
- **Next step:** **mount in `main.py`** — 12 endpoints + 20 tests go live at zero design cost

#### `tables` — BUILT, UNWIRED
- **Mounted:** **no**
- **Endpoints:** 13 (floors CRUD, floor plan, tables CRUD, status, occupancy stats)
- **Use cases:** 5 (`create_table`, `get_tables`, `manage_floor_plan`, `update_table`, `update_table_status`)
- **Repository:** `table_repos_impl.py` (includes `FloorRepositoryImpl`)
- **Tests:** `tests/api/test_table_management_api.py` (~9)
- **Issues:** `domain/table_repos.py` has 30+ `pass` interface stubs
- **Next step:** mount the router

#### `cart` — BUILT, UNWIRED
- **Mounted:** **no**
- **Endpoints:** 13 (sessions anon/auth/get/extend/migrate, items add/update/remove/get/clear, summary, validate-prices, validate-price)
- **Use cases:** 3 (`cart_item`, `cart_session`, `cart_summary`)
- **Repository:** `cart_item_repos_impl.py`, `cart_session_repos_impl.py`
- **Tests:** 6 files in `tests/features/test_cart_*.py`
- **Issues:**
  - `cart_router.py:336,443` — `user_id: UUID = Depends()` placeholder, no auth dependency actually wired
  - `cart_router.py:67` defines prefix `/api/v1/cart` inline, conflicting with centralized prefix pattern in `main.py`
- **Next step:** mount the router, fix prefix conflict, wire real auth dependency

#### `qr` — BUILT, UNWIRED
- **Mounted:** **no**
- **Endpoints:** 4 (generate, bulk, preview, management grid)
- **Use cases:** 3 (`generate_qr_code`, `generate_bulk_qr`, `get_qr_management_data`)
- **Repository:** `qr_generation_service.py`, `qr_repos_impl.py`
- **Tests:** `tests/api/test_qr_generation_api.py` (~7), `tests/core/test_qr_generation_core.py` (~1)
- **Issues:** none critical
- **Next step:** mount the router

#### `order_tracking` — BUILT, UNWIRED (with stubs)
- **Mounted:** **no**
- **Endpoints:** 9 (order tracking, status updates, notifications, metrics)
- **Use cases:** 3 (`get_order_tracking`, `send_notification`, `update_order_status`)
- **Repository:** `order_tracking_repos_impl.py`, `realtime_service.py`
- **Tests:** none
- **Issues:**
  - `order_tracking_router.py:60-77` defines `_NoopEmailService`, `_NoopWhatsAppService`, `_NoopSMSService` — all return `True`
  - Lines 424, 610 have commented-out `Depends()` for use cases — no real impl
  - `order_tracking_repos.py` has 35+ `pass` interface stubs
  - `realtime_service.py:378` `pass` in error path
- **Next step:** mount after replacing Noop services with real adapters behind a port

#### `transaction_management` — BUILT, UNWIRED (blocked on adapter)
- **Mounted:** **no**
- **Endpoints:** 12 (transactions CRUD, payment processing, refunds, history, financial reports, payouts)
- **Use cases:** 6 (`create_transaction`, `generate_financial_report`, `get_transaction_history`, `get_transaction_summary`, `process_payment`, `process_refund`)
- **Repository:** `transaction_repos_impl.py`
- **Tests:** none
- **Issues:**
  - `transaction_router.py:1150` returns 501 for PDF export
  - `domain/payment_gateway_interfaces.py` defines port interfaces but no concrete gateway adapter is bound
- **Next step:** bind a real payment gateway (Razorpay for India/UPI) before mounting

---

## 2. Tests Inventory

| File | Tests (~) | Targets |
|---|---|---|
| `tests/test_health.py` | 1 | `main.py` healthz |
| `tests/test_main.py` | 2 | app bootstrap |
| `tests/test_security.py` | 2 | `app/security.py` JWT verify |
| `tests/test_auth.py` | 10 | auth router flows |
| `tests/test_auth_domain.py` | 19 | auth value objects (`Email`, `Password`, `PhoneNumber`, `User`, `AuthSession`) |
| `tests/test_auth_use_cases.py` | 10 | auth use cases |
| `tests/test_auth_working.py` | 7 | auth happy paths |
| `tests/test_auth_fixed.py` | 7 | auth re-runs |
| `tests/test_auth_api_integration.py` | 9 | auth API integration |
| `tests/test_restaurant_registration.py` | 3 | restaurant registration workflow |
| `tests/test_restaurant_api_comprehensive.py` | 9 | restaurants (register/get/update/staff) |
| `tests/test_restaurant_endpoints.py` | 8 | restaurants endpoints (script-style) |
| `tests/api/test_endpoints.py` | 1 | auth endpoints smoke |
| `tests/api/test_public_menu_api.py` | 8 | public_menu |
| `tests/api/test_qr_generation_api.py` | 7 | qr |
| `tests/api/test_table_management_api.py` | 9 | tables |
| `tests/core/test_qr_generation_core.py` | 1 | qr core |
| `tests/integration/test_auth_security_fixes.py` | 14 | auth security |
| `tests/integration/test_real_supabase_auth.py` | 11 | real Supabase auth (integration) |
| `tests/integration/test_public_menu_integration.py` | 2 | public_menu integration |
| `tests/integration/test_restaurant_api_simple.py` | 5 | restaurants smoke |
| `tests/features/auth/test_supabase_auth_router.py` | 14 | `supabase_auth_router` (not mounted) |
| `tests/features/test_cart_and_orders_api_comprehensive.py` | 12 | cart+orders |
| `tests/features/test_cart_orders_api_end_to_end.py` | 8 | cart+orders e2e |
| `tests/features/test_cart_orders_api_execution.py` | 3 | cart+orders execution |
| `tests/features/test_cart_orders_api_final.py` | 1 | cart+orders |
| `tests/features/test_cart_orders_api_simple.py` | 1 | cart+orders |
| `tests/features/test_cart_and_orders_api_validation.py` | 0 | empty |
| `tests/features/test_api_simple.py` | 1 | simple |
| `tests/config/test_config.py` | 0 | empty |
| `tests/test_utils.py` | 0 | helpers only |

**Total:** ~165 tests across 30 files.

### Coverage gaps

- **No tests:** `admin`, `menu`, `order_tracking`, `transaction_management`
- **Duplicate auth test files:** 6 files cover the same auth surface (`test_auth*.py`)
- **Empty files:** `tests/features/test_cart_and_orders_api_validation.py`, `tests/config/test_config.py`

---

## 3. Persistence Layer

### Reality

| Impl file | Persistence |
|---|---|
| `auth/infrastructure/auth_repos_impl.py` | Supabase |
| `auth/infrastructure/supabase_auth_repository.py` | Supabase |
| `cart/infrastructure/cart_item_repos_impl.py` | Supabase |
| `cart/infrastructure/cart_session_repos_impl.py` | Supabase |
| `menu/infrastructure/menu_repos_impl.py` | Supabase |
| `order_tracking/infrastructure/order_tracking_repos_impl.py` | Supabase |
| `order_tracking/infrastructure/realtime_service.py` | Supabase realtime |
| `orders/infrastructure/order_models.py` | SQLAlchemy models (no consumer) |
| `orders/infrastructure/order_repos_impl.py` | Supabase |
| `public_menu/infrastructure/public_menu_repos_impl.py` | Supabase |
| `qr/infrastructure/qr_generation_service.py` | local QR lib + Supabase storage |
| `qr/infrastructure/qr_repos_impl.py` | Supabase |
| `restaurants/infrastructure/restaurant_repos_impl.py` | Supabase |
| `tables/infrastructure/table_repos_impl.py` | Supabase |
| `transaction_management/infrastructure/transaction_repos_impl.py` | Supabase |

**Result:** 14 of 15 impl files use Supabase (`Client` or `AClient`). The 1 outlier (`orders/infrastructure/order_models.py`) defines SQLAlchemy models that nothing imports.

### `core/database.py` audit

`app/core/database.py` defines:
- `engine` (SQLAlchemy async)
- `AsyncSessionLocal`
- `get_db_session()` dependency
- `Base` declarative class
- `DATABASE_URL` (read from `settings.database_url`, which is **not declared in `Settings`**)

**Imported by:** `app/core/database.py` only. No feature code, no scripts, no tests reference `get_db_session`, `engine`, or `Base`.

**Verdict:** Dead infrastructure. The `sqlalchemy[asyncpg]` and `asyncpg` dependencies in `pyproject.toml` are paying for code that runs nowhere.

### `core/config.py`

Active and load-bearing. Imported by `main.py`, `supabase_client.py`, `security.py`, all routers, all infra files.

---

## 4. Cross-Cutting Concerns

### Authentication

- `app/security.py` defines `verify_supabase_jwt` and `get_current_tenant`
- `verify_supabase_jwt` uses Supabase Auth — calls `supabase.auth.get_user(token)` per request
- `get_current_tenant` requires `X-Tenant-Id` header — currently used by only one router and not propagated by the Supabase client
- **Risk:** tenant isolation today relies on a header, not a JWT claim. RLS mistakes could leak data across restaurants.

### Error handling

- `AppError` base + `app_error_handler` registered in `app/main.py:60`
- Per-feature auth exception handlers in `features/auth/presentation/auth_exception_handlers.py`

### Middleware

- `app/middleware/error_handling.py`
- `app/middleware/security.py`
- CORS via `CORSMiddleware` configured with `settings.allowed_origins`

### Observability

- `sentry-sdk[fastapi]` declared in `pyproject.toml`
- `structlog>=24.1.0` for structured logging
- No trace propagation across use cases yet

---

## 5. Roadmap

Five phases, each with a single decision gate before moving on. Sequenced by lowest cost × highest unlock.

### Phase 1 — Wire the free wins

**Goal:** Unlock ~50 endpoints that are already built and tested.

**Tasks:**

1. **Mount four unwired routers** in `app/main.py`:
   - `cart_router` (13 endpoints, 25 tests)
   - `qr_router` (4 endpoints, 8 tests)
   - `tables_router` (13 endpoints, 9 tests)
   - `restaurants_router` (12 endpoints, 20 tests)

2. **Pick canonical auth:**
   - Mount `supabase_auth_router` (10 endpoints, 14 tests)
   - Delete `auth_router.py` (5 endpoints, 30+ tests covering the same surface)
   - Fix `/me` 501 in either surviving router

3. **Fix `cart_router` self-prefix conflict:**
   - `cart_router.py:67` defines `prefix="/api/v1/cart"` inline
   - Reconcile with centralized prefix pattern in `main.py`

4. **Replace mounted `menu/router.py` stub:**
   - Delegate to `menu_publishing_use_case` + `menu_repos_impl`

5. **Decide on `orders` router shape:**
   - Either wire the 4 existing use cases or document why the RPC shim wins
   - Same decision for `order_models.py`: keep or delete

6. **Decide on dead `core/database.py`:**
   - Delete it (and `sqlalchemy`/`asyncpg`/`greenlet` deps) **or** commit to using it in Phase 4
   - Do not carry both paths

**Risk:** Low. All code is tested. Worst case is auth surface breakage for Flutter, which is fixable in a day.

**Decision gate:** Run `pytest --cov` and confirm coverage ≥ 90%. If yes, proceed.

### Phase 2 — Bring partial features to parity

**Goal:** Make `order_tracking` shippable; resolve `admin` scope.

**Tasks:**

1. **Resolve `admin` scope:**
   - Today it duplicates `restaurants` registration
   - Either delete `admin` entirely or expand to a real admin panel (impersonation, data fixes, audit log viewer)

2. **Replace Noop services in `order_tracking`:**
   - Define ports: `INotificationSender`, `IEmailSender`, `IWhatsAppSender`
   - Implement real adapters (MSG91 SMS, Meta WhatsApp Cloud API)
   - Replace `_NoopEmailService`, `_NoopWhatsAppService`, `_NoopSMSService`

3. **Mount `order_tracking_router`** after 2.2

**Risk:** Medium — needs MSG91 account, DLT template approval (2-3 days buffer), WhatsApp template approval (2-5 days buffer).

**Decision gate:** Ship a real notification path (MSG91 SMS + WhatsApp via Meta Cloud) end-to-end with one happy flow.

### Phase 3 — Ports and primitives

**Goal:** Establish the port abstractions that unblock the remaining heavy features.

**Tasks:**

| Port | File | Concrete impl |
|---|---|---|
| `IQueue` | `app/common/queue.py` (new) | `PgmqQueue` using Supabase Postgres extension |
| `ICache` | `app/common/cache.py` (new) | `PostgresCache` (table + `pg_cron` sweep) |
| `IPaymentGateway` | promote from `transaction_management/domain/payment_gateway_interfaces.py` to `app/common/payment_gateway.py` | Razorpay adapter (India, UPI native) |
| `ISearch` | `app/common/search.py` (new) | `PostgresSearch` (tsvector + pg_trgm) |

**Risk:** Low per port. Each is one port interface + one impl.

**Decision gate:** One real use case consumes each port before more features are built.

### Phase 4 — Wire the remaining heavy feature

**Goal:** Mount `transaction_management` and complete the endpoint surface.

**Tasks:**

1. **Bind Razorpay adapter** to `IPaymentGateway`
2. **Mount `transaction_router`** with stubbed PDF export (501) clearly marked
3. **Write tests for `transaction_management`** (currently zero)

**Risk:** Medium — Razorpay account, webhook setup, test-mode round-trip.

**Decision gate:** First real payment round-trips successfully in test mode with webhook reconciliation.

### Phase 5 — Observability + multi-tenant

**Goal:** Remove tenant-header leak risk; add production observability.

**Tasks:**

1. **Promote tenant ID from header to JWT claim:**
   - Add `app_metadata.tenant_id` to Supabase user
   - Update `app/security.py` to read tenant from JWT, not `X-Tenant-Id`
   - Remove `get_current_tenant` dependency

2. **Add Sentry tracing on use-case boundaries:**
   - Span per use case invocation
   - Tag with `restaurant_id`, `feature`, `user_id`

3. **Query review with `pg_stat_statements`:**
   - Enable extension
   - Audit hot tables: `orders`, `cart_items`, `menu_items`, `order_payment_history`
   - Add missing indexes

4. **Wire `pg_cron` for maintenance:**
   - Cache sweep
   - Stale-cart cleanup
   - Daily aggregates

**Risk:** Low per task.

**Decision gate:** Security review approves removal of `X-Tenant-Id` header.

---

## 6. What to Build Next — Recommendation

**Start with Phase 1 today.**

Reasoning:
- 50 endpoints become reachable in <2 days with zero new logic
- Coverage goes *up* (mounting tested routers raises %, deleting dead `core/database.py` lowers denominator)
- It unblocks the Flutter team immediately — restaurants, tables, cart, QR are all sitting there waiting
- It costs nothing in design time; Phase 2 onward needs decisions; Phase 1 needs typing

After Phase 1, the real product question surfaces: **what does "the next feature" mean?** The options are:

- **(a) Surface what exists** — Phases 1-4 (recommended for the next 2-3 weeks)
- **(b) Add a new domain** — loyalty, reservations, inventory, multi-location, staff scheduling (2-4 weeks per feature)
- **(c) Cross-cutting infra** — observability, multi-tenant, billing (1-2 weeks)

---

## 7. Key Files Reference

| Concern | Path |
|---|---|
| App bootstrap | `app/main.py` |
| Settings | `app/core/config.py` |
| Dead DB stack | `app/core/database.py` |
| Supabase client (sync + async) | `app/common/supabase_client.py` |
| Exceptions | `app/common/exceptions.py` |
| JWT verify | `app/security.py` |
| Routers (mounted) | `app/features/{auth,menu,orders,public_menu,admin}/presentation/*` |
| Routers (unwired) | `app/features/{restaurants,tables,cart,qr,order_tracking,transaction_management}/presentation/*` |
| Dead SQLAlchemy models | `app/features/orders/infrastructure/order_models.py` |
| Duplicate auth router | `app/features/auth/presentation/supabase_auth_router.py` |
| Noop notification services | `app/features/order_tracking/presentation/order_tracking_router.py:60-77` |
| Payment gateway port (unbound) | `app/features/transaction_management/domain/payment_gateway_interfaces.py` |
| Test conftest | `conftest.py` |
| Coverage config | `pytest.ini` |

---

## 8. Risks Summary

| Risk | Where | Mitigation |
|---|---|---|
| 50+ endpoints unreachable | 6 unwired routers | Phase 1 mount |
| Tenant isolation via header, not JWT | `app/security.py:7` | Phase 5.1 |
| Notifications silently fail | `_Noop*Service` always return `True` | Phase 2.2 |
| Payment gateway adapter absent | `transaction_management` | Phase 4.1 |
| Dead SQLAlchemy code in repo | `core/database.py`, `order_models.py` | Phase 1.6 decision |
| Duplicate auth routers | `auth_router.py` vs `supabase_auth_router.py` | Phase 1.2 |
| Coverage floor broken | `--cov-fail-under=90` | Phase 1 raises coverage |
| `cart_router` prefix conflict | `cart_router.py:67` | Phase 1.3 |
