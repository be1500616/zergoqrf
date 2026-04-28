# Configuration Management Guidelines

## 1. Introduction
This document defines the standards for managing configuration in all applications. Proper configuration management is essential for security, scalability, and maintainability.

## 2. Core Principles
- **Environment-Specific**: Configuration MUST be separated by environment (e.g., `development`, `staging`, `production`).
- **Secure**: Sensitive information (secrets, keys, passwords) MUST NOT be stored in version control. Use a secure secret management solution.
- **Centralized**: Configuration should be loaded from a single, reliable source of truth.
- **Typed**: When possible, use typed configuration objects to prevent errors and improve developer experience.

## 3. Environment Variables
- **Primary Source**: Environment variables are the primary method for supplying environment-specific configuration.
- **Naming**: Use `UPPER_SNAKE_CASE` for all environment variables (e.g., `DATABASE_URL`).
- **Defaults**: Provide sensible default values for non-critical configuration in a `.env.example` file. The `.env` file itself should be included in `.gitignore`.

## 4. Secrets Management
- **Tooling**: Use a dedicated secrets management tool like HashiCorp Vault, AWS Secrets Manager, or Google Secret Manager.
- **Access Control**: Access to secrets MUST be tightly controlled and audited.
- **Rotation**: Implement a policy for regular rotation of all secrets.

## 5. Loading Configuration
- **Centralized Loading**: Application configuration should be loaded and validated at startup.
- **Validation**: Use a library like Pydantic (Python) or Zod (Node.js) to validate the structure and types of the configuration.

### Example (Node.js with `dotenv` and `zod`)
```javascript
// src/config/index.js
import dotenv from 'dotenv';
import { z } from 'zod';

dotenv.config();

const envSchema = z.object({
  NODE_ENV: z.enum(['development', 'production', 'test']),
  PORT: z.coerce.number().default(3000),
  DATABASE_URL: z.string().url(),
});

export const config = envSchema.parse(process.env);
