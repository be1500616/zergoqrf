"""Restaurant Pydantic schemas for API requests and responses.

This module contains Pydantic models for restaurant API endpoints.
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr


class RestaurantCreateSchema(BaseModel):
    """Schema for restaurant creation request."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Restaurant name")
    description: Optional[str] = Field(None, description="Restaurant description")
    address: Optional[str] = Field(None, description="Restaurant address")
    phone: Optional[str] = Field(None, description="Restaurant phone number")
    email: Optional[EmailStr] = Field(None, description="Restaurant email")
    website: Optional[str] = Field(None, description="Restaurant website URL")
    cuisine_type: Optional[str] = Field(None, description="Type of cuisine")
    dining_style: Optional[str] = Field(None, description="Dining style (casual, fine_dining, etc.)")
    
    # Owner information
    owner_email: EmailStr = Field(..., description="Owner email address")
    owner_password: str = Field(..., min_length=8, description="Owner password")
    owner_name: Optional[str] = Field(None, description="Owner full name")


class RestaurantUpdateSchema(BaseModel):
    """Schema for restaurant update request."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[str] = None
    cuisine_type: Optional[str] = None
    dining_style: Optional[str] = None
    is_active: Optional[bool] = None


class BusinessHoursSchema(BaseModel):
    """Schema for business hours configuration."""
    
    monday: Optional[Dict[str, str]] = Field(None, description="Monday hours (open/close)")
    tuesday: Optional[Dict[str, str]] = Field(None, description="Tuesday hours")
    wednesday: Optional[Dict[str, str]] = Field(None, description="Wednesday hours")
    thursday: Optional[Dict[str, str]] = Field(None, description="Thursday hours")
    friday: Optional[Dict[str, str]] = Field(None, description="Friday hours")
    saturday: Optional[Dict[str, str]] = Field(None, description="Saturday hours")
    sunday: Optional[Dict[str, str]] = Field(None, description="Sunday hours")
    holidays: Optional[List[str]] = Field(None, description="Holiday dates (YYYY-MM-DD)")
    special_hours: Optional[Dict[str, Dict[str, str]]] = Field(None, description="Special date hours")


class RestaurantSettingsSchema(BaseModel):
    """Schema for restaurant settings configuration."""
    
    # Branding
    logo_url: Optional[str] = Field(None, description="Logo image URL")
    primary_color: Optional[str] = Field(None, description="Primary brand color (hex)")
    secondary_color: Optional[str] = Field(None, description="Secondary brand color (hex)")
    
    # Financial
    currency: Optional[str] = Field(None, description="Currency code (INR, USD, etc.)")
    tax_rate: Optional[float] = Field(None, ge=0.0, le=1.0, description="Tax rate (0.0-1.0)")
    service_charge_rate: Optional[float] = Field(None, ge=0.0, le=1.0, description="Service charge rate")
    
    # Operational
    service_model: Optional[str] = Field(None, description="Service model (self_service, staff_assisted)")
    auto_accept_orders: Optional[bool] = Field(None, description="Auto-accept orders")
    estimated_prep_time: Optional[int] = Field(None, ge=1, description="Estimated prep time in minutes")
    
    # Notifications
    email_notifications: Optional[bool] = Field(None, description="Enable email notifications")
    sms_notifications: Optional[bool] = Field(None, description="Enable SMS notifications")
    whatsapp_notifications: Optional[bool] = Field(None, description="Enable WhatsApp notifications")


class RestaurantResponseSchema(BaseModel):
    """Schema for restaurant response."""
    
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


class StaffCreateSchema(BaseModel):
    """Schema for creating a new staff member."""
    
    email: EmailStr = Field(..., description="Staff email address")
    password: str = Field(..., min_length=8, description="Staff password")
    name: Optional[str] = Field(None, description="Staff full name")
    role: str = Field(..., pattern="^(manager|kitchen|service)$", description="Staff role")
    permissions: Optional[Dict[str, Any]] = Field(None, description="Custom permissions")


class StaffUpdateSchema(BaseModel):
    """Schema for updating staff member."""
    
    role: Optional[str] = Field(None, pattern="^(owner|manager|kitchen|service)$")
    permissions: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class StaffResponseSchema(BaseModel):
    """Schema for staff response."""
    
    id: UUID
    restaurant_id: UUID
    user_id: UUID
    role: str
    permissions: Dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    # User information (if available)
    email: Optional[str] = None
    name: Optional[str] = None

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class RestaurantRegistrationResponseSchema(BaseModel):
    """Schema for restaurant registration response."""
    
    restaurant: RestaurantResponseSchema
    owner: StaffResponseSchema
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class RestaurantListResponseSchema(BaseModel):
    """Schema for restaurant list response."""
    
    restaurants: List[RestaurantResponseSchema]
    total: int
    page: int
    per_page: int

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class StaffListResponseSchema(BaseModel):
    """Schema for staff list response."""
    
    staff: List[StaffResponseSchema]
    total: int

    class Config:
        """Pydantic configuration."""
        from_attributes = True
