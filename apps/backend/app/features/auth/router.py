from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ...common.supabase_client import get_supabase
from ...core.config import settings

router = APIRouter()


class SignInRequest(BaseModel):
    email: str
    password: str


@router.post("/sign-in")
async def sign_in(payload: SignInRequest):
    sb = get_supabase()
    # Using supabase-py auth
    res = sb.auth.sign_in_with_password(
        {"email": payload.email, "password": payload.password}
    )
    if not res or not res.session:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {
        "access_token": res.session.access_token,
        "user": res.user.model_dump(),
    }


@router.get("/profile")
async def profile():
    # Placeholder - in real impl, decode JWT and fetch user profile
    return {"env": settings.env}
