"""Test utilities and helper functions.

This module provides common utilities for testing following
the Arrange-Act-Assert (AAA) pattern.
"""

from typing import Any, Dict
from unittest.mock import MagicMock


def assert_response_structure(
    response_data: Dict[str, Any], expected_fields: list[str]
) -> None:
    """Assert that response contains expected fields.

    Args:
        response_data: The response data to check.
        expected_fields: List of expected field names.

    Raises:
        AssertionError: If any expected field is missing.
    """
    for field in expected_fields:
        assert field in response_data, f"Missing field: {field}"


def create_mock_supabase_response(
    data: Dict[str, Any] = None, error: str = None
) -> MagicMock:
    """Create a mock Supabase response.

    Args:
        data: The data to return in the response.
        error: Error message if the response should simulate an error.

    Returns:
        MagicMock: Mocked Supabase response.
    """
    mock_response = MagicMock()
    mock_response.data = data or []
    mock_response.error = error
    return mock_response


def create_test_user(
    email: str = "test@example.com", user_id: str = "test-user-id"
) -> Dict[str, Any]:
    """Create test user data.

    Args:
        email: User email address.
        user_id: User ID.

    Returns:
        dict: Test user data.
    """
    return {
        "id": user_id,
        "email": email,
        "phone": "+1234567890",
        "is_active": True,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }


def create_test_restaurant(
    name: str = "Test Restaurant", restaurant_id: str = "test-restaurant-id"
) -> Dict[str, Any]:
    """Create test restaurant data.

    Args:
        name: Restaurant name.
        restaurant_id: Restaurant ID.

    Returns:
        dict: Test restaurant data.
    """
    return {
        "id": restaurant_id,
        "name": name,
        "address": "123 Test St, Test City, TC 12345",
        "phone": "+1234567890",
        "email": "restaurant@test.com",
        "is_active": True,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }
