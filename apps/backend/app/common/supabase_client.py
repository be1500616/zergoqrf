"""Supabase client factories and FastAPI dependencies.

Two factories (`make_supabase_service`, `make_supabase_anon`) create the
long-lived async clients, stored on ``app.state`` at startup. Two
FastAPI dependencies (`get_supabase`, `get_supabase_anon`) read those
clients off ``request.app.state`` so endpoints keep the familiar
``Depends(...)`` shape. ``user_supabase`` is a sync one-shot helper
for a user-scoped client (tokens rotate, not cached).
"""

from fastapi import Request
from supabase import AClient, acreate_client, create_client
from supabase import Client as SyncClient

from ..core.config import settings


async def make_supabase_service() -> AClient:
    """Async factory for the service-role client. Called once in lifespan."""
    key = settings.supabase_service_role_key or settings.supabase_anon_key or ""
    return await acreate_client(settings.supabase_url, key)


async def make_supabase_anon() -> AClient:
    """Async factory for the anon client. Called once in lifespan."""
    return await acreate_client(settings.supabase_url, settings.supabase_anon_key)


def get_supabase(request: Request) -> AClient:
    """FastAPI dependency returning the shared service-role client."""
    return request.app.state.supabase_service


def get_supabase_anon(request: Request) -> AClient:
    """FastAPI dependency returning the shared anon client."""
    return request.app.state.supabase_anon


def user_supabase(access_token: str) -> SyncClient:
    """Sync one-shot for a user-scoped client (tokens rotate, not cached)."""
    client = create_client(settings.supabase_url, settings.supabase_anon_key)
    client.auth.set_session(access_token, "")
    return client
