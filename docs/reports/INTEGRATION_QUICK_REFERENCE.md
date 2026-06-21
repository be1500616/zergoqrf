# Authentication Integration - Quick Reference Guide

## Quick Overview

**Goal:** Merge Supabase Router (working) with Clean Architecture approach (proper design)

**Result:** Single integrated router with Clean Architecture + all Supabase features

**Timeline:** ~6 working days

---

## 6-Phase Implementation

### Phase 1: Infrastructure (SupabaseAuthRepository)
**File:** `infrastructure/supabase_auth_repository.py` (NEW)

**What to create:**
```python
class SupabaseAuthRepository(IAuthRepository):
    def __init__(self, supabase_client: Client)

    # Implement these methods:
    async def sign_in_with_email(email, password) → AuthenticationResult
    async def sign_up_with_email(email, password, name, role, restaurant_id) → AuthenticationResult
    async def initiate_phone_auth(phone) → bool
    async def verify_phone_otp(phone, otp_code, name) → AuthenticationResult
    async def refresh_session(refresh_token) → AuthenticationResult
    async def sign_out(user_id) → bool
    async def get_user_by_id(user_id) → Optional[User]
    async def get_user_by_email(email) → Optional[User]
    async def get_user_by_phone(phone) → Optional[User]
    async def update_user_metadata(user_id, metadata) → bool
```

**Copy from:** `supabase_auth_router.py` (the actual Supabase calls)

---

### Phase 2: Application Layer (Use Cases + DTOs)

#### Part A: Create New Use Cases

**PhoneAuthInitiateUseCase**
- File: `application/use_cases/phone_auth_initiate_use_case.py`
- Calls: `auth_repository.initiate_phone_auth(phone)`
- Returns: DTO with message, phone, otp_sent=true

**PhoneAuthVerifyUseCase**
- File: `application/use_cases/phone_auth_verify_use_case.py`
- Calls: `auth_repository.verify_phone_otp(phone, otp, name)`
- Returns: AuthTokenResponseDTO with tokens + user info

**SignOutUseCase**
- File: `application/use_cases/sign_out_use_case.py`
- Calls: `auth_repository.sign_out(user_id)`
- Returns: Success response DTO

**ValidateRestaurantCodeUseCase**
- File: `application/use_cases/validate_restaurant_code_use_case.py`
- Calls: Supabase directly (query restaurants table + create session)
- Returns: Restaurant branding + session token

**ValidateEmailAvailabilityUseCase**
- File: `application/use_cases/validate_email_availability_use_case.py`
- Calls: `auth_repository.get_user_by_email()` or Supabase query
- Returns: Email availability status

#### Part B: Extend DTOs

**File:** `application/auth_dtos.py` (extend existing)

**Add these DTOs:**
```python
class PhoneAuthInitiateRequestDTO:
    phone: str

class PhoneAuthVerifyRequestDTO:
    phone: str
    otp_code: str
    name: Optional[str] = None

class SignOutRequestDTO:
    pass

class SignOutResponseDTO:
    message: str
    success: bool

class RestaurantCodeRequestDTO:
    code: str

class EmailAvailabilityRequestDTO:
    email: str

class EmailAvailabilityResponseDTO:
    available: bool
```

---

### Phase 3: Presentation Layer

**File:** `presentation/auth_router.py` (REPLACE - combines both routers)

**Endpoints to implement:**
```python
router = APIRouter(prefix="/auth", tags=["Authentication"])

# Email endpoints
@router.post("/signin/email")
@router.post("/signup/email")
@router.get("/validate/email")

# Phone endpoints
@router.post("/signin/phone")
@router.post("/verify/phone")

# Session endpoints
@router.post("/anonymous-session")
@router.post("/refresh")
@router.post("/signout")

# User endpoints
@router.get("/me")
@router.get("/profile")

# Extra endpoints
@router.post("/validate-restaurant-code")
```

**Key principle:**
- Each endpoint extracts schema → creates DTO → calls use case → returns response
- All use cases injected via FastAPI Depends()

---

### Phase 4: Dependency Injection

**File:** `application/dependencies.py` (extend existing)

