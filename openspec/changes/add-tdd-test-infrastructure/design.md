# Design: TDD Test Infrastructure

## Context

The Zergo QR system is a full-stack application with FastAPI backend and Flutter frontend. The codebase follows Clean Architecture principles with clear separation of concerns. Current state:

- **Testing Frameworks**: Configured but not utilized (pytest, flutter_test)
- **CI/CD**: Pipeline exists but tests don't provide meaningful coverage
- **Code Quality**: Existing features have bugs, no regression prevention
- **Development Speed**: Slowed by manual testing and bug fixes
- **Team**: Migrating from BMAD to OpenSpec methodology

**Stakeholders**:
- Backend developers (Python/FastAPI)
- Frontend developers (Flutter/Dart)
- QA team (needs automated regression suite)
- Product owners (need confidence in releases)

**Constraints**:
- Must maintain backward compatibility
- Cannot break existing functionality
- Need gradual migration path (big bang impossible)
- Team has limited TDD experience

## Goals / Non-Goals

### Goals
1. Establish comprehensive test coverage for critical business logic (90% backend, 80% frontend)
2. Create TDD workflow that integrates with existing development process
3. Provide test utilities that reduce boilerplate and speed up test writing
4. Document testing patterns and best practices
5. Enable automated regression testing in CI/CD
6. Support both testing existing features (bug-first) and new features (test-first)

### Non-Goals
- 100% test coverage (diminishing returns)
- E2E UI automation (too brittle, focus on unit/integration)
- Performance/load testing (out of scope for now)
- Contract testing with external services (future consideration)

## Decisions

### Decision 1: Testing Framework Selection

**Backend - Pytest with Layered Testing Strategy**
```
Unit Tests (70%) → Integration Tests (20%) → API Tests (10%)
```

**Why**:
- Pytest is already configured and widely adopted
- Excellent async support (pytest-asyncio)
- Powerful fixtures for setup/teardown
- Clear test discovery and organization
- Great integration with coverage tools

**Alternatives Considered**:
- unittest: Too verbose, less pythonic
- nose2: Less active community
- No framework: Insufficient structure

### Decision 2: Frontend Testing Pyramid

**Flutter - Widget-Centric Testing**
```
Unit Tests (50%) → Widget Tests (40%) → Integration Tests (10%)
```

**Why**:
- Flutter's widget testing is unique and powerful
- Tests are fast and reliable
- Golden tests provide visual regression coverage
- Minimal brittle E2E tests

**Alternatives Considered**:
- Patrol (E2E): Keep for critical user journeys only
- Integration tests for everything: Too slow and flaky

### Decision 3: Test Data Management

**Use Factories and Fixtures**
- Backend: `factory_boy` + pytest fixtures
- Frontend: Fake repositories + mocktail

**Why**:
- Eliminates test data coupling
- Easy to create varied test scenarios
- More maintainable than hardcoded fixtures

**Alternatives Considered**:
- Static fixtures: Too rigid, hard to maintain
- Database snapshots: Overkill for unit tests

### Decision 4: Testing Existing Features (Bug-First TDD)

**Workflow for Legacy Code**:
```
1. Write failing test exposing bug
2. Fix bug (minimal change)
3. Verify test passes
4. Refactor if needed (tests guard against regression)
```

**Why**:
- Provides immediate value (fixes bugs)
- Tests pay for themselves immediately
- Incremental approach doesn't block development
- Natural way to increase coverage

**Alternatives Considered**:
- Rewrite then test: Too risky, introduces new bugs
- Ignore old code, only test new: Technical debt grows

### Decision 5: Coverage Requirements

**Graded Coverage Targets**:
- Backend: 60% overall (business logic 80%, infrastructure 50%)
- Frontend: 60% overall (controllers/widgets 80%, screens 50%)
- Enforced in CI/CD with automatic PR blocking

**Why**:
- Matches pragmatic testing goals (80% business logic, 60% overall)
- Allows fast test execution (<5 minutes for full suite)
- Focuses coverage on high-risk code (business logic)
- Lower coverage for simple CRUD (models, routes, screens)
- Industry standard for well-tested applications with fast feedback

**Alternatives Considered**:
- 100% coverage: Diminishing returns, tests themselves can be buggy
- No coverage requirement: No accountability

### Decision 6: Test Organization

**Mirror Production Structure**
```
apps/backend/app/features/auth/
  domain/
  application/
  infrastructure/
  presentation/

apps/backend/tests/features/auth/
  test_auth_entities.py
  test_auth_use_cases.py
  test_auth_repos.py
  test_auth_router.py
```

**Why**:
- Easy to find tests for specific code
- Clear relationship between test and production code
- Follows single responsibility principle

