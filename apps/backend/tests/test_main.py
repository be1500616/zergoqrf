"""Tests for main FastAPI application.

This module contains tests for the main application endpoints and
configuration following clean architecture principles.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestHealthCheck:
    """Test cases for health check endpoint."""

    async def test_health_check_returns_ok_status(self, test_client: AsyncClient):
        """Test that health check endpoint returns OK status.

        Args:
            test_client: FastAPI test client fixture.
        """
        # Act
        response = await test_client.get("/healthz")

        # Assert
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    async def test_health_check_endpoint_is_accessible(self, test_client: AsyncClient):
        """Test that health check endpoint is accessible without auth.

        Args:
            test_client: FastAPI test client fixture.
        """
        # Act
        response = await test_client.get("/healthz")

        # Assert
        assert response.status_code == 200
        assert "status" in response.json()
