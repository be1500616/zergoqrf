from functools import lru_cache

from supabase import Client, create_client

from ..core.config import settings


@lru_cache(maxsize=1)
def get_supabase() -> Client:
    key = settings.supabase_service_role_key or settings.supabase_anon_key or ""
    return create_client(settings.supabase_url, key)
