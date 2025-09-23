import jwt
from fastapi import Header, HTTPException

from .core.config import settings


def get_current_tenant(x_tenant_id: str | None = Header(default=None)) -> str:
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="X-Tenant-Id header required")
    return x_tenant_id


def verify_supabase_jwt(authorization: str | None = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = authorization.split(" ", 1)[1]
    try:
        jwt.decode(
            token,
            settings.supabase_jwt_secret,  # type: ignore[arg-type]
            algorithms=["HS256"],
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    return token
