# Authentication Router Integration Plan

## Executive Summary

This document outlines the strategy to merge the **Supabase-focused authentication router** with the **Clean Architecture authentication system**, creating a unified, maintainable authentication layer that:
- ✅ Maintains Clean Architecture principles (domain, application, infrastructure, presentation)
- ✅ Leverages Supabase as the primary auth infrastructure
- ✅ Includes all features from both current routers
- ✅ Ensures testability and separation of concerns
- ✅ Provides consistent error handling and logging

---

## Current State Analysis

### Router 1: Clean Architecture Router (`auth_router.py`)
**Status:** DISABLED (commented out in main.py line 16-17)

**Strengths:**
- Follows Clean Architecture patterns strictly
- Clear separation of concerns (domain, application, infrastructure, presentation)
- Use cases encapsulate business logic
- Repository pattern allows easy testing with mocks
- Comprehensive error handling with domain exceptions
- Dependency injection through FastAPI

**Weaknesses:**
- Incomplete implementation
- `/me` endpoint returns 501 (not implemented)
- Missing features: phone OTP, signout, restaurant code validation
- Import issues preventing usage
- Doesn't fully leverage Supabase's capabilities

### Router 2: Supabase-Focused Router (`supabase_auth_router.py`)
**Status:** ACTIVE (used in main.py line 126)

**Strengths:**
- Fully functional with all features
- Phone OTP authentication
- Restaurant code validation
- Email availability checking
- Complete signout functionality
- Proper logging and error handling
- Uses Supabase's native capabilities

**Weaknesses:**
- Direct Supabase client calls in route handlers
- Mixes infrastructure concerns with presentation
- Hard to unit test (tight coupling to Supabase)
- Duplicates business logic across endpoints
- Not following Clean Architecture pattern

---

## Integration Strategy

### Phase 1: Infrastructure Layer Enhancement
**Goal:** Create a SupabaseAuthRepository that implements IAuthRepository while using Supabase directly

**Files to Create/Modify:**
- `infrastructure/supabase_auth_repository.py` (NEW)

**Key Components:**

1. **SupabaseAuthRepository**
   - Implements all methods from `IAuthRepository` interface
   - Handles Supabase API calls
   - Converts Supabase responses to domain entities
   - Proper error handling and logging

2. **Methods to Implement:**
   ```
   async def sign_in_with_email(email: Email, password: str) -> AuthenticationResult
   async def sign_up_with_email(email: Email, password: str, ...) -> AuthenticationResult
   async def initiate_phone_auth(phone: Phone) -> bool
   async def verify_phone_otp(phone: Phone, otp_code: OTPCode, ...) -> AuthenticationResult
   async def refresh_session(refresh_token: Token) -> AuthenticationResult
   async def sign_out(user_id: str) -> bool
   async def get_user_by_id(user_id: str) -> Optional[User]
   async def get_user_by_email(email: Email) -> Optional[User]
   async def get_user_by_phone(phone: Phone) -> Optional[User]
   async def update_user_metadata(user_id: str, metadata: Dict) -> bool
   ```

3. **Helper Methods:**
   - `_convert_supabase_user_to_entity()` - Convert Supabase user to User entity
   - `_convert_supabase_session_to_auth_result()` - Convert session to AuthenticationResult
   - `_create_anonymous_session()` - Create anonymous session via Supabase RPC
   - `_validate_restaurant_code()` - Look up restaurant by code

**Benefits:**
- ✅ Repository pattern provides abstraction
- ✅ Dependency injection friendly
- ✅ Easy to mock for testing
- ✅ Clear separation of infrastructure concerns
- ✅ Implements contract defined by IAuthRepository

---

### Phase 2: Application Layer Extensions
**Goal:** Add missing use cases to support all features from Supabase router

**Files to Create/Modify:**
- `application/use_cases/phone_auth_initiate_use_case.py` (NEW)
- `application/use_cases/phone_auth_verify_use_case.py` (NEW)
- `application/use_cases/sign_out_use_case.py` (NEW)
- `application/use_cases/validate_restaurant_code_use_case.py` (NEW)
- `application/use_cases/validate_email_availability_use_case.py` (NEW)
- `application/auth_dtos.py` (EXTEND)

**Use Cases to Create:**

1. **PhoneAuthInitiateUseCase**
   - Input: `PhoneAuthInitiateRequestDTO` with phone number
   - Output: `PhoneAuthInitiateResponseDTO` with confirmation
   - Logic: Call auth repo to send OTP, handle errors

