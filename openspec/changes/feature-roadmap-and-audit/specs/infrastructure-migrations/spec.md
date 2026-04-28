# Capability: Infrastructure & Migrations

## ADDED Requirements

### Requirement: Supabase Schema Consistency

The database schema MUST be defined in version-controlled SQL migration files.

#### Scenario: Migration Application

- **GIVEN** a fresh Supabase environment
- **WHEN** running all migrations in `infra/supabase/migrations/`
- **THEN** the resulting schema must match the expected production layout

### Requirement: Seed Data Availability

Initial system state (e.g., default categories) MUST be available via a seed script.

#### Scenario: Seeding Data

- **GIVEN** an initialized schema
- **WHEN** running `infra/supabase/seeds/seed.sql`
- **THEN** the database must be populated with essential initial data