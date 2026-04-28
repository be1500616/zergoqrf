# Authentication Testing Guide

This guide provides comprehensive instructions for testing authentication functionality in your ZERGO backend application.

## Overview

The authentication testing system is organized into several layers:

1. **Test Configuration** (`tests/config/`) - Centralized settings and test data
2. **Test Factories** (`tests/factories/`) - Data generation utilities
3. **Test Helpers** (`tests/utils/`) - Reusable testing utilities
4. **Test Files** - Actual test implementations

## Running Tests

### Unit Tests (No external dependencies)

```bash
# Run all unit tests
pytest tests/ -m unit

# Run specific auth unit tests
pytest tests/features/auth/ -m unit

# Run with coverage
pytest tests/ -m unit --cov=app --cov-report=html
```

### Integration Tests (With real Supabase)

```bash
# Set environment for integration tests
export TEST_ENV=integration
export SUPABASE_URL=your_supabase_url
export SUPABASE_ANON_KEY=your_supabase_anon_key
export SUPABASE_SERVICE_ROLE_KEY=your_service_role_key  # Optional, for cleanup

# Run integration tests
pytest tests/integration/ -m integration

# Run specific integration tests
pytest tests/integration/test_real_supabase_auth.py -v
```

### All Tests

```bash
# Run all tests with proper environment setup
export TEST_ENV=integration  # or 'unit' for unit tests only
pytest tests/ -v
```

## Test Configuration

### Environment Variables

```bash
# Test Environment
TEST_ENV=unit|integration|staging|production

# Database
TEST_DATABASE_URL=sqlite+aiosqlite:///./test.db

# Supabase (for integration tests)
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# Test Configuration
TEST_AUTO_CLEANUP=true
TEST_LOG_LEVEL=WARNING
TEST_JWT_SECRET=your-test-jwt-secret
```

### Configuration Files

The test configuration is centralized in `tests/config/test_config.py`:

- **Database settings**: SQLite for unit tests, configurable for integration
- **Authentication settings**: Token expiry, password requirements
- **Rate limiting**: Test rate limits
- **Performance settings**: Load test configurations

## Test Data Management

### Centralized Test Data

All test data is managed through centralized configuration:

```python
from tests.config.auth_test_data import AUTH_TEST_GENERATOR, AUTH_TEST_SCENARIOS

# Generate test credentials
credentials = AUTH_TEST_GENERATOR.generate_user_credentials(role="customer")

# Get predefined test scenarios
scenarios = AUTH_TEST_SCENARIOS.get_signup_scenarios()
```

### User Factory

The user factory creates realistic test users:

```python
from tests.factories.user_factory import USER_FACTORY

# Create customer
customer = USER_FACTORY.create_customer()

# Create manager with restaurant
manager = USER_FACTORY.create_manager(restaurant_id="rest-123")

# Create batch users
users = USER_FACTORY.create_batch_users(count=10, role="customer")
```

## Test Patterns

### 1. Basic Authentication Test

```python
import pytest
from tests.utils.auth_helpers import AuthTestHelper

@pytest.mark.asyncio
async def test_customer_signup_signin(client: AsyncClient, auth_helper: AuthTestHelper):
    # Create credentials
    credentials = AUTH_TEST_GENERATOR.generate_user_credentials(role="customer")

    # Test signup
    signup_response = await auth_helper.signup_user(credentials)
    assert signup_response.get("error") is None
    auth_helper.assert_auth_response(signup_response)

    # Test signin
    signin_response = await auth_helper.signin_user(credentials.email, credentials.password)
    assert signin_response.get("error") is None

    # Verify user data
    assert signin_response["user"]["email"] == credentials.email
    assert signin_response["user"]["role"] == "customer"
```

### 2. Error Scenario Test

```python
@pytest.mark.asyncio
async def test_invalid_credentials(auth_helper: AuthTestHelper):
    # Test signin with invalid credentials
    response = await auth_helper.signin_user("nonexistent@test.com", "wrongpassword")

    assert response.get("error") is not None
    auth_helper.assert_error_response(response)
```

### 3. Multi-tenant Test

```python
@pytest.mark.asyncio
async def test_restaurant_manager_access(auth_helper: AuthTestHelper):
    # Create manager for specific restaurant
    credentials = AUTH_TEST_GENERATOR.generate_user_credentials(
        role="manager",
        restaurant_id="restaurant-123"
    )

    # Test signup
    response = await auth_helper.signup_user(credentials)
    assert response.get("error") is None

    # Verify restaurant association
    assert response["user"]["restaurant_id"] == "restaurant-123"
    assert response["user"]["role"] == "manager"
```

## Real Supabase Testing

### Prerequisites

1. **Supabase Project**: Have a Supabase project ready
2. **Environment Setup**: Configure environment variables
3. **Database Schema**: Ensure your database schema matches the application

### Setup

