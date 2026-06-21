# OpenSpec Chronology — Database & Runtime

This document is the single source of truth for the time order and dependency order of the OpenSpec changes related to the database runtime. It exists so that future maintainers can answer two questions in 30 seconds:

1. **What was created when?** (chronological order)
2. **What depends on what?** (dependency order)

If a change is not listed here, it is not part of the database/runtime story.

---

## Chronological Order

Numbered by creation time. Times reflect when the change first appeared in the tree (git-tracked commits use the commit timestamp; uncommitted drafts use the file mtime or session context).

### Pre-session (committed to git)

| # | When | Change | State at session start |
|---|---|---|---|
| 1 | 2026-04-29 01:34 IST | `add-tdd-test-infrastructure` | committed |
| 2 | 2026-04-29 03:03 IST | `add-postgres-local-dev-runtime` | committed |
| 3 | Jan 8 2026 (session memory) | `feature-roadmap-and-audit` | uncommitted, in tree |

### Session 1 — early (uncommitted, written before this conversation)

| # | When | Change | Notes |
|---|---|---|---|
| 4 | session-1 morning | `add-dev-prod-supabase-workflow` | profile contract, Tier A/B split |
| 5 | session-1 morning | `add-flutter-cross-platform-design-language` | design system |
| 6 | session-1 morning | `add-unified-fastapi-flutter-logging` | logging |
| 7 | session-1 morning | `add-phased-kiosk-kds-mobile-ordering-rollout` | phased rollout |

### Session 2 — mid (this conversation)

| # | When | Change | Notes |
|---|---|---|---|
| 8 | session-2 14:00ish | `unify-supabase-postgres-runtime` | **created then deleted** — monolithic 5-capability proposal that was over-engineered |
| 9 | session-2 14:34 | `parked/` directory | created during the split |
| 10 | session-2 14:36 | **`fix-broken-database-connection`** | **active, validated, ready for review** — the broken-thing fix |
| 11 | session-2 14:37 | `parked/migrations-and-conventions` | promote when the 2nd real schema change lands |
| 12 | session-2 14:37 | `parked/app-jobs-and-realtime-fanout` | promote when a feature needs async work |

---

## Dependency Order

The dependency graph, drawn from each change's `proposal.md` "Dependencies" section.

```
   ┌─────────────────────────────────────────────────────────────────────────────┐
   │                                                                             │
   │   add-postgres-local-dev-runtime (Apr 29 03:03, committed)                  │
   │   ├── bullets "Postgres-backed queue, no RabbitMQ"                          │
   │   │   └──→ parked/app-jobs-and-realtime-fanout                              │
   │   └── profile + queue SLO contract                                          │
   │       └──→ soft-dep on fix-broken-database-connection (key names match)     │
   │                                                                             │
   │   add-dev-prod-supabase-workflow (session-1, uncommitted)                  │
   │   ├── profile contract (SUPABASE_{PROFILE}_*)                               │
   │   │   └──→ soft-dep on fix-broken-database-connection                       │
   │   └── Tier A / Tier B test split                                            │
   │       └──→ parked/migrations-and-conventions (Tier B future work)           │
   │                                                                             │
   │   add-phased-kiosk-kds-mobile-ordering-rollout (session-1, uncommitted)    │
   │   ├── §1 "Replace placeholder order-tracking router dependency providers"   │
   │   │   └──→ blocks on fix-broken-database-connection (DI wiring)             │
   │   └── §5 Observability                                                     │
   │       └──→ soft-dep on fix-broken-database-connection (Settings)            │
   │                                                                             │
   │   ╔══════════════════════════════════════════════════════════════════════╗ │
   │   ║  fix-broken-database-connection (★ ACTIVE, validated)               ║ │
   │   ║  ├── Hard dep: nothing in this repo (the broken-thing fix)          ║ │
   │   ║  ├── Soft dep: add-dev-prod-supabase-workflow (profile keys match)  ║ │
   │   ║  └── Blocks:                                                         ║ │
   │   ║      ├── add-phased-kiosk-kds-mobile-ordering-rollout (§1, §5)      ║ │
   │   ║      ├── parked/migrations-and-conventions                          ║ │
   │   ║      └── parked/app-jobs-and-realtime-fanout                         ║ │
   │   ╚══════════════════════════════════════════════════════════════════════╝ │
   │           │                                                                 │
   │           ▼                                                                 │
   │   parked/migrations-and-conventions (promote on 2nd migration)             │
   │   ├── Hard dep: fix-broken-database-connection                              │
   │   ├── Soft dep: add-dev-prod-supabase-workflow (Tier A/B)                   │
   │   └── Blocks: parked/app-jobs-and-realtime-fanout                           │
   │                                                                             │
   │   parked/app-jobs-and-realtime-fanout (promote with first caller)          │
   │   ├── Hard dep: fix-broken-database-connection                              │
   │   ├── Hard dep: parked/migrations-and-conventions (when promoted)           │
   │   └── Soft dep: add-phased-kiosk-kds-mobile-ordering-rollout §1             │
   │       (the first caller is likely order-tracking status fan-out)            │
   │                                                                             │
   └─────────────────────────────────────────────────────────────────────────────┘
```