2. **PhoneAuthVerifyUseCase**
   - Input: `PhoneAuthVerifyRequestDTO` with phone, OTP, optional name
   - Output: `AuthTokenResponseDTO` with tokens and user info
   - Logic: Verify OTP, create session, return tokens

3. **SignOutUseCase**
   - Input: `SignOutRequestDTO` with user_id
   - Output: `SignOutResponseDTO` with success message
   - Logic: Call Supabase auth.sign_out(), invalidate session

4. **ValidateRestaurantCodeUseCase**
   - Input: `RestaurantCodeRequestDTO` with code
   - Output: `RestaurantCodeResponseDTO` with branding and session token
   - Logic: Query restaurant by code, create anonymous session, return branding

5. **ValidateEmailAvailabilityUseCase**
   - Input: `EmailAvailabilityRequestDTO` with email
   - Output: `EmailAvailabilityResponseDTO` with availability status
   - Logic: Query auth.users table, return availability

**DTOs to Add:**
```python
# Phone Auth
class PhoneAuthInitiateRequestDTO:
    phone: str

class PhoneAuthInitiateResponseDTO:
    message: str
    phone: str
    otp_sent: bool

class PhoneAuthVerifyRequestDTO:
    phone: str
    otp_code: str
    name: Optional[str] = None

# Sign Out
class SignOutRequestDTO:
    pass  # Use from current user context

class SignOutResponseDTO:
    message: str
    success: bool

# Restaurant Code
class RestaurantCodeRequestDTO:
    code: str

class RestaurantBrandingDTO:
    restaurant_id: str
    name: str
    logo_url: Optional[str]
    primary_color: Optional[str]
    secondary_color: Optional[str]

class RestaurantCodeResponseDTO:
    valid: bool
    restaurant: RestaurantBrandingDTO
    session_token: str
    message: str

# Email Availability
class EmailAvailabilityRequestDTO:
    email: str

class EmailAvailabilityResponseDTO:
    available: bool
```

---

### Phase 3: Presentation Layer Integration
**Goal:** Create unified auth router that combines both routers using Clean Architecture

**Files to Create/Modify:**
- `presentation/auth_router.py` (REPLACE with integrated version)
- `presentation/auth_schemas.py` (EXTEND with new schemas)
- `presentation/supabase_auth_router.py` (ARCHIVE or DELETE)

**Unified Router Endpoints:**

```
POST   /auth/validate/email                    # Email availability check
POST   /auth/signin/email                      # Email/password sign in
POST   /auth/signup/email                      # Email/password registration
POST   /auth/signin/phone                      # Initiate phone OTP
POST   /auth/verify/phone                      # Verify phone OTP
POST   /auth/anonymous-session                 # Create anonymous session
POST   /auth/refresh                           # Refresh access token
POST   /auth/signout                           # Sign out user
POST   /auth/validate-restaurant-code          # Validate restaurant code
GET    /auth/me                                # Get current user profile
GET    /auth/profile                           # Alias for /me
```

**Router Implementation Structure:**

```python
router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signin/email")
async def sign_in_with_email(
    request: EmailSignInSchema,
    sign_in_use_case: SignInUseCase = Depends(get_signin_use_case)
) -> AuthResponse:
    """Implementation using use case"""

@router.post("/signin/phone")
async def initiate_phone_auth(
    request: PhoneAuthInitiateSchema,
    phone_auth_use_case: PhoneAuthInitiateUseCase = Depends(...)
) -> PhoneAuthInitiateResponse:
    """Implementation using use case"""

# ... and so on for all endpoints
```

**Key Principles:**
- ✅ All endpoints delegate to use cases
- ✅ Use cases handle business logic
- ✅ DTOs bridge presentation and application layers
- ✅ Exception handling maps domain errors to HTTP status codes
- ✅ Consistent response format across all endpoints

---

### Phase 4: Dependency Injection Configuration
**Goal:** Update dependencies.py to provide all use case factories

**Files to Modify:**
- `application/dependencies.py`

**New Factories to Add:**

```python
def get_phone_auth_initiate_use_case(
    auth_repository: IAuthRepository = Depends(get_auth_repository)
) -> PhoneAuthInitiateUseCase:
    return PhoneAuthInitiateUseCase(auth_repository)

def get_phone_auth_verify_use_case(
    auth_repository: IAuthRepository = Depends(get_auth_repository)
) -> PhoneAuthVerifyUseCase:
    return PhoneAuthVerifyUseCase(auth_repository)

def get_sign_out_use_case(
    auth_repository: IAuthRepository = Depends(get_auth_repository)
) -> SignOutUseCase:
    return SignOutUseCase(auth_repository)

def get_validate_restaurant_code_use_case(
    auth_repository: IAuthRepository = Depends(get_auth_repository)
) -> ValidateRestaurantCodeUseCase:
    return ValidateRestaurantCodeUseCase(auth_repository)

def get_email_availability_use_case(
    auth_repository: IAuthRepository = Depends(get_auth_repository)
) -> ValidateEmailAvailabilityUseCase:
    return ValidateEmailAvailabilityUseCase(auth_repository)
```

**Repository Injection Update:**

```python
def get_auth_repository(
    supabase_client: Client = Depends(get_supabase)
) -> IAuthRepository:
    """Returns Supabase-based auth repository"""
    return SupabaseAuthRepository(supabase_client)
```

---

### Phase 5: Application Main Configuration
**Goal:** Update main.py to use new integrated router

**Files to Modify:**
- `main.py`

**Changes:**

```python
# OLD (commented out)
# from .features.auth.presentation.auth_router import router as clean_auth_router
from .features.auth.presentation.supabase_auth_router import router as supabase_auth_router

# NEW
from .features.auth.presentation.auth_router import router as auth_router

# In create_app():
# OLD
app.include_router(supabase_auth_router, tags=["Authentication"])

# NEW
app.include_router(auth_router, tags=["Authentication"])
```

---

### Phase 6: Testing Strategy
**Goal:** Ensure all functionality is properly tested

**Files to Create/Modify:**
- `tests/features/auth/` (comprehensive test suite)

**Test Coverage:**

1. **Repository Tests** (`test_supabase_auth_repository.py`)
   - Test all repository methods with mocked Supabase client
   - Test error handling and exception mapping
   - Test data conversion (Supabase → domain entities)

2. **Use Case Tests**
   - `test_phone_auth_initiate_use_case.py`
   - `test_phone_auth_verify_use_case.py`
   - `test_sign_out_use_case.py`
   - `test_validate_restaurant_code_use_case.py`
   - `test_email_availability_use_case.py`
   - Each test mocks the repository and verifies business logic

3. **Router Integration Tests** (`test_auth_router_integration.py`)
   - Test all endpoints with Supabase client mocked
   - Test error responses and status codes
   - Test response schema validity
   - Test dependency injection

---

## Implementation Phases Timeline

### Phase 1: Infrastructure (1-2 days)
- [ ] Create SupabaseAuthRepository
- [ ] Implement all repository methods
- [ ] Add helper conversion methods
- [ ] Add logging and error handling

### Phase 2: Application (2-3 days)
- [ ] Create new use cases (5 total)
- [ ] Extend auth_dtos.py with new DTOs
- [ ] Implement business logic in each use case
- [ ] Add comprehensive error handling

### Phase 3: Presentation (1-2 days)
- [ ] Create unified auth_router.py
- [ ] Implement all endpoints
- [ ] Add Pydantic schemas
- [ ] Test exception handling

### Phase 4: Configuration (1 day)
- [ ] Update dependencies.py
- [ ] Update main.py
- [ ] Test import resolution

### Phase 5: Testing (2-3 days)
- [ ] Write unit tests for repository
- [ ] Write unit tests for all use cases
- [ ] Write integration tests for router
- [ ] Manual testing of all endpoints

### Phase 6: Cleanup & Documentation (1 day)
- [ ] Archive old supabase_auth_router.py
- [ ] Remove duplicate code
- [ ] Update project documentation
- [ ] Verify no broken imports

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────┐
│          Presentation Layer (HTTP)              │
│  ┌───────────────────────────────────────────┐  │
│  │  Unified auth_router.py                   │  │
│  │  - /auth/signin/email                     │  │
│  │  - /auth/signup/email                     │  │
│  │  - /auth/signin/phone                     │  │
│  │  - /auth/verify/phone                     │  │
│  │  - /auth/signout                          │  │
│  │  - /auth/refresh                          │  │
│  │  - /auth/anonymous-session                │  │
│  │  - /auth/validate-restaurant-code         │  │
│  │  - /auth/me                               │  │
│  └───────────────────────────────────────────┘  │
└──────────────────┬────────────────────────────┬──┘
                   │                            │