**Alternatives Considered**:
- Separate test structure by type (unit/integration/e2e): Harder to navigate

### Decision 7: CI/CD Integration

**Automated Quality Gates**:
```yaml
- PR must pass all tests
- Coverage must meet threshold (80% business logic, 60% overall)
- Test suite must complete in under 5 minutes
- No format violations
- No type errors
- Security scan clean
```

**Execution Speed Targets**:
```bash
# Fast feedback during development
pytest tests/unit/ -n auto  # < 1 minute

# Full suite with coverage
pytest -n auto --cov=app    # < 5 minutes

# Slow tests (run separately)
pytest tests/integration/ tests/e2e/ -n auto
```

**Why**:
- Enforces standards automatically
- Prevents low-quality code from merging
- Reduces code review burden

**Alternatives Considered**:
- Manual enforcement: Inconsistent, easily bypassed

### Decision 8: Mocking Strategy

**Pragmatic Mocking**:
- Mock external dependencies (database, APIs, services)
- Don't mock internal code (test real interactions)
- Use real implementations when fast and reliable (in-memory entities)

**Why**:
- Tests stay focused on unit under test
- Faster than real dependencies
- More reliable than integration tests for unit logic

**Alternatives Considered**:
- No mocking: Too slow, tests coupled to infrastructure
- Over-mocking: Tests become tautologies, don't catch real bugs

## Architecture

### Backend Test Architecture

```
tests/
├── conftest.py                      # Root fixtures and configuration
├── fixtures/                        # Shared fixtures
│   ├── auth_fixtures.py
│   ├── db_fixtures.py
│   └── restaurant_fixtures.py
├── factories/                       # Test data factories
│   ├── auth_factory.py
│   └── restaurant_factory.py
├── utils/                           # Test helpers
│   ├── assertions.py
│   └── helpers.py
├── unit/                            # Fast, isolated tests
│   ├── features/
│   │   ├── auth/
│   │   └── restaurants/
│   └── core/
├── integration/                     # Multi-component tests
│   ├── test_auth_flow.py
│   └── test_order_flow.py
└── api/                             # Endpoint tests
    ├── test_auth_endpoints.py
    └── test_restaurant_endpoints.py
```

### Frontend Test Architecture

```
test/
├── flutter_test_config.dart         # Test configuration
├── helpers/                         # Test utilities
│   ├── test_helpers.dart
│   └── mock_helpers.dart
├── mocks/                           # Mock implementations
│   └── repositories/
├── unit/                            # Pure logic tests
│   ├── features/
│   │   ├── auth/
│   │   └── restaurants/
│   └── core/
├── widget/                          # Widget tests
│   └── features/
│       ├── auth/
│       └── restaurants/
├── golden/                          # Screenshot tests
│   └── widgets/
└── integration/                     # User journey tests
    └── features/
```

## Testing Patterns

### Backend Testing Patterns

**1. Arrange-Act-Assert (AAA)**
```python
def test_user_login_success():
    # Arrange
    user = create_user(email="test@example.com")
    login_data = UserLoginDto(email="test@example.com", password="password")

    # Act
    result = await signin_use_case(login_data)

    # Assert
    assert result.success is True
    assert result.token is not None
```

**2. Parameterized Tests**
```python
@pytest.mark.parametrize("email,expected", [
    ("valid@email.com", True),
    ("invalid", False),
    ("", False),
])
def test_email_validation(email, expected):
    assert validate_email(email) == expected
```

**3. Fixture Injection**
```python
def test_create_restaurant(db_session, auth_header):
    response = client.post("/api/restaurants",
                         json=restaurant_data,
                         headers=auth_header)
    assert response.status_code == 201
```

### Frontend Testing Patterns

**1. Widget Test with Mocks**
```dart
testWidgets('LoginScreen shows error on invalid email',
    (tester) async {
  // Arrange
  final mockAuthRepo = MockAuthRepository();
  await tester.pumpWidget(
    MaterialApp(
      home: LoginScreen(authRepo: mockAuthRepo),
    ),
  );

  // Act
  await tester.enterText(
    find.byKey(Key('email-field')),
    'invalid-email',
  );
  await tester.tap(find.byKey(Key('login-button')));
  await tester.pump();

  // Assert
  expect(find.text('Invalid email'), findsOneWidget);
});
```

**2. Golden Test**
```dart
testGolden('RestaurantCard golden',
  (tester) async {
    await tester.pumpWidget(
      RestaurantCard(restaurant: mockRestaurant),
    );
    await expectLater(
      find.byType(RestaurantCard),
      matchesGoldenFile('goldens/restaurant_card.png'),
    );
  },
);
```

## TDD Workflows

### For New Features (Test-First)

