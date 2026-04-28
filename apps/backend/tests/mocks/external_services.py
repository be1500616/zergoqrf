"""Mocks for external services.

This module provides mock implementations for external services
like Supabase, following clean architecture testing principles.
"""

import uuid
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock


class MockSupabaseClient:
    """Mock implementation of Supabase client."""

    def __init__(self):
        """Initialize mock Supabase client with common methods."""
        self.auth = MockSupabaseAuth()
        self.table_data: Dict[str, List[Dict[str, Any]]] = {}
        self._setup_tables()

    def _setup_tables(self) -> None:
        """Setup mock table data."""
        self.table_data = {
            "users": [],
            "restaurants": [],
            "orders": [],
            "menu_items": [],
        }

    def table(self, table_name: str) -> "MockSupabaseTable":
        """Get mock table instance.

        Args:
            table_name: Name of the table.

        Returns:
            MockSupabaseTable: Mock table instance.
        """
        return MockSupabaseTable(table_name, self.table_data)


class MockSupabaseAuth:
    """Mock Supabase authentication service."""

    def __init__(self):
        """Initialize mock auth service."""
        self.users: List[Dict[str, Any]] = []

    async def sign_up(self, email: str, password: str, **kwargs) -> Dict[str, Any]:
        """Mock user sign up.

        Args:
            email: User email.
            password: User password.
            **kwargs: Additional signup data.

        Returns:
            dict: Mock signup response.
        """
        user_id = str(uuid.uuid4())
        user_data = {
            "id": user_id,
            "email": email,
            "created_at": "2024-01-01T00:00:00Z",
            **kwargs,
        }
        self.users.append(user_data)

        return {
            "user": user_data,
            "session": {
                "access_token": f"mock_token_{user_id}",
                "refresh_token": f"mock_refresh_{user_id}",
            },
        }

    async def sign_in_with_password(self, email: str, password: str) -> Dict[str, Any]:
        """Mock user sign in.

        Args:
            email: User email.
            password: User password.

        Returns:
            dict: Mock signin response.
        """
        user = next((u for u in self.users if u["email"] == email), None)

        if not user:
            return {"user": None, "session": None, "error": "Invalid credentials"}

        return {
            "user": user,
            "session": {
                "access_token": f"mock_token_{user['id']}",
                "refresh_token": f"mock_refresh_{user['id']}",
            },
        }

    async def get_user(self, token: str) -> Dict[str, Any]:
        """Mock get current user.

        Args:
            token: Access token.

        Returns:
            dict: Mock user response.
        """
        # Extract user_id from mock token
        if not token.startswith("mock_token_"):
            return {"user": None, "error": "Invalid token"}

        user_id = token.replace("mock_token_", "")
        user = next((u for u in self.users if u["id"] == user_id), None)

        if not user:
            return {"user": None, "error": "User not found"}

        return {"user": user}


class MockSupabaseTable:
    """Mock Supabase table operations."""

    def __init__(self, table_name: str, table_data: Dict[str, List]):
        """Initialize mock table.

        Args:
            table_name: Name of the table.
            table_data: Reference to shared table data.
        """
        self.table_name = table_name
        self.table_data = table_data
        self._query_filters: List[Dict[str, Any]] = []

    def select(self, columns: str = "*") -> "MockSupabaseTable":
        """Mock select operation.

        Args:
            columns: Columns to select.

        Returns:
            MockSupabaseTable: Self for chaining.
        """
        return self

    def eq(self, column: str, value: Any) -> "MockSupabaseTable":
        """Mock equality filter.

        Args:
            column: Column name.
            value: Value to match.

        Returns:
            MockSupabaseTable: Self for chaining.
        """
        self._query_filters.append({"type": "eq", "column": column, "value": value})
        return self

    async def execute(self) -> Dict[str, Any]:
        """Execute mock query.

        Returns:
            dict: Mock query result.
        """
        data = self.table_data.get(self.table_name, [])

        # Apply filters
        for filter_item in self._query_filters:
            if filter_item["type"] == "eq":
                data = [
                    item
                    for item in data
                    if item.get(filter_item["column"]) == filter_item["value"]
                ]

        # Clear filters for next query
        self._query_filters = []

        return {"data": data, "error": None}

    async def insert(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock insert operation.

        Args:
            data: Data to insert.

        Returns:
            dict: Mock insert result.
        """
        # Add ID if not provided
        if "id" not in data:
            data["id"] = str(uuid.uuid4())

        # Add timestamps
        data["created_at"] = "2024-01-01T00:00:00Z"
        data["updated_at"] = "2024-01-01T00:00:00Z"

        self.table_data[self.table_name].append(data)

        return {"data": [data], "error": None}

    async def update(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock update operation.

        Args:
            data: Data to update.

        Returns:
            dict: Mock update result.
        """
        table_data = self.table_data.get(self.table_name, [])
        updated_items = []

        for item in table_data:
            # Apply filters to find matching items
            matches = True
            for filter_item in self._query_filters:
                if filter_item["type"] == "eq":
                    if item.get(filter_item["column"]) != filter_item["value"]:
                        matches = False
                        break

            if matches:
                item.update(data)
                item["updated_at"] = "2024-01-01T00:00:00Z"
                updated_items.append(item)

        # Clear filters for next query
        self._query_filters = []

        return {"data": updated_items, "error": None}


def create_mock_supabase_client() -> MockSupabaseClient:
    """Create a mock Supabase client instance.

    Returns:
        MockSupabaseClient: Mock client instance.
    """
    return MockSupabaseClient()