┌──────────────────▼─────────────────────┐     │
│   Application Layer (Use Cases)         │     │
│ ┌───────────────────────────────────┐  │     │
│ │ SignInUseCase                     │  │     │
│ │ SignUpUseCase                     │  │     │
│ │ PhoneAuthInitiateUseCase          │  │     │
│ │ PhoneAuthVerifyUseCase            │  │     │
│ │ RefreshTokenUseCase               │  │     │
│ │ AnonymousSessionUseCase           │  │     │
│ │ SignOutUseCase                    │  │     │
│ │ ValidateRestaurantCodeUseCase     │  │     │
│ │ ValidateEmailAvailabilityUseCase  │  │     │
│ └───────────────────────────────────┘  │     │
└──────────────────┬──────────────────────┘     │
                   │                            │
┌──────────────────▼────────────────────┐       │
│   Domain Layer (Interfaces)            │       │
│ ┌────────────────────────────────────┐ │       │
│ │ IAuthRepository (interface)         │ │       │
│ │ - sign_in_with_email()              │ │       │
│ │ - sign_up_with_email()              │ │       │
│ │ - initiate_phone_auth()             │ │       │
│ │ - verify_phone_otp()                │ │       │
│ │ - refresh_session()                 │ │       │
│ │ - sign_out()                        │ │       │
│ │ - get_user_by_id/email/phone()      │ │       │
│ │ - update_user_metadata()            │ │       │
│ └────────────────────────────────────┘ │       │
└──────────────────┬─────────────────────┘       │
                   │                            │
┌──────────────────▼──────────────────────────┐  │
│   Infrastructure Layer (Supabase)           │  │
│ ┌───────────────────────────────────────┐  │  │
│ │ SupabaseAuthRepository (impl)          │  │  │
│ │ ✅ Implements IAuthRepository          │  │  │
│ │ ✅ Uses Supabase client                │  │  │
│ │ ✅ Converts responses to domain        │  │  │
│ └───────────────────────────────────────┘  │  │
└──────────────────┬──────────────────────────┘  │
                   │                            │
        ┌──────────▼──────────┐                 │
        │  Supabase Backend   │ ◄───────────────┘
        │  - Auth API         │
        │  - Database (RPC)   │
        │  - User Tables      │
        └─────────────────────┘
```

---

## Benefits of This Integration

### Code Quality
- ✅ **Separation of Concerns:** Each layer has a single responsibility
- ✅ **Testability:** Mock repositories and test business logic independently
- ✅ **Maintainability:** Changes to Supabase API isolated in repository
- ✅ **Reusability:** Use cases can be used by multiple presentation layers

### Architecture
- ✅ **Clean Architecture:** Follows industry best practices
- ✅ **DDD-Inspired:** Domain entities represent real business concepts
- ✅ **SOLID Principles:** Dependency inversion, single responsibility
- ✅ **Scalability:** Easy to add new auth methods without restructuring

### Features
- ✅ **Complete:** All features from both routers combined
- ✅ **Consistent:** Unified error handling and response format
- ✅ **Secure:** Proper logging and audit trails
- ✅ **Pragmatic:** Leverages Supabase capabilities effectively

---

## Success Criteria

- ✅ All auth endpoints functional with same behavior as Supabase router
- ✅ Code follows Clean Architecture principles
- ✅ All use cases have corresponding repositories
- ✅ Comprehensive test coverage (>80%)
- ✅ No import errors or circular dependencies
- ✅ Consistent error handling and HTTP status codes
- ✅ Proper logging for audit trails
- ✅ Documentation updated

---

## Questions for Review

1. **Route Prefix:** Should we keep `/auth` prefix or change to match Clean router?
2. **Phone Auth:** Do we need to support phone auth or can we skip it initially?
3. **Restaurant Code:** Is restaurant code validation critical or optional feature?
4. **Backward Compatibility:** Do we need to support both routes temporarily?
5. **Authentication Method:** Any preference for JWT vs session tokens?

---

## Next Steps

1. Review and approve this plan
2. Start Phase 1: Infrastructure (SupabaseAuthRepository)
3. Proceed through phases sequentially
4. Regular testing at each phase boundary
5. Final integration testing before deployment
