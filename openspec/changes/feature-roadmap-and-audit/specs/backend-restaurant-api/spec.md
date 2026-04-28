# Capability: Backend Restaurant API

## ADDED Requirements

### Requirement: Restaurant Management

The backend MUST provide endpoints to create, read, and update restaurant profiles.

#### Scenario: Restaurant Creation

- **GIVEN** an authenticated owner
- **WHEN** posting a new restaurant's details (name, description, etc.) to the API
- **THEN** a new restaurant record must be created and linked to the owner

### Requirement: Multi-tenant Isolation

Restaurant data MUST be strictly isolated by tenant (owner).

#### Scenario: Tenant Isolation

- **GIVEN** Two different owners (A and B)
- **WHEN** Owner A requests their restaurant list
- **THEN** they must NOT see any restaurants belonging to Owner B

