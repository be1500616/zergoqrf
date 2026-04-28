"""Restaurant domain entities.

This module contains the core business entities for the restaurant feature.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class Restaurant(BaseModel):
    """Restaurant entity representing a restaurant business."""
    
    id: UUID
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=6, max_length=8)
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    cuisine_type: Optional[str] = None
    dining_style: Optional[str] = None
    business_hours: Dict[str, Any] = Field(default_factory=dict)
    settings: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class RestaurantSettings(BaseModel):
    """Restaurant settings configuration."""
    
    # Branding
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    
    # Financial
    currency: str = "INR"
    tax_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    service_charge_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    
    # Operational
    service_model: str = Field(default="self_service")  # self_service, staff_assisted
    auto_accept_orders: bool = True
    estimated_prep_time: int = Field(default=30, ge=1)  # minutes
    
    # Notifications
    email_notifications: bool = True
    sms_notifications: bool = False
    whatsapp_notifications: bool = False
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class BusinessHours(BaseModel):
    """Business hours configuration."""
    
    monday: Optional[Dict[str, str]] = None
    tuesday: Optional[Dict[str, str]] = None
    wednesday: Optional[Dict[str, str]] = None
    thursday: Optional[Dict[str, str]] = None
    friday: Optional[Dict[str, str]] = None
    saturday: Optional[Dict[str, str]] = None
    sunday: Optional[Dict[str, str]] = None
    
    # Special dates
    holidays: list[str] = Field(default_factory=list)
    special_hours: Dict[str, Dict[str, str]] = Field(default_factory=dict)
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class RestaurantStaff(BaseModel):
    """Restaurant staff entity."""
    
    id: UUID
    restaurant_id: UUID
    user_id: UUID
    role: str = Field(..., pattern="^(owner|manager|kitchen|service)$")
    permissions: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
