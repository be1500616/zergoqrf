# Testing Guide

This document provides comprehensive information about testing in the ZERGO QR project, covering both backend (Python/FastAPI) and frontend (Flutter) testing strategies.

## Table of Contents

- [Overview](#overview)
- [Backend Testing](#backend-testing)
- [Frontend Testing](#frontend-testing)
- [Test Coverage](#test-coverage)
- [Continuous Integration](#continuous-integration)
- [Running Tests](#running-tests)
- [Writing Tests](#writing-tests)
- [Best Practices](#best-practices)

## Overview

Our testing strategy follows the test pyramid principle:

```
    /\
   /E2E\
  /      \
 /Integration\
/    Unit     \
```

- **Unit Tests**: Fast, isolated tests for individual functions/classes
- **Integration Tests**: Test component interactions
- **E2E Tests**: Test complete user journeys

## Backend Testing

### Framework: pytest + FastAPI TestClient

**Key Features:**

- Async support with `pytest-asyncio`
- API testing with `TestClient`
- Mock external services (Supabase)
- Coverage reporting with `pytest-cov`

### Test Structure

```
apps/backend/tests/
├── __init__.py
├── conftest.py              # Global fixtures
├── test_main.py             # Main app tests
├── test_utils.py            # Test utilities
└── mocks/
    ├── __init__.py
    └── external_services.py  # Mock implementations
```

### Running Backend Tests

```bash
# Navigate to backend directory
cd apps/backend

# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test types
make test-unit
make test-integration

# Run tests with watch mode
pytest-watch
```

### Example Backend Test

```python
@pytest.mark.asyncio
class TestHealthCheck:
    async def test_health_check_returns_ok_status(self, test_client: AsyncClient):
        # Arrange
        # (Setup done in fixtures)

        # Act
        response = await test_client.get("/healthz")

        # Assert
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
```

## Frontend Testing

### Framework: flutter_test + mocktail + golden_toolkit

**Key Features:**

- Unit tests for business logic
- Widget tests for UI components
- Integration tests for complete flows
- Golden tests for visual regression
- Mock services with mocktail

### Test Structure

```
apps/frontend/test/
├── helpers/
│   └── test_helpers.dart     # Test utilities
├── unit/
│   └── main_test.dart        # Unit tests
├── widget/
│   └── home_screen_test.dart # Widget tests
├── golden/
│   └── golden_tests.dart     # Visual regression tests
├── mocks/
│   └── mock_services.dart    # Mock implementations
└── flutter_test_config.dart  # Test configuration
```

### Running Frontend Tests

```bash
# Navigate to frontend directory
cd apps/frontend

# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test types
make test-unit      # Unit tests
make test-widget    # Widget tests
make test-golden    # Golden tests
make test-integration # Integration tests

# Update golden files
make test-golden-update

# Generate HTML coverage report
make test-cov-html
```

### Example Frontend Tests

**Unit Test:**

```dart
group('TestDataFactory Tests', () {
  test('should create valid user data', () {
    // Act
    final userData = TestDataFactory.createUserData();

    // Assert
    expect(userData, isA<Map<String, dynamic>>());
    expect(userData['email'], isNotNull);
  });
});
```

**Widget Test:**

```dart
testWidgets('HomeScreen displays welcome message', (tester) async {
  // Arrange & Act
  await WidgetTestHelpers.pumpWidgetWithGetX(
    tester,
    const HomeScreen(),
  );

  // Assert
  expect(find.text('Welcome to ZERGO QR'), findsOneWidget);
});
```

**Golden Test:**

```dart
testGoldens('HomeScreen renders correctly', (tester) async {
  await tester.pumpWidgetBuilder(
    const HomeScreen(),
    wrapper: materialAppWrapper(),
  );

  await screenMatchesGolden(tester, 'home_screen_default');
});
```

## Test Coverage

### Coverage Targets

- **Backend**: ≥ 90%
- **Frontend**: ≥ 80%
- **Overall**: ≥ 85%

### Coverage Reports

**Backend:**

```bash
cd apps/backend
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

**Frontend:**

```bash
cd apps/frontend
flutter test --coverage
genhtml coverage/lcov.info -o coverage/html
open coverage/html/index.html
```

### Coverage in CI/CD

Coverage is automatically:

- Measured in GitHub Actions
- Uploaded to Codecov
- Reported in PR comments
- Used to enforce quality gates

## Continuous Integration

### GitHub Actions Workflow

Our CI pipeline (`/.github/workflows/test.yml`) includes:

1. **Backend Tests**

   - Lint (flake8)
   - Type checking (mypy)
   - Format check (black)
   - Unit/integration tests
   - Coverage reporting

2. **Frontend Tests**

   - Static analysis (flutter analyze)
   - Format check (dart format)
   - Unit/widget tests
   - Coverage reporting
   - Golden test validation

3. **Integration Tests**

   - End-to-end workflows
   - Cross-component integration

4. **Build Tests**

   - Backend syntax validation
   - Frontend APK build
   - Web build validation

5. **Security Scanning**
   - Dependency vulnerability checks
   - Secret scanning

### Branch Protection

Tests are required to pass before merging:

- All status checks must be green
- Coverage thresholds must be met
- No blocking security vulnerabilities

## Running Tests

### Local Development

**Quick Test Run:**

```bash
# From project root
make test-all

# Backend only
cd apps/backend && make test

# Frontend only
cd apps/frontend && make test
```

**With Coverage:**

```bash
# Backend
cd apps/backend && make test-cov

# Frontend
cd apps/frontend && make test-cov
```

**Watch Mode:**

```bash
# Backend
cd apps/backend && pytest-watch

# Frontend
cd apps/frontend && make test-watch
```

### CI/CD Environment

Tests run automatically on:

- Every push to `main`, `develop`, or `gitbutler/workspace`
- Every pull request
- Manual workflow dispatch

## Writing Tests

### Backend Test Guidelines

1. **Follow AAA Pattern**: Arrange, Act, Assert
2. **Use descriptive names**: `test_should_return_error_when_user_not_found`
3. **Mock external dependencies**: Use fixtures for Supabase, etc.
4. **Test both success and failure cases**
5. **Use async/await properly**

**Example:**

```python
@pytest.mark.asyncio
async def test_should_create_user_when_valid_data_provided(
    test_client: AsyncClient,
    sample_user_data: dict
):
    # Arrange
    user_data = sample_user_data

    # Act
    response = await test_client.post("/users/", json=user_data)

    # Assert
    assert response.status_code == 201
    assert response.json()["email"] == user_data["email"]
```

### Frontend Test Guidelines

1. **Test behavior, not implementation**
2. **Use semantic queries**: `find.text()` over `find.byKey()`
3. **Test accessibility**: Include semantic tests
4. **Mock external services**: Don't make real API calls
5. **Test responsive layouts**: Multiple screen sizes

**Example:**

```dart
testWidgets('should show error message when login fails', (tester) async {
  // Arrange
  final mockAuthService = MockAuthService();
  when(() => mockAuthService.signIn(any(), any()))
      .thenThrow(AuthException('Invalid credentials'));

  await WidgetTestHelpers.pumpWidgetWithGetX(
    tester,
    LoginScreen(),
    bindings: [TestBind(mockAuthService)],
  );

  // Act
  await tester.enterText(find.byKey(Key('email')), 'test@example.com');
  await tester.enterText(find.byKey(Key('password')), 'wrongpassword');
  await tester.tap(find.text('Sign In'));
  await tester.pumpAndSettle();

  // Assert
  expect(find.text('Invalid credentials'), findsOneWidget);
});
```

## Best Practices

### General

1. **Write tests first** (TDD when possible)
2. **Keep tests simple and focused**
3. **Use meaningful test data**
4. **Clean up after tests** (fixtures, mocks)
5. **Test edge cases and error conditions**
6. **Avoid test interdependencies**
7. **Use consistent naming conventions**

### Performance

1. **Use fixtures for expensive setup**
2. **Mock external services**
3. **Parallelize when possible**
4. **Cache dependencies in CI**
5. **Use test databases/isolated environments**

### Maintenance

1. **Keep tests up-to-date with code changes**
2. **Refactor tests when refactoring code**
3. **Remove obsolete tests**
4. **Document complex test scenarios**
5. **Review test coverage regularly**

### Anti-patterns to Avoid

❌ **Don't:**

- Test implementation details
- Write overly complex tests
- Ignore failing tests
- Skip edge cases
- Use production data in tests
- Write tests without assertions
- Test external libraries

✅ **Do:**

- Test public interfaces
- Keep tests simple and readable
- Fix or remove failing tests
- Test boundary conditions
- Use test-specific data
- Always include meaningful assertions
- Focus on your own code

---

For questions or issues with testing, please:

1. Check existing test examples
2. Review this documentation
3. Ask in team chat or create an issue
4. Update documentation when needed
