from functools import lru_cache
from typing import Optional

from supabase import Client, create_client, AClient, acreate_client

from ..core.config import settings


@lru_cache(maxsize=1)
def get_supabase() -> Client:
    """Get Supabase client with service role key for backend operations."""
    key = settings.supabase_service_role_key or settings.supabase_anon_key or ""
    return create_client(settings.supabase_url, key)


@lru_cache(maxsize=1)
def get_supabase_anon() -> Client:
    """Get Supabase client with anonymous key for public operations."""
    return create_client(settings.supabase_url, settings.supabase_anon_key)


def create_user_client(access_token: str) -> Client:
    """Create Supabase client with user's access token for RLS-enabled operations."""
    client = create_client(settings.supabase_url, settings.supabase_anon_key)
    client.auth.set_session(access_token, "")
    return client


def get_user_supabase_client(access_token: str) -> Client:
    """Get Supabase client configured with user's JWT token for RLS operations.

    This client should be used for operations that need to respect Row Level Security
    policies, as it includes the user's authentication context.

    Args:
        access_token: The user's JWT access token

    Returns:
        Supabase client configured with user authentication
    """
    return create_user_client(access_token)


# Async client functions for scalable concurrent operations
@lru_cache(maxsize=1)
async def get_async_supabase() -> AClient:
    """Get async Supabase client with service role key for backend operations.

    This client supports concurrent operations and should be used for
    high-throughput scenarios with multiple concurrent users.
    """
    key = settings.supabase_service_role_key or settings.supabase_anon_key or ""
    return await acreate_client(settings.supabase_url, key)


@lru_cache(maxsize=1)
async def get_async_supabase_anon() -> AClient:
    """Get async Supabase client with anonymous key for public operations."""
    return await acreate_client(settings.supabase_url, settings.supabase_anon_key)


async def create_async_user_client(access_token: str) -> AClient:
    """Create async Supabase client with user's access token for RLS-enabled operations."""
    client = await acreate_client(settings.supabase_url, settings.supabase_anon_key)
    await client.auth.set_session(access_token, "")
    return client


async def get_async_user_supabase_client(access_token: str) -> AClient:
    """Get async Supabase client configured with user's JWT token for RLS operations.

    This client should be used for operations that need to respect Row Level Security
    policies, as it includes the user's authentication context.

    Args:
        access_token: The user's JWT access token

    Returns:
        Async Supabase client configured with user authentication
    """
    return await create_async_user_client(access_token)
