"""Global test configuration and fixtures.

This module provides pytest fixtures for database testing, authentication,
and common test utilities following clean architecture principles.
"""

# Test env must be set BEFORE the first ``app.*`` import, because
# ``app.core.config.settings = Settings()`` runs at module import time and
# validates that the active profile has a database URL.
import os

os.environ.setdefault("APP_PROFILE", "local")
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres",
)
# ``local`` profile is treated as "development" in Settings; bypass the
# Supabase-required branch by providing an empty URL/key (the validation
# gate is ``profile in {"dev", "test", "prod"}``).
os.environ.setdefault("SUPABASE_URL", "http://localhost:54321")
os.environ.setdefault("SUPABASE_ANON_KEY", "test-anon-key")
os.environ.setdefault("SUPABASE_JWT_SECRET", "test-jwt-secret")

import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from unittest.mock import Mock

import pytest
import pytest_asyncio
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


@pytest_asyncio.fixture
async def test_client(test_app) -> AsyncGenerator[AsyncClient, None]:
    """Create test client for the FastAPI app under test."""
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def test_app(mock_supabase):
    """Create a FastAPI app with Supabase clients stubbed via app.state.

    Replaces the production ``lifespan`` (which would try to talk to a real
    Supabase) with one that just sets ``app.state`` to a mock.
    """
    @asynccontextmanager
    async def _stub_lifespan(app):
        app.state.supabase_service = mock_supabase
        app.state.supabase_anon = mock_supabase
        yield

    app = create_app()
    app.router.lifespan_context = _stub_lifespan
    return app
