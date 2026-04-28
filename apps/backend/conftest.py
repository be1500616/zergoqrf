"""Global test configuration and fixtures.

This module provides pytest fixtures for database testing, authentication,
and common test utilities following clean architecture principles.
"""

import uuid
from typing import AsyncGenerator
from unittest.mock import Mock, patch

import pytest
from app.main import create_app
from httpx import ASGITransport, AsyncClient

@pytest.fixture
def mock_supabase():
    """Mock Supabase client for testing."""
    mock_client = Mock()
    mock_auth = Mock()
    mock_client.auth = mock_auth

    # Mock successful signup
    mock_auth.sign_up.return_value = Mock(
        session=Mock(
            access_token="test_access_token",
            refresh_token="test_refresh_token",
            expires_in=3600,
        ),
        user=Mock(id=str(uuid.uuid4()), email="test@example.com", phone=None, user_metadata={"role": "customer"}),
    )

    # Mock successful signin
    mock_auth.sign_in_with_password.return_value = Mock(
        session=Mock(
            access_token="test_access_token",
            refresh_token="test_refresh_token",
            expires_in=3600,
        ),
        user=Mock(id=str(uuid.uuid4()), email="test@example.com", phone=None, user_metadata={"role": "customer"}),
    )

    # Mock get_user for token validation
    mock_auth.get_user.return_value = Mock(
        user=Mock(
            id=str(uuid.uuid4()),
            email="test@example.com",
            user_metadata={"role": "customer"},
            phone=None,
        )
    )
    
    # Mock table query
    mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
    mock_client.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = []

    return mock_client

@pytest.fixture(autouse=True)
def patch_supabase(mock_supabase):
    """Global patch for ALL Supabase client creation functions."""
    with patch("app.common.supabase_client.get_supabase", return_value=mock_supabase), \
         patch("app.common.supabase_client.get_supabase_anon", return_value=mock_supabase), \
         patch("app.common.supabase_client.create_client", return_value=mock_supabase), \
         patch("app.common.supabase_client.acreate_client", return_value=mock_supabase), \
         patch("supabase.create_client", return_value=mock_supabase), \
         patch("supabase.acreate_client", return_value=mock_supabase):
        
        # Clear lru_cache for Supabase client functions
        from app.common import supabase_client
        if hasattr(supabase_client.get_supabase, "cache_clear"):
            supabase_client.get_supabase.cache_clear()
        if hasattr(supabase_client.get_supabase_anon, "cache_clear"):
            supabase_client.get_supabase_anon.cache_clear()
            
        yield mock_supabase

@pytest.fixture
async def test_client() -> AsyncGenerator[AsyncClient, None]:
    """Create test client with dependency overrides.

    Returns a test client for making HTTP requests to the FastAPI app.
    """
    app = create_app()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
