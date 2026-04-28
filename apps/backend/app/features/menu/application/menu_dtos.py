"""Menu Data Transfer Objects.

This module contains DTOs for transferring menu data between layers.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field

from ..domain.menu_entities import MenuStatus, ItemStatus, DietaryIndicator, ModifierType


class MenuCategoryCreateDTO(BaseModel):
    """DTO for creating a new menu category."""
    
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    parent_category_id: Optional[UUID] = None
    sort_order: int = Field(default=0)
    availability_schedule: Optional[Dict[str, Any]] = None

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class MenuCategoryUpdateDTO(BaseModel):
    """DTO for updating menu category."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    parent_category_id: Optional[UUID] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None
    availability_schedule: Optional[Dict[str, Any]] = None

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class MenuCategoryResponseDTO(BaseModel):
    """DTO for menu category response."""
    
    id: UUID
    restaurant_id: UUID
    name: str
    description: Optional[str] = None
    parent_category_id: Optional[UUID] = None
    sort_order: int
    is_active: bool
    availability_schedule: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    # Optional nested data
    subcategories: Optional[List['MenuCategoryResponseDTO']] = None
    item_count: Optional[int] = None

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class MenuItemVariantDTO(BaseModel):
    """DTO for menu item variant."""
    
    id: Optional[UUID] = None
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    price_adjustment: float = Field(default=0.0)
    sort_order: int = Field(default=0)
    is_active: bool = True

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class MenuItemModifierDTO(BaseModel):
    """DTO for menu item modifier."""
    
    id: Optional[UUID] = None
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    price: float = Field(default=0.0, ge=0.0)
    sort_order: int = Field(default=0)
    is_active: bool = True

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class MenuItemModifierGroupDTO(BaseModel):
    """DTO for menu item modifier group."""
    
    id: Optional[UUID] = None
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    modifier_type: ModifierType = ModifierType.SINGLE_SELECT
    is_required: bool = False
    min_selections: int = Field(default=0, ge=0)
    max_selections: Optional[int] = Field(default=None, ge=1)
    sort_order: int = Field(default=0)
    is_active: bool = True
    modifiers: List[MenuItemModifierDTO] = Field(default_factory=list)

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class MenuItemCreateDTO(BaseModel):
    """DTO for creating a new menu item."""
    
    category_id: UUID
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    base_price: float = Field(..., gt=0.0)
    image_url: Optional[str] = None
    gallery_images: List[str] = Field(default_factory=list)
    status: ItemStatus = ItemStatus.AVAILABLE
    dietary_indicators: List[DietaryIndicator] = Field(default_factory=list)
    allergen_info: List[str] = Field(default_factory=list)
    nutritional_info: Optional[Dict[str, Any]] = None
    preparation_time: Optional[int] = None
    sort_order: int = Field(default=0)
    availability_schedule: Optional[Dict[str, Any]] = None
    daily_limit: Optional[int] = None
    variants: List[MenuItemVariantDTO] = Field(default_factory=list)
    modifier_groups: List[MenuItemModifierGroupDTO] = Field(default_factory=list)

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class MenuItemUpdateDTO(BaseModel):
    """DTO for updating menu item."""
    
    category_id: Optional[UUID] = None
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    base_price: Optional[float] = Field(None, gt=0.0)
    image_url: Optional[str] = None
    gallery_images: Optional[List[str]] = None
    status: Optional[ItemStatus] = None
    dietary_indicators: Optional[List[DietaryIndicator]] = None
    allergen_info: Optional[List[str]] = None
    nutritional_info: Optional[Dict[str, Any]] = None
    preparation_time: Optional[int] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None
    availability_schedule: Optional[Dict[str, Any]] = None
    daily_limit: Optional[int] = None
    variants: Optional[List[MenuItemVariantDTO]] = None
    modifier_groups: Optional[List[MenuItemModifierGroupDTO]] = None

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class MenuItemResponseDTO(BaseModel):
    """DTO for menu item response."""
    
    id: UUID
    restaurant_id: UUID
    category_id: UUID
    name: str
    description: Optional[str] = None
    base_price: float
    image_url: Optional[str] = None
    gallery_images: List[str]
    status: ItemStatus
    dietary_indicators: List[DietaryIndicator]
    allergen_info: List[str]
    nutritional_info: Dict[str, Any]
    preparation_time: Optional[int] = None
    sort_order: int
    is_active: bool
    availability_schedule: Dict[str, Any]
    daily_limit: Optional[int] = None
    sold_count: int
    created_at: datetime
    updated_at: datetime
    
    # Related data
    category_name: Optional[str] = None
    variants: List[MenuItemVariantDTO] = Field(default_factory=list)
    modifier_groups: List[MenuItemModifierGroupDTO] = Field(default_factory=list)

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class MenuVersionCreateDTO(BaseModel):
    """DTO for creating a new menu version."""
    
    version_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class MenuVersionResponseDTO(BaseModel):
    """DTO for menu version response."""
    
    id: UUID
    restaurant_id: UUID
    version_name: str
    description: Optional[str] = None
    status: MenuStatus
    is_current_live: bool
    scheduled_publish_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    
    # Statistics
    category_count: Optional[int] = None
    item_count: Optional[int] = None

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class MenuPublishDTO(BaseModel):
    """DTO for menu publishing request."""
    
    publish_immediately: bool = True
    scheduled_publish_at: Optional[datetime] = None
    publish_notes: Optional[str] = None

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class MenuStructureDTO(BaseModel):
    """DTO for complete menu structure."""
    
    categories: List[MenuCategoryResponseDTO]
    items: List[MenuItemResponseDTO]
    version_info: Optional[MenuVersionResponseDTO] = None

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class MenuSearchDTO(BaseModel):
    """DTO for menu search request."""
    
    query: Optional[str] = None
    category_id: Optional[UUID] = None
    status: Optional[ItemStatus] = None
    dietary_indicators: Optional[List[DietaryIndicator]] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    include_inactive: bool = False

    class Config:
        """Pydantic configuration."""
        from_attributes = True
