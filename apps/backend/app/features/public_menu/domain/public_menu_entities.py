"""Public menu domain entities.

This module contains entities optimized for public menu browsing.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field
from enum import Enum


class PublicDietaryIndicator(str, Enum):
    """Public dietary indicator enumeration."""
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    GLUTEN_FREE = "gluten_free"
    DAIRY_FREE = "dairy_free"
    NUT_FREE = "nut_free"
    SPICY = "spicy"
    HALAL = "halal"
    KOSHER = "kosher"


class PublicItemStatus(str, Enum):
    """Public item status enumeration."""
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    FEATURED = "featured"


class PublicRestaurantBranding(BaseModel):
    """Restaurant branding information for public display."""
    
    id: UUID
    name: str = Field(..., min_length=1, max_length=200)
    code: str = Field(..., min_length=1, max_length=50)
    logo_url: Optional[str] = None
    primary_color: str = Field(default="#FF6B35")
    secondary_color: str = Field(default="#2C3E50")
    accent_color: str = Field(default="#F39C12")
    description: Optional[str] = None
    cuisine_type: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class PublicMenuCategory(BaseModel):
    """Public menu category entity."""
    
    id: UUID
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    sort_order: int = Field(default=0)
    item_count: int = Field(default=0)
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class PublicMenuItem(BaseModel):
    """Public menu item entity optimized for customer browsing."""
    
    id: UUID
    category_id: UUID
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    base_price: float = Field(..., gt=0.0)
    image_url: Optional[str] = None
    gallery_images: List[str] = Field(default_factory=list)
    status: PublicItemStatus = PublicItemStatus.AVAILABLE
    dietary_indicators: List[PublicDietaryIndicator] = Field(default_factory=list)
    allergen_info: List[str] = Field(default_factory=list)
    preparation_time: Optional[int] = None  # minutes
    sort_order: int = Field(default=0)
    is_featured: bool = Field(default=False)
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class PublicMenuStructure(BaseModel):
    """Complete public menu structure."""
    
    restaurant: PublicRestaurantBranding
    categories: List[PublicMenuCategory]
    items: List[PublicMenuItem]
    last_updated: datetime
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class PublicMenuSearchResult(BaseModel):
    """Search result for menu items."""
    
    items: List[PublicMenuItem]
    total_count: int
    search_query: str
    categories_found: List[PublicMenuCategory] = Field(default_factory=list)
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
