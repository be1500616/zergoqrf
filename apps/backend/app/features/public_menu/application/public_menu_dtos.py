"""Public menu DTOs.

This module contains data transfer objects for public menu operations.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field

from ..domain.public_menu_entities import (
    PublicDietaryIndicator,
    PublicItemStatus,
)


class PublicRestaurantBrandingDTO(BaseModel):
    """DTO for public restaurant branding information."""
    
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


class PublicMenuCategoryDTO(BaseModel):
    """DTO for public menu category."""
    
    id: UUID
    name: str
    description: Optional[str] = None
    sort_order: int = 0
    item_count: int = 0
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class PublicMenuItemDTO(BaseModel):
    """DTO for public menu item."""
    
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


class PublicMenuStructureDTO(BaseModel):
    """DTO for complete public menu structure."""
    
    restaurant: PublicRestaurantBrandingDTO
    categories: List[PublicMenuCategoryDTO]
    items: List[PublicMenuItemDTO]
    last_updated: datetime
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class PublicMenuSearchRequestDTO(BaseModel):
    """DTO for menu search request."""
    
    query: str = Field(..., min_length=1, max_length=100)
    limit: int = Field(default=50, ge=1, le=100)
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class PublicMenuSearchResultDTO(BaseModel):
    """DTO for menu search results."""
    
    items: List[PublicMenuItemDTO]
    total_count: int
    search_query: str
    categories_found: List[PublicMenuCategoryDTO] = Field(default_factory=list)
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