**Add these factory functions:**
```python
def get_auth_repository(supabase: Client = Depends(get_supabase)) → IAuthRepository:
    return SupabaseAuthRepository(supabase)

def get_phone_auth_initiate_use_case(
    auth_repo: IAuthRepository = Depends(get_auth_repository)
) → PhoneAuthInitiateUseCase:
    return PhoneAuthInitiateUseCase(auth_repo)

# Similar factories for other 4 new use cases...
```

---

### Phase 5: Main Configuration

**File:** `main.py` (simple change)

**Change from:**
```python
from .features.auth.presentation.supabase_auth_router import router as supabase_auth_router
# ...
app.include_router(supabase_auth_router, tags=["Authentication"])
```

**Change to:**
```python
from .features.auth.presentation.auth_router import router as auth_router
# ...
app.include_router(auth_router, tags=["Authentication"])
```

---

### Phase 6: Testing

**Create comprehensive tests:**
- `tests/features/auth/test_supabase_auth_repository.py`
- `tests/features/auth/test_phone_auth_use_cases.py`
- `tests/features/auth/test_restaurant_code_use_case.py`
- `tests/features/auth/test_auth_router_integration.py`

**Test approach:**
1. Mock Supabase client in repository tests
2. Mock repository in use case tests
3. Mock repository in router integration tests

---

## File Structure (New Organization)

```
apps/backend/app/features/auth/
├── domain/
│   ├── auth_entities.py      (KEEP - User, AuthSession, etc.)
│   ├── auth_vos.py           (KEEP - Email, Password, Token, etc.)
│   ├── auth_repos.py         (KEEP - IAuthRepository interface)
│   └── auth_exceptions.py    (KEEP - all exception types)
│
├── application/
│   ├── auth_dtos.py          (EXTEND - add new DTOs)
│   ├── dependencies.py       (EXTEND - add new factories)
│   └── use_cases/
│       ├── signup_use_case.py                   (KEEP)
│       ├── signin_use_case.py                   (KEEP)
│       ├── refresh_token_use_case.py            (KEEP)
│       ├── anonymous_session_use_case.py        (KEEP)
│       ├── get_current_user_use_case.py         (KEEP)
│       ├── phone_auth_initiate_use_case.py      (NEW)
│       ├── phone_auth_verify_use_case.py        (NEW)
│       ├── sign_out_use_case.py                 (NEW)
│       ├── validate_restaurant_code_use_case.py (NEW)
│       └── validate_email_availability_use_case.py (NEW)
│
├── infrastructure/
│   ├── auth_repos_impl.py                   (KEEP - basic implementations)
│   ├── supabase_auth_repository.py          (NEW - main auth repo)
│   └── supabase_auth_repository_impl.py     (ARCHIVE - old file)
│
├── presentation/
│   ├── auth_router.py                       (REPLACE - integrated)
│   ├── auth_schemas.py                      (KEEP - Pydantic models)
│   ├── auth_exception_handlers.py           (KEEP)
│   ├── supabase_dependencies.py             (KEEP - for use case dependencies)
│   ├── error_helpers.py                     (KEEP - error utilities)
│   └── supabase_auth_router.py              (ARCHIVE - old file)
│
└── tests/
    ├── test_supabase_auth_repository.py     (NEW)
    ├── test_phone_auth_use_cases.py         (NEW)
    ├── test_restaurant_code_use_case.py     (NEW)
    ├── test_email_availability_use_case.py  (NEW)
    └── test_auth_router_integration.py      (NEW)
```

---

## Key Implementation Details

### SupabaseAuthRepository Implementation Strategy

**Copy relevant code from `supabase_auth_router.py`:**

1. **sign_in_with_email():**
   - Copy: `supabase.auth.sign_in_with_password()`
   - Convert Supabase response to AuthenticationResult + User entity
   - Handle errors properly

2. **sign_up_with_email():**
   - Copy: `supabase.auth.sign_up()` logic
   - Create user metadata with name, role, restaurant_id
   - Return AuthenticationResult

3. **initiate_phone_auth():**
   - Copy: `supabase.auth.sign_in_with_otp()` logic
   - Return boolean success

