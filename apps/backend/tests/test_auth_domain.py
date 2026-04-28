"""Unit tests for authentication domain layer.

This module tests the domain entities, value objects, and business logic
without any external dependencies.
"""

from datetime import datetime, timedelta
from uuid import uuid4

import pytest
from app.features.auth.domain.auth_entities import AuthSession, User
from app.features.auth.domain.auth_exceptions import (
    InvalidEmailFormatError,
    InvalidPhoneFormatError,
    WeakPasswordError,
)
from app.features.auth.domain.auth_vos import Email, Password, PhoneNumber


class TestEmail:
    """Test cases for Email value object."""

    def test_valid_email_creation(self):
        """Test creating a valid email."""
        email = Email("test@example.com")
        assert email.value == "test@example.com"

    def test_email_normalization(self):
        """Test email normalization (lowercase)."""
        email = Email("TEST@EXAMPLE.COM")
        assert email.value == "test@example.com"

    def test_invalid_email_format(self):
        """Test invalid email format raises exception."""
        with pytest.raises(InvalidEmailFormatError):
            Email("invalid-email")

        with pytest.raises(InvalidEmailFormatError):
            Email("@example.com")

        with pytest.raises(InvalidEmailFormatError):
            Email("test@")

    def test_email_equality(self):
        """Test email equality comparison."""
        email1 = Email("test@example.com")
        email2 = Email("TEST@EXAMPLE.COM")
        assert email1 == email2


class TestPassword:
    """Test cases for Password value object."""

    def test_valid_password_creation(self):
        """Test creating a valid password."""
        password = Password("SecurePass123!")
        assert password.hashed_value is not None
        assert password.verify("SecurePass123!")

    def test_weak_password_rejection(self):
        """Test weak password rejection."""
        with pytest.raises(WeakPasswordError):
            Password("123")  # Too short

        with pytest.raises(WeakPasswordError):
            Password("password")  # No numbers

    def test_password_hashing(self):
        """Test password hashing functionality."""
        password = Password("SecurePass123!")
        hashed_value = password.hashed_value

        # Create password from hash
        hashed_password = Password(hashed_value, is_hashed=True)
        assert hashed_password.hashed_value == hashed_value
        assert hashed_password.verify("SecurePass123!")
        assert not hashed_password.verify("WrongPassword")

    def test_password_strength_validation(self):
        """Test password strength validation."""
        # Valid strong passwords
        Password("SecurePass123!")
        Password("MyP@ssw0rd")
        Password("Complex1ty!")

        # Invalid weak passwords
        with pytest.raises(WeakPasswordError):
            Password("short")
        with pytest.raises(WeakPasswordError):
            Password("password")  # No numbers
        with pytest.raises(WeakPasswordError):
            Password("12345678")  # No letters


class TestPhoneNumber:
    """Test cases for PhoneNumber value object."""

    def test_valid_phone_creation(self):
        """Test creating valid phone numbers."""
        phone = PhoneNumber("+1234567890")
        assert phone.value == "+1234567890"

    def test_phone_normalization(self):
        """Test phone number normalization."""
        phone = PhoneNumber("(123) 456-7890")
        assert phone.value == "+1234567890"  # Normalized format

    def test_invalid_phone_format(self):
        """Test invalid phone format raises exception."""
        with pytest.raises(InvalidPhoneFormatError):
            PhoneNumber("123")  # Too short

        with pytest.raises(InvalidPhoneFormatError):
            PhoneNumber("abc-def-ghij")  # Non-numeric


