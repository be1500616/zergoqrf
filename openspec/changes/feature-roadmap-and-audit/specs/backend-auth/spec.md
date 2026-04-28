# Capability: Backend Auth

## ADDED Requirements

### Requirement: JWT Authentication

The backend MUST secure endpoints using JWT (JSON Web Tokens) issued by Supabase Auth.

#### Scenario: Authorized Request

- **GIVEN** a request to a protected endpoint with a valid Supabase JWT
- **WHEN** the authentication middleware processes the request
- **THEN** the request must be permitted and `current_user` context must be populated

### Requirement: Token Validation

The backend MUST strictly validate token signatures and expiration.

#### Scenario: Invalid Token

- **GIVEN** a request with an expired or malformed JWT
- **WHEN** the authentication middleware processes the request
- **THEN** it must return a `401 Unauthorized` response