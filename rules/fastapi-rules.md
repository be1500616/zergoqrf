---
type: "always_apply"
---

# Python FastAPI Coding Standards & Clean Architecture Guidelines

## Table of Contents

1.  [Introduction](#1-introduction)
2.  [Clean Architecture Guidelines](#2-clean-architecture-guidelines)
    - [2.1 Domain Layer](#21-domain-layer)
    - [2.2 Application Layer](#22-application-layer)
    - [2.3 Infrastructure Layer](#23-infrastructure-layer)
    - [2.4 Presentation Layer](#24-presentation-layer)
3.  [Code Organization Standards](#3-code-organization-standards)
    - [3.1 Hybrid Directory Structure](#31-hybrid-directory-structure)
    - [3.2 Feature Module Guidelines](#32-feature-module-guidelines)
    - [3.3 File Naming Conventions](#33-file-naming-conventions)
    - [3.4 Import Guidelines](#34-import-guidelines)
4.  [Function and Method Guidelines](#4-function-and-method-guidelines)
    - [4.1 Single Responsibility Principle (SRP)](#41-single-responsibility-principle-srp)
    - [4.2 Parameter and Return Types](#42-parameter-and-return-types)
    - [4.3 Error Handling](#43-error-handling)
5.  [Documentation Standards](#5-documentation-standards)
    - [5.1 Google-Style Docstrings](#51-google-style-docstrings)
    - [5.2 Docstring Examples](#52-docstring-examples)
6.  [FastAPI-Specific Best Practices](#6-fastapi-specific-best-practices)
    - [6.1 Dependency Injection](#61-dependency-injection)
    - [6.2 Pydantic Models](#62-pydantic-models)
    - [6.3 Route Organization](#63-route-organization)
    - [6.4 Async/Await Usage](#64-asyncawait-usage)
7.  [Code Quality Rules](#7-code-quality-rules)
    - [7.1 Naming Conventions](#71-naming-conventions)
    - [7.2 Type Hints](#72-type-hints)
    - [7.3 Logging](#73-logging)
    - [7.4 Testing](#74-testing)
8.  [Scalability Patterns](#8-scalability-patterns)
    - [8.1 Database Session Management](#81-database-session-management)
    - [8.2 Background Tasks](#82-background-tasks)
    - [8.3 Caching](#83-caching)
9.  [Security Considerations](#9-security-considerations)
    - [9.1 Authentication](#91-authentication)
    - [9.2 Input Validation](#92-input-validation)
10. [API Versioning](#10-api-versioning)
11. [Migration Guidance](#11-migration-guidance)
12. [Augment Agent Instructions](#12-augment-agent-instructions)
13. [Code Review Checklist](#13-code-review-checklist)

---

## 1. Introduction

This document provides coding standards and guidelines for developing Python FastAPI applications using Clean Architecture principles. Its purpose is to ensure code quality, maintainability, and consistency across the project. It serves as a guide for developers and as a set of rules for the Augment Code Agent.

---

## 2. Clean Architecture Guidelines

We follow a 4-layer architecture to separate concerns and create a decoupled, testable, and maintainable system.

- **Dependency Rule**: Inner layers MUST NOT know anything about outer layers. For example, the `domain` layer cannot import from the `application` or `infrastructure` layers.

```
+-----------------------------------------------------------------+
|  Presentation (FastAPI Routers, Pydantic Schemas)               |
|-----------------------------------------------------------------|
|  Application (Use Cases, Services, DTOs)                        |
|-----------------------------------------------------------------|
|  Domain (Entities, Value Objects, Domain Services, Repositories)|
|-----------------------------------------------------------------|
|  Infrastructure (Database, External APIs, Frameworks)           |
+-----------------------------------------------------------------+
```

### 2.1 Domain Layer

- **Purpose**: Contains the core business logic and rules. It is the heart of the application.
- **Contents**:

  - **Entities**: Business objects with an identity (e.g., `User`, `Campaign`).
  - **Value Objects**: Immutable objects without an identity (e.g., `Email`, `Password`).
  - **Repository Interfaces**: Abstract contracts for data persistence (e.g., `IUserRepository`).
  - **Domain Services**: Business logic that doesn't naturally fit within an entity.

- **Example (`app/features/user/domain/user_entities.py`)**:

  ```python
  # app/features/user/domain/user_entities.py
  from .user_vos import Email

  class User:
      def __init__(self, id: int, email: Email, is_active: bool):
          self.id = id
          self.email = email
          self.is_active = is_active

      def deactivate(self):
          self.is_active = False
  ```

### 2.2 Application Layer

- **Purpose**: Orchestrates the flow of data and calls domain objects to perform business logic. It defines the application's use cases.
- **Contents**:

  - **Application Services / Use Cases**: Implements specific application logic (e.g., `CreateUserService`).
  - **Data Transfer Objects (DTOs)**: Simple objects for transferring data between layers, especially between Presentation and Application.

- **Example (`app/features/user/application/use_cases/create_user.py`)**:

  ```python
  # app/features/user/application/use_cases/create_user.py
  from ...domain.user_repos import IUserRepository
  from ...domain.user_vos import Email
  from ..user_dtos import UserDTO

  class CreateUserUseCase:
      def __init__(self, user_repository: IUserRepository):
          self._repository = user_repository

      async def execute(self, email: str, password: str) -> UserDTO:
          # ... business logic orchestration ...
          pass
  ```

### 2.3 Infrastructure Layer

- **Purpose**: Implements the details of external concerns like databases, APIs, and frameworks. It provides concrete implementations of the repository interfaces defined in the Domain layer.
- **Contents**:

  - **Repository Implementations**: Concrete data access logic (e.g., `UserRepositoryImpl` using SQLAlchemy).
  - **Database Models**: SQLAlchemy models.
  - **External Service Clients**: Clients for interacting with third-party APIs.

- **Example (`app/features/user/infrastructure/user_repos_impl.py`)**:

  ```python
  # app/features/user/infrastructure/user_repos_impl.py
  from sqlalchemy.ext.asyncio import AsyncSession
  from ...domain.user_repos import IUserRepository
  from ...domain.user_entities import User
  from .user_models import UserModel

  class UserRepositoryImpl(IUserRepository):
      def __init__(self, session: AsyncSession):
          self._session = session

      async def find_by_email(self, email: str) -> User | None:
          # ... SQLAlchemy query logic ...
          pass
  ```

### 2.4 Presentation Layer

- **Purpose**: Handles HTTP requests and responses. It is the entry point for users and external clients.
- **Contents**:

  - **API Routers**: FastAPI `APIRouter` instances defining endpoints.
  - **Request/Response Schemas**: Pydantic models for data validation and serialization.
  - **Dependencies**: FastAPI dependencies for handling concerns like authentication and database sessions.

- **Example (`app/features/user/presentation/user_router.py`)**:

  ```python
  # app/features/user/presentation/user_router.py
  from fastapi import APIRouter, Depends
  from ..application.use_cases.create_user import CreateUserUseCase
  from .user_schemas import UserCreateSchema, UserResponseSchema

  router = APIRouter()

  @router.post("/users/", response_model=UserResponseSchema)
  async def create_user_endpoint(
      request: UserCreateSchema,
      create_user_use_case: CreateUserUseCase = Depends(), # Dependency injection for the use case
  ):
      # ... delegate to create_user_use_case.execute() ...
      pass
  ```

---

## 3. Code Organization Standards

### 3.1 Vertical Slice (Feature-First) Directory Structure

To ensure maximum scalability and maintainability, we adopt a **Vertical Slice Architecture**. This approach organizes the codebase around business features. Each feature is a self-contained module that includes all necessary components for its functionality. This structure promotes high cohesion and low coupling, making the system easier to develop, test, and scale.

The layers of Clean Architecture are preserved *within* each feature module, providing a clear and scalable separation of concerns.

**Key Principles:**

- **Feature Co-location**: All code for a single feature resides in its own directory under `app/features/`.
- **Layered Internal Structure**: Each feature directory contains subdirectories for `application`, `domain`, `infrastructure`, and `presentation` layers.
- **Explicit Naming**: Files are named specifically (e.g., `category_services.py` instead of a generic `services.py`) to improve clarity and prevent files from becoming too large.
- **Test Mirroring**: The `tests/` directory mirrors the `app/` structure, ensuring that tests are easy to locate.
- **Package Markers**: Every directory that should be a Python package MUST contain an `__init__.py` file.

```
whatsfuse-central-api/
├── app/
│   ├── features/
│   │   ├── __init__.py
│   │   └── category/
│   │       ├── __init__.py
│   │       ├── application/
│   │       │   ├── __init__.py
│   │       │   ├── use_cases/
│   │       │   │   ├── __init__.py
│   │       │   │   ├── create_category.py # Example: Use case for creating a category
│   │       │   │   ├── get_category.py    # Example: Use case for retrieving a category
│   │       │   │   └── update_category.py # Each file represents a single use case
│   │       │   └── category_dtos.py     # Data Transfer Objects for the feature
│   │       ├── domain/
│   │       │   ├── __init__.py
│   │       │   ├── category_entities.py # Core business entities
│   │       │   ├── category_repos.py    # Repository interfaces
│   │       │   └── category_vos.py      # Value objects
│   │       ├── infrastructure/
│   │       │   ├── __init__.py
│   │       │   ├── category_models.py   # Database models (e.g., SQLAlchemy)
│   │       │   └── category_repos_impl.py # Concrete repository implementations
│   │       └── presentation/
│   │           ├── __init__.py
│   │           ├── category_router.py   # FastAPI router for the feature
│   │           └── category_schemas.py  # Pydantic schemas for API requests/responses
│   ├── shared/                      # Shared, decoupled modules (Shared Kernel)
│   │   ├── __init__.py
│   │   ├── common/                  # Truly universal code (e.g., base exceptions)
│   │   ├── database/                # Database session, engine, base models
│   │   └── security/                # Authentication, authorization logic
│   └── main.py                      # Main FastAPI app, combines routers from features
└── tests/
    └── features/
        ├── __init__.py
        └── category/
            ├── __init__.py
            ├── test_application.py
            ├── test_domain.py
            └── test_presentation.py
```

### 3.2 Feature Module Guidelines

- **When to create a new feature module**:
  - When introducing a new, distinct business domain or major functional area (e.g., `User Management`, `Product Catalog`, `Order Processing`).
  - When the new functionality has its own set of entities, use cases, and persistence requirements that are largely independent of existing features.
  - To improve team autonomy and reduce merge conflicts in large projects.

- **When to extend an existing feature module**:
  - When adding new functionality that directly relates to or extends an existing business domain (e.g., adding a new field to an existing `User` entity, or a new operation to the `UserService`).
  - To keep related logic co-located and maintain cohesion within a single feature.

- **Module Structure**: Each feature module is self-contained. The internal structure follows the layer-based organization as defined in the directory map.

### 3.3 File Naming Conventions

- Use `snake_case` for all Python files and directories.
- Files should be prefixed with the feature name (e.g., `category_`) followed by their type. This improves clarity and searchability.
- **Use Case Files**: Place each use case in its own file within the `application/use_cases/` directory (e.g., `create_category.py`).
- **Routers**: `_router.py` suffix (e.g., `category_router.py`).
- **Repositories**: `_repos.py` for interfaces, `_repos_impl.py` for implementations.
- **Schemas**: `_schemas.py`.
- **DTOs**: `_dtos.py`.
- **Entities**: `_entities.py`.
- **Value Objects**: `_vos.py`.
- **Models**: `_models.py`.

### 3.4 Import Guidelines

Imports must always respect the Clean Architecture Dependency Rule (imports flow inwards).

- **Within a Feature**: Use relative imports to navigate between layers of the same feature.
- **Between Features**: Direct imports between features are **strongly discouraged**. If features must interact, it should be done through a higher-level orchestration layer or an event-driven mechanism, not direct coupling.
- **Shared Kernel**: Features can import from the `app.shared` modules.

**Examples**:

```python
# 1. Presentation Layer importing Application Layer (Allowed)
# app/features/category/presentation/category_router.py
from ..application.use_cases.create_category import CreateCategoryUseCase
from ..application.use_cases.get_category import GetCategoryUseCase

# 2. Application Layer importing Domain Layer (Allowed)
# app/features/category/application/use_cases/create_category.py
from ...domain.category_repos import ICategoryRepository
from ...domain.category_entities import Category

# 3. Infrastructure Layer importing Domain Layer (Allowed)
# app/features/category/infrastructure/category_repos_impl.py
from ...domain.category_repos import ICategoryRepository
from .category_models import CategoryModel

# 4. Feature importing from Shared Kernel (Allowed)
# app/features/category/infrastructure/category_repos_impl.py
from app.shared.database import AsyncSession # Importing from the shared module

# 5. NOT Allowed: Inner Layer importing Outer Layer
# app/features/category/domain/category_entities.py
# from ..application.use_cases.create_category import CreateCategoryUseCase # BAD!

# 6. NOT Allowed: Direct import between features
# app/features/user/application/use_cases/create_user.py
# from app.features.category.application.use_cases.create_category import CreateCategoryUseCase # BAD!
```

---

## 4. Function and Method Guidelines

### 4.1 Single Responsibility Principle (SRP)

- **Do**: A function should do one thing and do it well.
  ```python
  async def get_user_by_id(user_id: int, db: AsyncSession) -> User:
      """Fetches a single user from the database."""
      # ... logic to fetch user ...
  ```
- **Don't**: A function should not perform multiple unrelated actions.
  ```python
  # Bad: Fetches user and then sends an email
  async def get_user_and_send_email(user_id: int, db: AsyncSession):
      # ... logic to fetch user ...
      # ... logic to send email ...
  ```

### 4.2 Parameter and Return Types

- **Do**: Always use explicit type hints for parameters and return values.

  ```python
  from .models import User

  def format_user_name(user: User) -> str:
      return f"{user.first_name} {user.last_name}"
  ```

- **Don't**: Omit type hints.
  ```python
  # Bad: No type hints
  def format_user_name(user):
      return f"{user.first_name} {user.last_name}"
  ```

### 4.3 Error Handling

- **Do**: Catch specific exceptions and raise custom, meaningful exceptions.

  ```python
  class UserNotFoundError(Exception):
      pass

  async def get_user(user_id: int, user_repo: IUserRepository):
      try:
          user = await user_repo.get_by_id(user_id)
          if not user:
              raise UserNotFoundError(f"User with id {user_id} not found.")
          return user
      except SQLAlchemyError as e:
          logger.error(f"Database error fetching user: {e}")
          raise InfrastructureError("Could not access database.")
  ```

- **Don't**: Use bare `except` clauses.
  ```python
  # Bad: Hides all errors
  try:
      # ... some code ...
  except:
      pass
  ```

---

## 5. Documentation Standards

### 5.1 Google-Style Docstrings

All modules, classes, and functions must have Google-style docstrings. This is non-negotiable for code quality and maintainability.

### 5.2 Docstring Examples

#### Class Docstring

```python
class UserService:
    """Manages user-related operations.

    This service contains the business logic for creating, updating,
    and retrieving users.

    Attributes:
        user_repository: The repository for user data access.
    """
```

#### Async Function/Method Docstring

```python
async def create_user(
    email: str,
    password: str,
    user_service: UserService = Depends(),
) -> UserResponse:
    """Creates a new user.

    Args:
        email: The email address of the new user.
        password: The plaintext password for the new user.
        user_service: The user service dependency.

    Returns:
        The created user object.

    Raises:
        HTTPException: If a user with the given email already exists.
    """
```

---

## 6. FastAPI-Specific Best Practices

### 6.1 Dependency Injection

- **Do**: Use `Depends` for all dependencies (services, repositories, sessions). This makes testing and swapping implementations easy.

  ```python
  from .dependencies import get_user_service

  @router.get("/users/me")
  async def read_users_me(user_service: UserService = Depends(get_user_service)):
      # ...
  ```

### 6.2 Pydantic Models

- **Do**: Define separate Pydantic models for request (`Create`, `Update`) and response (`Response`) schemas. Never return database models directly from the API.

  ```python
  # schemas/user_schemas.py
  from pydantic import BaseModel, EmailStr

  class UserBase(BaseModel):
      email: EmailStr

  class UserCreate(UserBase):
      password: str

  class UserResponse(UserBase):
      id: int
      is_active: bool

      class Config:
          orm_mode = True
  ```

### 6.3 Route Organization

- **Do**: Use `APIRouter` to group related endpoints into separate files.

  ```python
  # main.py
  from .presentation.api.v1 import users_router, items_router

  app = FastAPI()
  app.include_router(users_router, prefix="/api/v1/users", tags=["Users"])
  app.include_router(items_router, prefix="/api/v1/items", tags=["Items"])
  ```

### 6.4 Async/Await Usage

- **Do**: Use `async def` for all route handlers and I/O-bound operations (database calls, API requests).
- **Don't**: Call blocking I/O functions in an `async` function without `await`. This will block the event loop.

  ```python
  # Bad: time.sleep() is blocking
  @router.get("/")
  async def my_route():
      time.sleep(5) # This blocks the entire server!
      return {"message": "done"}

  # Good: asyncio.sleep() is non-blocking
  @router.get("/")
  async def my_route():
      await asyncio.sleep(5)
      return {"message": "done"}
  ```

---

## 7. Code Quality Rules

### 7.1 Naming Conventions

- **Classes**: `PascalCase` (e.g., `UserService`).
- **Functions, Methods, Variables**: `snake_case` (e.g., `create_user`).
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRIES`).
- **Private members**: `_` prefix (e.g., `_internal_method`).

### 7.2 Type Hints

- All function signatures MUST include type hints.
- Use types from the `typing` module where appropriate (`List`, `Dict`, `Optional`, `Any`).

### 7.3 Logging

- Use the standard `logging` module.
- Log meaningful messages with context.
- **NEVER** log sensitive information like passwords, API keys, or PII.
- **Example**: `logger.info("User %d created successfully.", user.id)`

### 7.4 Testing

- Write unit tests for domain and application logic.
- Write integration tests for API endpoints using `TestClient`.
- Use `pytest` fixtures for setting up test data and dependencies.
- Aim for high test coverage.

---

## 8. Scalability Patterns

### 8.1 Database Session Management

- Use a dependency-injected session that is created per-request and closed afterward.
  ```python
  # dependencies.py
  async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
      async with async_session_factory() as session:
          yield session
  ```

### 8.2 Background Tasks

- For long-running tasks that should not block the HTTP response, use `BackgroundTasks`.
  ```python
  @router.post("/email")
  def send_email(background_tasks: BackgroundTasks, email: EmailSchema):
      background_tasks.add_task(send_notification, email.address, "Hello")
      return {"message": "Email sending initiated."}
  ```

### 8.3 Caching

- Implement caching for frequently accessed, non-volatile data using libraries like `fastapi-cache2`.
- Cache at the service layer or with a decorator on API routes.

---

## 9. Security Considerations

### 9.1 Authentication

- Use standard, robust authentication mechanisms like **OAuth2 with JWT Bearer tokens**.
- Implement token refresh logic.
- Store passwords using a strong hashing algorithm (e.g., `bcrypt`).

### 9.2 Input Validation

- Rely on Pydantic for rigorous input validation.
- Define constraints on string lengths, number ranges, etc., in your schemas.

---

## 10. API Versioning

- Prefix routes with a version number (e.g., `/api/v1/`).
- This allows for introducing breaking changes in future versions without affecting existing clients.

---

## 11. Augment Agent Instructions

**When generating, refactoring, or reviewing code, you MUST adhere to the following directives:**

1.  **Strictly Follow Clean Architecture**: Place all new code in the correct layer as defined in [Section 2](#2-clean-architecture-guidelines).
2.  **Generate Full Docstrings**: Every function, method, and class you create MUST have a complete Google-style docstring as per [Section 5](#5-documentation-standards).
3.  **Apply Type Hints Everywhere**: All function signatures and variable declarations must have explicit type hints.
4.  **Use Dependency Injection**: For services, repositories, and database sessions, always use FastAPI's `Depends` system.
5.  **Separate Schemas**: Create distinct Pydantic models for request and response data. Do not expose database models in the API.
6.  **Organize Routes**: Group related endpoints in a dedicated `APIRouter` file within the `presentation/api/v1/` directory.
7.  **Handle Errors Gracefully**: Implement specific, custom exceptions for business logic errors and handle infrastructure errors with logging and generic error responses.
8.  **Write Testable Code**: Ensure all business logic is decoupled from the framework and can be unit-tested easily.
9.  **Adhere to Naming Conventions**: All generated code must follow the naming conventions in [Section 7.1](#71-naming-conventions).
10. **Prioritize Security**: Never log sensitive data. Use secure patterns for authentication and password handling.

---

## 12. Code Review Checklist

- [ ] Does the code adhere to the Clean Architecture layers?
- [ ] Are all functions, classes, and modules documented with Google-style docstrings?
- [ ] Are type hints used for all function signatures?
- [ ] Is dependency injection used for services and sessions?
- [ ] Are Pydantic schemas used for all API inputs and outputs?
- [ ] Is error handling specific and meaningful?
- [ ] Are there corresponding unit or integration tests for the new code?
- [ ] Is sensitive information kept out of logs?
- [ ] Does the code follow all naming and style conventions?
- [ ] Is the code free of blocking calls in async functions?
