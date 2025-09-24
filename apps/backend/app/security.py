from fastapi import Depends, Header, HTTPException
from supabase import Client

from apps.backend.app.common.supabase_client import get_supabase


def get_current_tenant(x_tenant_id: str | None = Header(default=None)) -> str:
    if not x_tenant_id:
        raise HTTPException(
            status_code=400, detail="X-Tenant-Id header required"
        )
    return x_tenant_id


def verify_supabase_jwt(
    authorization: str | None = Header(default=None),
    supabase: Client = Depends(get_supabase),
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = authorization.split(" ", 1)[1]
    try:
        # Use Supabase client to verify the token
        user_response = supabase.auth.get_user(token)
        if user_response.user is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_response.user
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")