```bash
# Create a test environment file
cp .env.example .env.test

# Edit .env.test with your test credentials
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-key  # For cleanup
```

### Running Integration Tests

```bash
# Set test environment
export TEST_ENV=integration
source .env.test

# Run integration tests
pytest tests/integration/test_real_supabase_auth.py -v -s
```

### Test Cleanup

Integration tests automatically cleanup created resources:

- **Users**: Deleted from auth.users and users table
- **Restaurants**: Deleted from restaurants table
- **Sessions**: Invalidated and removed

## Test Scenarios Coverage

### ✅ Currently Covered

1. **Email Authentication**
   - Customer signup/signin
   - Manager signup/signin with restaurant association
   - Invalid credentials handling
   - Email format validation

2. **Phone Authentication**
   - OTP request initiation
   - OTP verification structure
   - Phone format validation

3. **Token Management**
   - JWT token generation
   - Token refresh
   - Token validation
   - Expired token handling

4. **Anonymous Sessions**
   - QR code session creation
   - Restaurant and table association
   - Session validation

5. **Security**
   - SQL injection prevention
   - XSS protection
   - Token tampering detection
   - Rate limiting structure

### 🔄 Missing Scenarios (To be implemented)

1. **Advanced Security**
   - Brute force protection
   - Account lockout
   - Device fingerprinting
   - Suspicious activity detection

2. **Session Management**
   - Multiple device sessions
   - Session cleanup
   - Concurrent session limits

3. **Password Management**
   - Password reset flow
   - Password strength validation
   - Password history

4. **Email Verification**
   - Email confirmation flow
   - Verification token handling
   - Resend verification

5. **Performance Testing**
   - Load testing for authentication
   - Concurrent user handling
   - Database performance

## Best Practices

### 1. Test Organization

- **Use centralized configuration**: Never hardcode test data
- **Follow naming conventions**: Use descriptive test names
- **Group related tests**: Use pytest markers
- **Clean up resources**: Always cleanup created data

### 2. Test Data

- **Use factories**: Generate realistic test data
- **Make it unique**: Avoid conflicts between tests
- **Use consistent formats**: Follow real-world patterns
- **Document assumptions**: Comment test data requirements

### 3. Error Handling

- **Test failure scenarios**: Don't just test happy paths
- **Validate error messages**: Ensure proper error responses
- **Test edge cases**: Boundary conditions and invalid inputs
- **Handle timeouts**: Account for network delays

### 4. Integration Testing

- **Use real services**: Test with actual Supabase when possible
- **Isolate test data**: Use separate test environment
- **Handle cleanup**: Remove test data after tests
- **Document requirements**: Clearly state integration test prerequisites

## Troubleshooting

### Common Issues

1. **Supabase Connection Failed**
   ```bash
   # Check environment variables
   echo $SUPABASE_URL
   echo $SUPABASE_ANON_KEY

   # Test connection manually
   curl -H "apikey: $SUPABASE_ANON_KEY" "$SUPABASE_URL/rest/v1/"
   ```

2. **Test Data Conflicts**
   ```bash
   # Clear test database
   rm -f test.db

   # Run with fresh database
   pytest tests/ --create-db
   ```

3. **Permission Errors**
   ```bash
   # Check RLS policies
   # Ensure test user has proper permissions

   # Use service role key for admin operations
   export SUPABASE_SERVICE_ROLE_KEY=your-key
   ```

4. **Token Validation Failures**
   ```bash
   # Check JWT secret
   echo $TEST_JWT_SECRET

   # Verify token format
   # Ensure proper JWT signing
   ```

### Debug Mode

Enable debug logging for troubleshooting:

```bash
export TEST_LOG_LEVEL=DEBUG
export TEST_ENABLE_SQL_LOGGING=true

pytest tests/ -v -s --log-cli-level=DEBUG
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Auth Tests
on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: |
          pip install -e .[dev]

      - name: Run unit tests
        run: |
          pytest tests/ -m unit --cov=app

      - name: Upload coverage
        uses: codecov/codecov-action@v1

  integration-tests:
    runs-on: ubuntu-latest
    needs: unit-tests
    if: github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: |
          pip install -e .[dev]

      - name: Run integration tests
        env:
          TEST_ENV: integration
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_ANON_KEY: ${{ secrets.SUPABASE_ANON_KEY }}
          SUPABASE_SERVICE_ROLE_KEY: ${{ secrets.SUPABASE_SERVICE_KEY }}
        run: |
          pytest tests/integration/ -m integration
```

## Contributing

When adding new authentication tests:

1. **Update test data**: Add new scenarios to `AUTH_TEST_SCENARIOS`
2. **Use helpers**: Leverage existing `AuthTestHelper` methods
3. **Add cleanup**: Ensure proper resource cleanup
4. **Document**: Add clear test descriptions and comments
5. **Test coverage**: Maintain high test coverage (>90%)

This testing framework ensures your authentication system remains robust and secure as your application evolves.