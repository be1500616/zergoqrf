import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, EmailStr, Field


class SignUpSchema(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    restaurant_id: Optional[uuid.UUID] = None
    role: Optional[str] = Field(
        None, pattern="^(owner|manager|kitchen|service|customer)$"
    )


class SignInSchema(BaseModel):
    email: EmailStr
    password: str


class PhoneSignInSchema(BaseModel):
    phone: str = Field(..., pattern="^\\+?[1-9]\\d{1,14}$")


class VerifyOTPSchema(BaseModel):
    phone: str = Field(..., pattern="^\\+?[1-9]\\d{1,14}$")
    otp: str = Field(..., min_length=6, max_length=6)
    name: Optional[str] = None


class AnonymousSessionSchema(BaseModel):
    restaurant_id: uuid.UUID
    table_id: uuid.UUID


class RefreshTokenSchema(BaseModel):
    refresh_token: str


class UserInfo(BaseModel):
    id: str
    email: Optional[str] = None
    phone: Optional[str] = None
    name: Optional[str] = None
    role: str
    restaurant_id: Optional[str] = None


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: Optional[int] = None
    user: Optional[UserInfo] = None


class AnonymousSessionResponse(BaseModel):
    session_id: uuid.UUID
    session_token: str
    expires_at: datetime
    restaurant_id: uuid.UUID
    table_id: uuid.UUID


class UserProfileResponse(BaseModel):
    id: uuid.UUID
    email: Optional[str] = None
    phone: Optional[str] = None
    name: Optional[str] = None
    role: str
    restaurant_id: Optional[uuid.UUID] = None
    permissions: Dict[str, Any] = {}
    is_active: bool = True