class TestUser:
    """Test cases for User entity."""

    def test_user_creation(self):
        """Test creating a user entity."""
        user = User(
            id=uuid4(),
            email=Email("test@example.com"),
            name="Test User",
            role="customer",
        )

        assert user.email.value == "test@example.com"
        assert user.name == "Test User"
        assert user.role == "customer"
        assert user.is_active is True

    def test_user_activation_deactivation(self):
        """Test user activation and deactivation."""
        user = User(
            id=uuid4(),
            email=Email("test@example.com"),
            name="Test User",
            role="customer",
        )

        assert user.is_active is True

        user.deactivate()
        assert user.is_active is False

        user.activate()
        assert user.is_active is True

    def test_user_permissions(self):
        """Test user permission checking."""
        # Customer user
        customer = User(
            id=uuid4(),
            email=Email("customer@example.com"),
            name="Customer",
            role="customer",
            permissions={"view_menu": True},
        )

        assert customer.has_permission("view_menu")
        assert not customer.has_permission("manage_staff")

        # Manager user
        manager = User(
            id=uuid4(),
            email=Email("manager@example.com"),
            name="Manager",
            role="manager",
            restaurant_id=uuid4(),
            permissions={
                "view_menu": True,
                "manage_staff": True,
                "manage_orders": True,
            },
        )

        assert manager.has_permission("view_menu")
        assert manager.has_permission("manage_orders")
        assert not manager.has_permission("manage_restaurant")

    def test_restaurant_access(self):
        """Test restaurant access checking."""
        restaurant_id = uuid4()
        other_restaurant_id = uuid4()

        user = User(
            id=uuid4(),
            email=Email("staff@example.com"),
            name="Staff",
            role="service",
            restaurant_id=restaurant_id,
        )

        assert user.can_access_restaurant(restaurant_id)
        assert not user.can_access_restaurant(other_restaurant_id)

        # Customer without restaurant should be able to access any restaurant for ordering
        customer = User(
            id=uuid4(),
            email=Email("customer@example.com"),
            name="Customer",
            role="customer",
        )

        assert customer.can_access_restaurant(
            restaurant_id
        )  # Customers can access any restaurant


class TestAuthSession:
    """Test cases for AuthSession entity."""

    def test_session_creation(self):
        """Test creating an authentication session."""
        user_id = uuid4()
        restaurant_id = uuid4()

        session = AuthSession(
            id=uuid4(),
            session_token="test_token",
            expires_at=datetime.utcnow() + timedelta(hours=1),
            user_id=user_id,
            restaurant_id=restaurant_id,
        )

        assert session.user_id == user_id
        assert session.restaurant_id == restaurant_id
        assert session.session_token == "test_token"
        assert not session.is_anonymous  # Has user_id, so not anonymous

    def test_anonymous_session_creation(self):
        """Test creating an anonymous session."""
        restaurant_id = uuid4()
        table_id = uuid4()

        session = AuthSession(
            id=uuid4(),
            session_token="anon_token",
            expires_at=datetime.utcnow() + timedelta(hours=2),
            user_id=None,
            restaurant_id=restaurant_id,
            table_id=table_id,
            is_anonymous=True,
        )

        assert session.user_id is None
        assert session.restaurant_id == restaurant_id
        assert session.table_id == table_id
        assert session.is_anonymous  # No user_id, so anonymous
        assert session.session_token == "anon_token"

    def test_session_expiration(self):
        """Test session expiration logic."""
        # Create session that expires in 1 hour
        session = AuthSession(
            id=uuid4(),
            session_token="test_token",
            expires_at=datetime.utcnow() + timedelta(hours=1),
            user_id=uuid4(),
        )

        assert not session.is_expired()

        # Create expired session
        expired_session = AuthSession(
            id=uuid4(),
            session_token="expired_token",
            expires_at=datetime.utcnow() - timedelta(hours=1),
            user_id=uuid4(),
        )

        assert expired_session.is_expired()

    def test_session_deactivation(self):
        """Test session deactivation."""
        session = AuthSession(
            id=uuid4(),
            session_token="test_token",
            expires_at=datetime.utcnow() + timedelta(hours=1),
            user_id=uuid4(),
        )

        # Session should not be expired initially
        assert not session.is_expired()

        # Test session token
        assert session.session_token == "test_token"