```
1. Write spec/scenarios → 2. Write failing test →
3. Write minimal code → 4. Refactor → 5. Document
```

**Example**:
```python
# Step 1: Write failing test
def test_add_staff_to_restaurant():
    restaurant = create_restaurant()
    staff_data = StaffCreateDto(name="John", role="waiter")

    result = add_staff_use_case(restaurant.id, staff_data)

    assert result.success
    assert restaurant.staff_count == 1

# Step 2: Run test → FAIL (no implementation)

# Step 3: Write minimal code to pass
def add_staff_use_case(restaurant_id, data):
    restaurant = db.get(restaurant_id)
    restaurant.add_staff(data)
    return SuccessResult()

# Step 4: Refactor for clean code

# Step 5: Document in spec
```

### For Existing Bugs (Bug-First TDD)

```
1. Reproduce bug → 2. Write failing test →
3. Fix bug → 4. Verify test passes → 5. Look for related bugs
```

**Example**:
```python
# Step 1: Bug report - login fails with valid token

# Step 2: Write failing test that exposes bug
def test_login_with_valid_token():
    token = generate_valid_token()
    response = client.get("/api/auth/me",
                         headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200  # Currently fails with 401

# Step 3: Fix bug (found token validation issue)
# Fixed: Added token refresh logic

# Step 4: Verify test passes

# Step 5: Add tests for token refresh, expiration, etc.
```

## Risks / Trade-offs

### Risk 1: Initial Velocity Drop
- **Impact**: Development slows 30-50% initially
- **Probability**: High
- **Mitigation**:
  - Start with critical features only
  - Provide templates and examples
  - Pair programming for knowledge transfer
  - Celebrate early wins (bugs caught)

### Risk 2: Brittle Tests
- **Impact**: Tests fail due to unrelated changes
- **Probability**: Medium
- **Mitigation**:
  - Focus on behavior over implementation
  - Avoid testing private methods
  - Use black-box testing style
  - Regular test maintenance

### Risk 3: Test Coverage Gaming
- **Impact**: High coverage, low quality
- **Probability**: Medium
- **Mitigation**:
  - Code review includes test review
  - Require meaningful assertions
  - Track branch coverage, not just line
  - Manual testing for critical flows

### Risk 4: Learning Curve Resistance
- **Impact**: Team doesn't adopt TDD
- **Probability**: Medium
- **Mitigation**:
  - Comprehensive documentation
  - Interactive workshops
  - Mentoring and code review feedback
  - Start with one feature as pilot

## Migration Plan

### Phase 1: Foundation (Week 1-2)
- [ ] Set up test utilities and fixtures
- [ ] Create test templates and examples
- [ ] Document TDD workflows
- [ ] Configure CI/CD quality gates
- [ ] Team training session

### Phase 2: Critical Features (Week 3-4)
- [ ] Add tests for auth flow (highest priority)
- [ ] Add tests for restaurant CRUD
- [ ] Add tests for order flow
- [ ] Fix exposed bugs
- [ ] Reach 70% coverage target

### Phase 3: Expand Coverage (Week 5-8)
- [ ] Add tests for remaining features
- [ ] Create integration test suite
- [ ] Add golden tests for UI
- [ ] Reach 90% backend, 80% frontend coverage

### Phase 4: Maintenance (Ongoing)
- [ ] Update tests with features
- [ ] Regular test review and cleanup
- [ ] Monthly coverage reports
- [ ] Continuous improvement

### Rollback Strategy
If test coverage blocks critical release:
1. Temporarily raise coverage threshold in CI
2. Create issue for technical debt
3. Must have plan to reach target within 2 sprints
4. Requires tech lead approval

## Open Questions

1. **Should we enforce TDD for ALL new code or encourage it?**
   - **Recommendation**: Encourage first, enforce after 2-month learning period

2. **What's the process for temporarily disabling tests?**
   - **Recommendation**: Requires tech lead approval + issue created

3. **How do we handle test data privacy?**
   - **Recommendation**: Use synthetic data only, never real customer data

4. **Should we test database migrations?**
   - **Recommendation**: Yes, add migration tests for critical schema changes

5. **How often should we update golden tests?**
   - **Recommendation**: Only when design changes intentionally, require review

## Metrics & Success Criteria

### Success Metrics
- 90% backend coverage, 80% frontend coverage by end of Phase 3
- All PRs include tests for new code
- Zero critical bugs in production for 3 consecutive releases
- Test suite runs in under 10 minutes (backend) and 5 minutes (frontend)
- 80% of bugs caught by tests before production

### Quality Signals
- Reduced bug report count
- Faster feature development (after learning period)
- Confident refactoring without breaking changes
- New developers onboard faster with test examples
