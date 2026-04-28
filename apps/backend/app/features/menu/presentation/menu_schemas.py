"""Menu Pydantic schemas for API requests and responses.

This module contains Pydantic models for menu API endpoints.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field

from ..domain.menu_entities import MenuStatus, ItemStatus, DietaryIndicator, ModifierType


class MenuCategoryCreateSchema(BaseModel):
    """Schema for menu category creation request."""
    
    name: str = Field(..., min_length=1, max_length=100, description="Category name")
    description: Optional[str] = Field(None, description="Category description")
    parent_category_id: Optional[UUID] = Field(None, description="Parent category ID for subcategories")
    sort_order: int = Field(default=0, description="Sort order within parent")
    availability_schedule: Optional[Dict[str, Any]] = Field(None, description="Availability schedule")


class MenuCategoryUpdateSchema(BaseModel):
    """Schema for menu category update request."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    parent_category_id: Optional[UUID] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None
    availability_schedule: Optional[Dict[str, Any]] = None


class MenuCategoryResponseSchema(BaseModel):
    """Schema for menu category response."""
    
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
    subcategories: Optional[List['MenuCategoryResponseSchema']] = None
    item_count: Optional[int] = None

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class MenuItemVariantSchema(BaseModel):
    """Schema for menu item variant."""
    
    id: Optional[UUID] = None
    name: str = Field(..., min_length=1, max_length=50, description="Variant name (e.g., Small, Medium, Large)")
    description: Optional[str] = Field(None, description="Variant description")
    price_adjustment: float = Field(default=0.0, description="Price adjustment from base price")
    sort_order: int = Field(default=0, description="Sort order")
    is_active: bool = Field(default=True, description="Whether variant is active")


class MenuItemModifierSchema(BaseModel):
    """Schema for menu item modifier."""
    
    id: Optional[UUID] = None
    name: str = Field(..., min_length=1, max_length=100, description="Modifier name")
    description: Optional[str] = Field(None, description="Modifier description")
    price: float = Field(default=0.0, ge=0.0, description="Additional price for modifier")
    sort_order: int = Field(default=0, description="Sort order")
    is_active: bool = Field(default=True, description="Whether modifier is active")


class MenuItemModifierGroupSchema(BaseModel):
    """Schema for menu item modifier group."""
    
    id: Optional[UUID] = None
    name: str = Field(..., min_length=1, max_length=100, description="Modifier group name")
    description: Optional[str] = Field(None, description="Modifier group description")
    modifier_type: ModifierType = Field(default=ModifierType.SINGLE_SELECT, description="Selection type")
    is_required: bool = Field(default=False, description="Whether selection is required")
    min_selections: int = Field(default=0, ge=0, description="Minimum selections required")
    max_selections: Optional[int] = Field(default=None, ge=1, description="Maximum selections allowed")
    sort_order: int = Field(default=0, description="Sort order")
    is_active: bool = Field(default=True, description="Whether group is active")
    modifiers: List[MenuItemModifierSchema] = Field(default_factory=list, description="List of modifiers")


class MenuItemCreateSchema(BaseModel):
    """Schema for menu item creation request."""
    
    category_id: UUID = Field(..., description="Category ID")
    name: str = Field(..., min_length=1, max_length=100, description="Item name")
    description: Optional[str] = Field(None, max_length=500, description="Item description")
    base_price: float = Field(..., gt=0.0, description="Base price")
    image_url: Optional[str] = Field(None, description="Main image URL")
    gallery_images: List[str] = Field(default_factory=list, description="Additional images")
    status: ItemStatus = Field(default=ItemStatus.AVAILABLE, description="Item status")
    dietary_indicators: List[DietaryIndicator] = Field(default_factory=list, description="Dietary indicators")
    allergen_info: List[str] = Field(default_factory=list, description="Allergen information")
    nutritional_info: Optional[Dict[str, Any]] = Field(None, description="Nutritional information")
    preparation_time: Optional[int] = Field(None, ge=1, description="Preparation time in minutes")
    sort_order: int = Field(default=0, description="Sort order within category")
    availability_schedule: Optional[Dict[str, Any]] = Field(None, description="Availability schedule")
    daily_limit: Optional[int] = Field(None, ge=1, description="Daily quantity limit")
    variants: List[MenuItemVariantSchema] = Field(default_factory=list, description="Item variants")
    modifier_groups: List[MenuItemModifierGroupSchema] = Field(default_factory=list, description="Modifier groups")


class MenuItemUpdateSchema(BaseModel):
    """Schema for menu item update request."""
    
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
    preparation_time: Optional[int] = Field(None, ge=1)
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None
    availability_schedule: Optional[Dict[str, Any]] = None
    daily_limit: Optional[int] = Field(None, ge=1)
    variants: Optional[List[MenuItemVariantSchema]] = None
    modifier_groups: Optional[List[MenuItemModifierGroupSchema]] = None


class MenuItemResponseSchema(BaseModel):
    """Schema for menu item response."""
    
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
    variants: List[MenuItemVariantSchema] = Field(default_factory=list)
    modifier_groups: List[MenuItemModifierGroupSchema] = Field(default_factory=list)

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class MenuVersionCreateSchema(BaseModel):
    """Schema for menu version creation request."""
    
    version_name: str = Field(..., min_length=1, max_length=100, description="Version name")
    description: Optional[str] = Field(None, description="Version description")


class MenuVersionResponseSchema(BaseModel):
    """Schema for menu version response."""
    
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


class MenuPublishSchema(BaseModel):
    """Schema for menu publishing request."""
    
    publish_immediately: bool = Field(default=True, description="Publish immediately")
    scheduled_publish_at: Optional[datetime] = Field(None, description="Scheduled publish time")
    publish_notes: Optional[str] = Field(None, description="Publishing notes")


class MenuStructureResponseSchema(BaseModel):
    """Schema for complete menu structure response."""
    
    categories: List[MenuCategoryResponseSchema]
    items: List[MenuItemResponseSchema]
    version_info: Optional[MenuVersionResponseSchema] = None

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class MenuSearchSchema(BaseModel):
    """Schema for menu search request."""
    
    query: Optional[str] = Field(None, description="Search query")
    category_id: Optional[UUID] = Field(None, description="Filter by category")
    status: Optional[ItemStatus] = Field(None, description="Filter by status")
    dietary_indicators: Optional[List[DietaryIndicator]] = Field(None, description="Filter by dietary indicators")
    price_min: Optional[float] = Field(None, ge=0.0, description="Minimum price filter")
    price_max: Optional[float] = Field(None, ge=0.0, description="Maximum price filter")
    include_inactive: bool = Field(default=False, description="Include inactive items")


class CategoryReorderSchema(BaseModel):
    """Schema for category reordering request."""
    
    category_orders: List[Dict[str, Any]] = Field(..., description="List of category ID and sort order mappings")


class MenuItemBulkUpdateSchema(BaseModel):
    """Schema for bulk menu item updates."""
    
    item_ids: List[UUID] = Field(..., description="List of item IDs to update")
    update_data: Dict[str, Any] = Field(..., description="Data to update for all items")


class MenuAnalyticsResponseSchema(BaseModel):
    """Schema for menu analytics response."""
    
    total_categories: int
    total_items: int
    active_items: int
    featured_items: int
    items_by_status: Dict[str, int]
    items_by_category: Dict[str, int]
    average_price: float
    price_range: Dict[str, float]

    class Config:
        """Pydantic configuration."""
        from_attributes = True