4. **verify_phone_otp():**
   - Copy: `supabase.auth.verify_otp()` logic
   - Update user metadata with name if provided
   - Return AuthenticationResult

5. **Anonymous sessions & restaurant codes:**
   - Can use Supabase RPC calls or direct table queries
   - Return appropriate entities/responses

### Data Flow Example: Phone OTP

```
1. Client: POST /auth/signin/phone
   ├─ Body: { "phone": "+1234567890" }

2. Router:
   ├─ Parse schema → PhoneAuthInitiateRequestDTO
   ├─ Inject PhoneAuthInitiateUseCase
   └─ Call use_case.execute(dto)

3. Use Case:
   ├─ Create Phone value object (validates format)
   ├─ Call auth_repository.initiate_phone_auth(phone)
   └─ Return response DTO

4. Repository:
   ├─ Call supabase.auth.sign_in_with_otp({"phone": ...})
   ├─ Handle any Supabase errors
   └─ Return True or raise AuthenticationError

5. Router:
   ├─ Convert response DTO to Pydantic schema
   └─ Return HTTP 200 with { "otp_sent": true }

6. Client receives: { "message": "OTP sent", "phone": "...", "otp_sent": true }
```

---

## Common Pitfalls & Solutions

### ❌ Pitfall 1: Circular Imports
**Problem:** importing from presentation layer in infrastructure

**Solution:**
- ✅ Never import routers in repositories/use cases
- ✅ Use DTOs (application layer) as boundary
- ✅ Exceptions always in domain layer

### ❌ Pitfall 2: Supabase Client Not Injected
**Problem:** Creating Supabase client in repository __init__

**Solution:**
- ✅ Always receive Client via constructor
- ✅ Use dependency injection from FastAPI
- ✅ Makes testing easy (mock client)

### ❌ Pitfall 3: Business Logic in Router
**Problem:** Moving code from supabase_auth_router.py directly to new router

**Solution:**
- ✅ Extract logic into use cases
- ✅ Router only handles: schema parsing, DI, HTTP response
- ✅ All logic in use cases

### ❌ Pitfall 4: Not Converting Supabase Objects to Domain
**Problem:** Returning Supabase user object directly

**Solution:**
- ✅ Repository converts Supabase → domain entities
- ✅ Use case works with domain entities only
- ✅ Router converts DTOs → HTTP response

### ❌ Pitfall 5: Inconsistent Error Handling
**Problem:** Different error handling in different use cases

**Solution:**
- ✅ Use domain exceptions consistently
- ✅ Repository maps Supabase errors → domain exceptions
- ✅ Exception mapper in presentation layer handles all

---

## Testing Strategy Checklist

### Repository Tests
- [ ] Test email/password sign in success path
- [ ] Test email/password sign in with wrong credentials
- [ ] Test user already exists error on signup
- [ ] Test phone OTP initiation
- [ ] Test phone OTP verification
- [ ] Test token refresh
- [ ] Test user lookup by ID, email, phone
- [ ] Test error cases (network, validation, etc.)

### Use Case Tests
- [ ] Test all happy paths
- [ ] Test error conditions
- [ ] Test validation (email format, password strength, phone format)
- [ ] Test data transformation (entity → DTO)

### Router Integration Tests
- [ ] Test all endpoint paths
- [ ] Test request/response schemas
- [ ] Test dependency injection
- [ ] Test HTTP status codes
- [ ] Test error responses

---

## Validation Checklist (Before Going Live)

- [ ] All endpoints return expected responses
- [ ] Email/password auth works
- [ ] Phone OTP auth works
- [ ] Anonymous sessions work
- [ ] Token refresh works
- [ ] Sign out works
- [ ] Restaurant code validation works
- [ ] Email availability check works
- [ ] Get current user works
- [ ] All error cases return correct HTTP status
- [ ] Logging shows auth events
- [ ] No import errors
- [ ] No circular dependencies
- [ ] All tests pass
- [ ] Test coverage > 80%

---

## Migration Checklist

