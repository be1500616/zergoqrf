"""Restaurant Data Transfer Objects.

This module contains DTOs for transferring restaurant data between layers.
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr


class RestaurantCreateDTO(BaseModel):
    """DTO for creating a new restaurant."""
    
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[str] = None
    cuisine_type: Optional[str] = None
    dining_style: Optional[str] = None
    
    # Owner information
    owner_email: EmailStr
    owner_password: str = Field(..., min_length=8)
    owner_name: Optional[str] = None
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class RestaurantUpdateDTO(BaseModel):
    """DTO for updating restaurant information."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[str] = None
    cuisine_type: Optional[str] = None
    dining_style: Optional[str] = None
    business_hours: Optional[Dict[str, Any]] = None
    settings: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class RestaurantResponseDTO(BaseModel):
    """DTO for restaurant response data."""
    
    id: UUID
    name: str
    code: str
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    cuisine_type: Optional[str] = None
    dining_style: Optional[str] = None
    business_hours: Dict[str, Any] = Field(default_factory=dict)
    settings: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class BusinessHoursUpdateDTO(BaseModel):
    """DTO for updating business hours."""
    
    monday: Optional[Dict[str, str]] = None
    tuesday: Optional[Dict[str, str]] = None
    wednesday: Optional[Dict[str, str]] = None
    thursday: Optional[Dict[str, str]] = None
    friday: Optional[Dict[str, str]] = None
    saturday: Optional[Dict[str, str]] = None
    sunday: Optional[Dict[str, str]] = None
    holidays: Optional[List[str]] = None
    special_hours: Optional[Dict[str, Dict[str, str]]] = None
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class RestaurantSettingsUpdateDTO(BaseModel):
    """DTO for updating restaurant settings."""
    
    # Branding
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    
    # Financial
    currency: Optional[str] = None
    tax_rate: Optional[float] = Field(None, ge=0.0, le=1.0)
    service_charge_rate: Optional[float] = Field(None, ge=0.0, le=1.0)
    
    # Operational
    service_model: Optional[str] = None
    auto_accept_orders: Optional[bool] = None
    estimated_prep_time: Optional[int] = Field(None, ge=1)
    
    # Notifications
    email_notifications: Optional[bool] = None
    sms_notifications: Optional[bool] = None
    whatsapp_notifications: Optional[bool] = None
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class StaffCreateDTO(BaseModel):
    """DTO for creating a new staff member."""
    
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: Optional[str] = None
    role: str = Field(..., pattern="^(manager|kitchen|service)$")
    permissions: Optional[Dict[str, Any]] = None
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class StaffUpdateDTO(BaseModel):
    """DTO for updating staff member information."""
    
    role: Optional[str] = Field(None, pattern="^(owner|manager|kitchen|service)$")
    permissions: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class StaffResponseDTO(BaseModel):
    """DTO for staff response data."""
    
    id: UUID
    restaurant_id: UUID
    user_id: UUID
    role: str
    permissions: Dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    # User information (joined)
    email: Optional[str] = None
    name: Optional[str] = None
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class RestaurantRegistrationResponseDTO(BaseModel):
    """DTO for restaurant registration response."""
    
    restaurant: RestaurantResponseDTO
    owner: StaffResponseDTO
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
