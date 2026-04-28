"""Public menu Pydantic schemas.

This module contains Pydantic schemas for public menu API request/response validation.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from ..domain.public_menu_entities import PublicDietaryIndicator, PublicItemStatus


class PublicRestaurantBrandingSchema(BaseModel):
    """Schema for public restaurant branding information."""
    
    id: UUID
    name: str
    code: str
    logo_url: Optional[str] = None
    primary_color: str = "#FF6B35"
    secondary_color: str = "#2C3E50"
    accent_color: str = "#F39C12"
    description: Optional[str] = None
    cuisine_type: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class PublicMenuCategorySchema(BaseModel):
    """Schema for public menu category."""
    
    id: UUID
    name: str
    description: Optional[str] = None
    sort_order: int = 0
    item_count: int = 0
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class PublicMenuItemSchema(BaseModel):
    """Schema for public menu item."""
    
    id: UUID
    category_id: UUID
    name: str
    description: Optional[str] = None
    base_price: float
    image_url: Optional[str] = None
    gallery_images: List[str] = Field(default_factory=list)
    status: PublicItemStatus = PublicItemStatus.AVAILABLE
    dietary_indicators: List[PublicDietaryIndicator] = Field(default_factory=list)
    allergen_info: List[str] = Field(default_factory=list)
    preparation_time: Optional[int] = None
    sort_order: int = 0
    is_featured: bool = False
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class PublicMenuStructureSchema(BaseModel):
    """Schema for complete public menu structure."""
    
    restaurant: PublicRestaurantBrandingSchema
    categories: List[PublicMenuCategorySchema]
    items: List[PublicMenuItemSchema]
    last_updated: datetime
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class PublicMenuSearchRequestSchema(BaseModel):
    """Schema for menu search request."""
    
    query: str = Field(..., min_length=1, max_length=100, description="Search query")
    limit: int = Field(default=50, ge=1, le=100, description="Maximum number of results")


class PublicMenuSearchResponseSchema(BaseModel):
    """Schema for menu search response."""
    
    items: List[PublicMenuItemSchema]
    total_count: int
    search_query: str
    categories_found: List[PublicMenuCategorySchema] = Field(default_factory=list)
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class PublicMenuCategoryItemsSchema(BaseModel):
    """Schema for category items response."""
    
    category: PublicMenuCategorySchema
    items: List[PublicMenuItemSchema]
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class ErrorResponseSchema(BaseModel):
    """Schema for error responses."""
    
    error: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Additional error details")
    code: Optional[str] = Field(None, description="Error code")