---

## Promotion Triggers

Each parked draft has a documented "trigger to promote." When the trigger fires, the draft is moved from `openspec/changes/parked/` to `openspec/changes/<id>/` and the `proposal.md` "Status" line is removed.

### `parked/migrations-and-conventions` — promote when **any** of:

- A second hand-written migration is added after `fix-broken-database-connection` lands.
- A destructive change (`drop column`, `set not null`, rename) is needed.
- The RLS posture question comes up in code review (the answer is "no, the table forgot RLS").

### `parked/app-jobs-and-realtime-fanout` — promote when **any** of:

- An endpoint needs to send a notification or push after a write commits.
- An endpoint needs to do work after a write that the user should not wait on.
- A scheduled job (recurring) is needed.
- A second write-side consumer (e.g. analytics) needs to subscribe to state changes.

The promotion lands in the same PR as the caller. The migration, the helper, the worker, and the caller are one reviewable diff.

---

## What Was Lost in the Split (And Where It Lives Now)

The monolithic `unify-supabase-postgres-runtime` proposal covered 5 capabilities. The split lifted 1 into an active change and parked 4 as drafts. Nothing was deleted; everything is recoverable from the parked drafts and the chronology.

| Original capability | Where it lives now | Status |
|---|---|---|
| `supabase-postgres-runtime` (DB connection) | `fix-broken-database-connection` | **active** |
| `local-supabase-dev-loop` (Makefile + dev workflow) | `fix-broken-database-connection` (collapsed to `make dev`) + `parked/migrations-and-conventions` (extended with lint, rls-check) | active + parked |
| `multi-tenant-rls-posture` | `parked/migrations-and-conventions` | parked |
| `schema-and-migration-management` | `parked/migrations-and-conventions` | parked |
| `postgres-cache-queue` | `parked/app-jobs-and-realtime-fanout` | parked |
| Outbox pattern (Decision 5 in design.md) | `parked/app-jobs-and-realtime-fanout/specs/outbox-fanout/spec.md` | parked |

### Tasks moved from the monolithic proposal to parked drafts

The original had 30 tasks across 10 sections. The split distributed them:

| Section | Original count | New home | Count there |
|---|---|---|---|
| 1. Config and Connection Cleanup | 5 | `fix-broken-database-connection` | 3 |
| 2. Supabase Client Collapse | 4 | `fix-broken-database-connection` | 4 |
| 3. Queue and Cache Tables | 6 | `parked/app-jobs-and-realtime-fanout` | 4 (queue + worker, no cache) |
| 4. Local Loop Tooling | 4 | `fix-broken-database-connection` (1) + `parked/migrations-and-conventions` (3) | 4 total |
| 5. Outbox-Style Status Fan-Out | 3 | `parked/app-jobs-and-realtime-fanout` | 3 (in caller tasks) |
| 6. RLS Posture and Tenant Isolation | 3 | `parked/migrations-and-conventions` | 5 |
| 7. Test Tier Split | 4 | `parked/migrations-and-conventions` (deferred) | 0 (deferred to follow-up) |
| 8. Schema and Migration Management | 12 | `parked/migrations-and-conventions` | 7 + 3 verification |
| 9. Documentation and Deprecation | 3 | `fix-broken-database-connection` (1) + `parked/migrations-and-conventions` (2) | 3 |
| 10. Verification | 5 | `fix-broken-database-connection` (5) | 5 |

### Specs preserved

| Spec | Requirements | File |
|---|---|---|
| `supabase-postgres-runtime` | 4 | `fix-broken-database-connection/specs/supabase-postgres-runtime/spec.md` |
| `schema-and-migration-management` | 12 | `parked/migrations-and-conventions/specs/schema-and-migration-management/spec.md` |
| `multi-tenant-rls-posture` | 6 | `parked/migrations-and-conventions/specs/multi-tenant-rls-posture/spec.md` |
| `local-supabase-dev-loop` | 7 | `parked/migrations-and-conventions/specs/local-supabase-dev-loop/spec.md` |
| `postgres-cache-queue` | 9 | `parked/app-jobs-and-realtime-fanout/specs/postgres-cache-queue/spec.md` |
| `outbox-fanout` | 6 | `parked/app-jobs-and-realtime-fanout/specs/outbox-fanout/spec.md` |

**Total: 44 OpenSpec requirements, all preserved across 6 spec files in 3 changes.**

---

## Next Move (Recommended)

1. **Land `fix-broken-database-connection`** — the active change. Implement the 7 tasks, validate, PR.
2. **Re-evaluate after the first real schema change.** If a developer adds a migration after the fix lands, promote `parked/migrations-and-conventions`.
3. **Re-evaluate when a feature needs async work.** The first such caller (likely order-tracking status fan-out from `add-phased-kiosk-kds-mobile-ordering-rollout` §1) triggers the promotion of `parked/app-jobs-and-realtime-fanout` in the same PR.

Do not promote the parked drafts speculatively. The triggers are documented. Wait for them.
