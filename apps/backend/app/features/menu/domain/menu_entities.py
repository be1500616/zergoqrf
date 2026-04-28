"""Menu domain entities.

This module contains the core business entities for the menu management feature.
"""

from datetime import datetime, time
from typing import Dict, Any, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field
from enum import Enum


class MenuStatus(str, Enum):
    """Menu status enumeration."""
    DRAFT = "draft"
    LIVE = "live"
    SCHEDULED = "scheduled"
    ARCHIVED = "archived"


class ItemStatus(str, Enum):
    """Menu item status enumeration."""
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    SEASONAL = "seasonal"
    FEATURED = "featured"


class DietaryIndicator(str, Enum):
    """Dietary indicator enumeration."""
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    GLUTEN_FREE = "gluten_free"
    KETO = "keto"
    SPICY = "spicy"
    HALAL = "halal"
    KOSHER = "kosher"


class ModifierType(str, Enum):
    """Modifier type enumeration."""
    SINGLE_SELECT = "single_select"
    MULTI_SELECT = "multi_select"
    QUANTITY = "quantity"


class MenuCategory(BaseModel):
    """Menu category entity representing a category or subcategory."""
    
    id: UUID
    restaurant_id: UUID
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    parent_category_id: Optional[UUID] = None
    sort_order: int = Field(default=0)
    is_active: bool = True
    availability_schedule: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class MenuItemVariant(BaseModel):
    """Menu item variant for different sizes/options."""
    
    id: UUID
    menu_item_id: UUID
    name: str = Field(..., min_length=1, max_length=50)  # Small, Medium, Large
    description: Optional[str] = None
    price_adjustment: float = Field(default=0.0)  # Price difference from base
    sort_order: int = Field(default=0)
    is_active: bool = True

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class MenuItemModifier(BaseModel):
    """Menu item modifier/add-on."""
    
    id: UUID
    modifier_group_id: UUID
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    price: float = Field(default=0.0, ge=0.0)
    sort_order: int = Field(default=0)
    is_active: bool = True

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class MenuItemModifierGroup(BaseModel):
    """Menu item modifier group."""
    
    id: UUID
    menu_item_id: UUID
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    modifier_type: ModifierType = ModifierType.SINGLE_SELECT
    is_required: bool = False
    min_selections: int = Field(default=0, ge=0)
    max_selections: Optional[int] = Field(default=None, ge=1)
    sort_order: int = Field(default=0)
    is_active: bool = True
    modifiers: List[MenuItemModifier] = Field(default_factory=list)

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class MenuItem(BaseModel):
    """Menu item entity representing a dish or product."""
    
    id: UUID
    restaurant_id: UUID
    category_id: UUID
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    base_price: float = Field(..., gt=0.0)
    image_url: Optional[str] = None
    gallery_images: List[str] = Field(default_factory=list)
    status: ItemStatus = ItemStatus.AVAILABLE
    dietary_indicators: List[DietaryIndicator] = Field(default_factory=list)
    allergen_info: List[str] = Field(default_factory=list)
    nutritional_info: Dict[str, Any] = Field(default_factory=dict)
    preparation_time: Optional[int] = None  # minutes
    sort_order: int = Field(default=0)
    is_active: bool = True
    availability_schedule: Dict[str, Any] = Field(default_factory=dict)
    daily_limit: Optional[int] = None
    sold_count: int = Field(default=0)
    created_at: datetime
    updated_at: datetime
    
    # Related entities
    variants: List[MenuItemVariant] = Field(default_factory=list)
    modifier_groups: List[MenuItemModifierGroup] = Field(default_factory=list)

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class MenuVersion(BaseModel):
    """Menu version entity for versioning and publishing."""
    
    id: UUID
    restaurant_id: UUID
    version_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    status: MenuStatus = MenuStatus.DRAFT
    is_current_live: bool = False
    scheduled_publish_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class MenuAvailabilitySchedule(BaseModel):
    """Menu availability schedule configuration."""
    
    # Weekly schedule
    monday: Optional[Dict[str, str]] = None  # {"start": "09:00", "end": "22:00"}
    tuesday: Optional[Dict[str, str]] = None
    wednesday: Optional[Dict[str, str]] = None
    thursday: Optional[Dict[str, str]] = None
    friday: Optional[Dict[str, str]] = None
    saturday: Optional[Dict[str, str]] = None
    sunday: Optional[Dict[str, str]] = None
    
    # Special dates
    special_dates: Dict[str, Dict[str, str]] = Field(default_factory=dict)  # {"2024-12-25": {"closed": true}}
    holiday_schedule: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class MenuPublishRequest(BaseModel):
    """Menu publish request entity."""
    
    version_id: UUID
    publish_immediately: bool = True
    scheduled_publish_at: Optional[datetime] = None
    publish_notes: Optional[str] = None

    class Config:
        """Pydantic configuration."""
        from_attributes = True
