"""Authentication test data configurations.

Centralized authentication test data, credentials, and scenarios
for consistent testing across all auth-related test modules.
"""

import secrets
import string
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from tests.config.test_config import TEST_CONFIG


@dataclass
class UserCredentials:
    """Test user credentials."""
    email: str
    password: str
    name: str
    phone: Optional[str] = None
    role: str = "customer"
    restaurant_id: Optional[str] = None


@dataclass
class AuthTestCase:
    """Authentication test case configuration."""
    name: str
    description: str
    credentials: UserCredentials
    expected_status: int
    expected_response: Dict[str, Any] = field(default_factory=dict)
    should_succeed: bool = True
    cleanup_after_test: bool = True


class AuthTestDataGenerator:
    """Generates test data for authentication scenarios."""

    def __init__(self):
        self.config = TEST_CONFIG
        self.created_users: List[str] = []
        self.created_sessions: List[str] = []

    def generate_unique_email(self, prefix: str = "test") -> str:
        """Generate unique test email."""
        unique_id = secrets.token_hex(self.config.UNIQUE_ID_LENGTH // 2)
        return f"{prefix}_{unique_id}@{self.config.TEST_EMAIL_DOMAIN}"

    def generate_unique_phone(self, prefix: str = None) -> str:
        """Generate unique test phone number."""
        if prefix is None:
            prefix = self.config.TEST_PHONE_PREFIX
        unique_suffix = ''.join(secrets.choice(string.digits) for _ in range(4))
        return f"{prefix}{unique_suffix}"

    def generate_password(self, strength: str = "strong") -> str:
        """Generate test password with specified strength."""
        if strength == "strong":
            return self.config.TEST_EMAIL_PASSWORD
        elif strength == "weak":
            return "weak"
        elif strength == "invalid":
            return ""
        else:
            return "TestPassword123!"

    def generate_user_credentials(
        self,
        email: str = None,
        password: str = None,
        name: str = None,
        phone: str = None,
        role: str = "customer",
        restaurant_id: str = None
    ) -> UserCredentials:
        """Generate user credentials for testing."""
        unique_id = secrets.token_hex(4)

        return UserCredentials(
            email=email or f"test_{unique_id}@{self.config.TEST_EMAIL_DOMAIN}",
            password=password or self.config.TEST_EMAIL_PASSWORD,
            name=name or f"Test User {unique_id}",
            phone=phone or self.generate_unique_phone(),
            role=role,
            restaurant_id=restaurant_id
        )

    def get_customer_credentials(self) -> UserCredentials:
        """Get standard customer test credentials."""
        return UserCredentials(
            email="customer@test.com",
            password=self.config.TEST_EMAIL_PASSWORD,
            name="Test Customer",
            phone=self.config.TEST_PHONE_PREFIX + "1234",
            role="customer"
        )

    def get_manager_credentials(self) -> UserCredentials:
        """Get standard manager test credentials."""
        return UserCredentials(
            email="manager@test.com",
            password=self.config.TEST_EMAIL_PASSWORD,
            name="Test Manager",
            phone=self.config.TEST_PHONE_PREFIX + "5678",
            role="manager",
            restaurant_id="test-restaurant-id"
        )

    def get_service_staff_credentials(self) -> UserCredentials:
        """Get standard service staff test credentials."""
        return UserCredentials(
            email="staff@test.com",
            password=self.config.TEST_EMAIL_PASSWORD,
            name="Test Staff",
            phone=self.config.TEST_PHONE_PREFIX + "9012",
            role="service",
            restaurant_id="test-restaurant-id"
        )


class AuthTestScenarios:
    """Predefined authentication test scenarios."""

    def __init__(self):
        self.generator = AuthTestDataGenerator()

    def get_signup_scenarios(self) -> List[AuthTestCase]:
        """Get user signup test scenarios."""
        return [
            AuthTestCase(
                name="valid_customer_signup",
                description="Valid customer signup with email and password",
                credentials=self.generator.generate_user_credentials(role="customer"),
                expected_status=200,
                should_succeed=True
            ),
            AuthTestCase(
                name="valid_manager_signup",
                description="Valid manager signup with restaurant association",
                credentials=self.generator.generate_user_credentials(
                    role="manager",
                    restaurant_id="test-restaurant-id"
                ),
                expected_status=200,
                should_succeed=True
            ),
            AuthTestCase(
                name="invalid_email_format",
                description="Signup with invalid email format",
                credentials=self.generator.generate_user_credentials(email="invalid-email"),
                expected_status=422,
                should_succeed=False
            ),
            AuthTestCase(
                name="weak_password",
                description="Signup with weak password",
                credentials=self.generator.generate_user_credentials(password="weak"),
                expected_status=422,
                should_succeed=False
            ),
            AuthTestCase(
                name="missing_required_fields",
                description="Signup with missing required fields",
                credentials=UserCredentials(
                    email="",
                    password="",
                    name=""
                ),
                expected_status=422,
                should_succeed=False
            )
        ]

    def get_signin_scenarios(self) -> List[AuthTestCase]:
        """Get user signin test scenarios."""
        return [
            AuthTestCase(
                name="valid_customer_signin",
                description="Valid customer signin",
                credentials=self.generator.get_customer_credentials(),
                expected_status=200,
                should_succeed=True
            ),
            AuthTestCase(
                name="valid_manager_signin",
                description="Valid manager signin",
                credentials=self.generator.get_manager_credentials(),
                expected_status=200,
                should_succeed=True
            ),
            AuthTestCase(
                name="invalid_email",
                description="Signin with non-existent email",
                credentials=self.generator.generate_user_credentials(),
                expected_status=401,
                should_succeed=False
            ),
            AuthTestCase(
                name="invalid_password",
                description="Signin with wrong password",
                credentials=UserCredentials(
                    email="customer@test.com",
                    password="wrongpassword",
                    name="Test Customer"
                ),
                expected_status=401,
                should_succeed=False
            ),
            AuthTestCase(
                name="missing_credentials",
                description="Signin with missing credentials",
                credentials=UserCredentials(
                    email="",
                    password="",
                    name=""
                ),
                expected_status=422,
                should_succeed=False
            )
        ]

    def get_phone_auth_scenarios(self) -> List[AuthTestCase]:
        """Get phone authentication test scenarios."""
        return [
            AuthTestCase(
                name="valid_phone_otp_request",
                description="Valid phone OTP request",
                credentials=self.generator.generate_user_credentials(),
                expected_status=200,
                should_succeed=True
            ),
            AuthTestCase(
                name="invalid_phone_format",
                description="OTP request with invalid phone format",
                credentials=self.generator.generate_user_credentials(phone="invalid-phone"),
                expected_status=422,
                should_succeed=False
            ),
            AuthTestCase(
                name="valid_otp_verification",
                description="Valid OTP verification",
                credentials=self.generator.generate_user_credentials(),
                expected_status=200,
                should_succeed=True
            ),
            AuthTestCase(
                name="invalid_otp_code",
                description="OTP verification with invalid code",
                credentials=self.generator.generate_user_credentials(),
                expected_status=401,
                should_succeed=False
            )
        ]

    def get_token_management_scenarios(self) -> List[Dict[str, Any]]:
        """Get token management test scenarios."""
        return [
            {
                "name": "valid_token_refresh",
                "description": "Valid token refresh",
                "token_type": "refresh",
                "expected_status": 200,
                "should_succeed": True
            },
            {
                "name": "invalid_refresh_token",
                "description": "Invalid refresh token",
                "token_type": "invalid",
                "expected_status": 401,
                "should_succeed": False
            },
            {
                "name": "expired_refresh_token",
                "description": "Expired refresh token",
                "token_type": "expired",
                "expected_status": 401,
                "should_succeed": False
            }
        ]

    def get_anonymous_session_scenarios(self) -> List[Dict[str, Any]]:
        """Get anonymous session test scenarios."""
        return [
            {
                "name": "valid_anonymous_session",
                "description": "Valid anonymous session creation",
                "restaurant_id": "test-restaurant-id",
                "table_id": "test-table-id",
                "expected_status": 200,
                "should_succeed": True
            },
            {
                "name": "missing_restaurant_id",
                "description="Anonymous session without restaurant ID",
                "restaurant_id": "",
                "table_id": "test-table-id",
                "expected_status": 422,
                "should_succeed": False
            },
            {
                "name": "missing_table_id",
                "description="Anonymous session without table ID",
                "restaurant_id": "test-restaurant-id",
                "table_id": "",
                "expected_status": 422,
                "should_succeed": False
            }
        ]

    def get_security_test_scenarios(self) -> List[Dict[str, Any]]:
        """Get security test scenarios."""
        return [
            {
                "name": "sql_injection_attempt",
                "description": "SQL injection attempt in email field",
                "payload": {
                    "email": "'; DROP TABLE users; --",
                    "password": "password123"
                },
                "expected_status": 422,
                "should_succeed": False
            },
            {
                "name": "xss_attempt",
                "description": "XSS attempt in name field",
                "payload": {
                    "email": "test@test.com",
                    "password": "password123",
                    "name": "<script>alert('xss')</script>"
                },
                "expected_status": 422,
                "should_succeed": False
            },
            {
                "name": "brute_force_protection",
                "description": "Multiple failed login attempts",
                "payload": {
                    "email": "test@test.com",
                    "password": "wrongpassword"
                },
                "attempts": 10,
                "expected_status": 429,
                "should_succeed": False
            }
        ]


# Global test data instances
AUTH_TEST_GENERATOR = AuthTestDataGenerator()
AUTH_TEST_SCENARIOS = AuthTestScenarios()

# Quick access to common test credentials
TEST_CUSTOMER_CREDENTIALS = AUTH_TEST_GENERATOR.get_customer_credentials()
TEST_MANAGER_CREDENTIALS = AUTH_TEST_GENERATOR.get_manager_credentials()
TEST_SERVICE_STAFF_CREDENTIALS = AUTH_TEST_GENERATOR.get_service_staff_credentials()

# Test tokens (for mocking)
VALID_TEST_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0ZXN0LXVzZXItaWQiLCJlbWFpbCI6InRlc3RAZXhhbXBsZS5jb20iLCJyb2xlIjoiY3VzdG9tZXIifQ.test-signature"
INVALID_TEST_TOKEN = "invalid.jwt.token"
EXPIRED_TEST_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0ZXN0LXVzZXItaWQiLCJleHAiOjE2MDAwMDAwMDB9.expired-signature"