### Before Migration
- [ ] New router fully tested
- [ ] All endpoints verified in local environment
- [ ] Backup of current configuration
- [ ] Rollback plan documented

### During Migration
- [ ] Stop current router in main.py line 126
- [ ] Start new router in main.py
- [ ] Import new router instead of old
- [ ] Run health check endpoint
- [ ] Test critical auth flows

### After Migration
- [ ] Archive old supabase_auth_router.py file
- [ ] Update documentation
- [ ] Monitor logs for errors
- [ ] Verify all endpoints in staging
- [ ] Get approval from team
- [ ] Deploy to production

---

## Reference Files

### Files to Create (NEW)
1. `infrastructure/supabase_auth_repository.py`
2. `application/use_cases/phone_auth_initiate_use_case.py`
3. `application/use_cases/phone_auth_verify_use_case.py`
4. `application/use_cases/sign_out_use_case.py`
5. `application/use_cases/validate_restaurant_code_use_case.py`
6. `application/use_cases/validate_email_availability_use_case.py`

### Files to Modify (EXTEND)
1. `application/auth_dtos.py` - Add new DTOs
2. `application/dependencies.py` - Add use case factories
3. `presentation/auth_schemas.py` - Add Pydantic models
4. `main.py` - Switch to new router

### Files to Replace (REPLACE)
1. `presentation/auth_router.py` - Merge both routers

### Files to Archive (KEEP but don't use)
1. `presentation/supabase_auth_router.py` - Backup
2. `infrastructure/auth_repos_impl.py` - May keep for reference

---

## Estimated Effort

| Phase | Task | Est. Hours | Notes |
|-------|------|-----------|-------|
| 1 | SupabaseAuthRepository | 4-6 | Copy logic from supabase_auth_router |
| 2 | Use Cases (5 new) | 6-8 | Follow existing patterns |
| 2 | DTOs | 2-3 | Straightforward additions |
| 3 | Unified Router | 4-5 | Combine both routers |
| 3 | Schemas | 2-3 | Add Pydantic models |
| 4 | Dependencies | 2-3 | Add factories |
| 5 | main.py | 0.5 | One-line change |
| 6 | Testing | 8-12 | Comprehensive test suite |
| Final | Integration & QA | 2-3 | End-to-end validation |
| **TOTAL** | | **30-40 hours** | **~6 working days** |

---

## Success Criteria (Final Checklist)

- ✅ All 11 endpoints functional
- ✅ Clean Architecture principles maintained
- ✅ All features from Supabase router included
- ✅ Test coverage ≥ 80%
- ✅ No import errors
- ✅ No circular dependencies
- ✅ Proper logging at all layers
- ✅ Consistent error handling
- ✅ Dependency injection working
- ✅ Zero-downtime migration possible
- ✅ Documentation updated
- ✅ Code reviewed and approved

---

## Quick Start Commands

```bash
# Phase 1: Create repository file
touch apps/backend/app/features/auth/infrastructure/supabase_auth_repository.py

# Phase 2: Create use case files
mkdir -p apps/backend/app/features/auth/application/use_cases
touch apps/backend/app/features/auth/application/use_cases/phone_auth_*.py
touch apps/backend/app/features/auth/application/use_cases/sign_out_use_case.py
touch apps/backend/app/features/auth/application/use_cases/validate_*.py

# Phase 3: Replace router
# (backup old first)
cp apps/backend/app/features/auth/presentation/supabase_auth_router.py \
   apps/backend/app/features/auth/presentation/supabase_auth_router.py.bak

# Phase 6: Run tests
pytest apps/backend/tests/features/auth/ -v --cov

# Final: Check imports
python -m py_compile apps/backend/app/main.py
```

---

## Questions? Refer Back To

- **Full details:** `AUTH_INTEGRATION_PLAN.md`
- **Comparison:** `ROUTER_COMPARISON.md`
- **Current code:** Check `supabase_auth_router.py` for implementation patterns
- **Architecture:** Review `domain/auth_repos.py` for interfaces

---

## Next Step

**Read:** `AUTH_INTEGRATION_PLAN.md` for detailed implementation guide

**Start:** Phase 1 - Create SupabaseAuthRepository
