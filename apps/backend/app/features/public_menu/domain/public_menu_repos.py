"""Public menu repository interfaces.

This module contains repository interfaces for public menu data access.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from .public_menu_entities import (
    PublicMenuStructure,
    PublicRestaurantBranding,
    PublicMenuCategory,
    PublicMenuItem,
    PublicMenuSearchResult,
)


class IPublicMenuRepository(ABC):
    """Interface for public menu data access."""
    
    @abstractmethod
    async def get_restaurant_by_code(self, restaurant_code: str) -> Optional[PublicRestaurantBranding]:
        """Get restaurant branding information by code.
        
        Args:
            restaurant_code: Restaurant code from QR code URL.
            
        Returns:
            Restaurant branding information or None if not found.
        """
        pass
    
    @abstractmethod
    async def get_restaurant_by_id(self, restaurant_id: UUID) -> Optional[PublicRestaurantBranding]:
        """Get restaurant branding information by ID.
        
        Args:
            restaurant_id: Restaurant UUID.
            
        Returns:
            Restaurant branding information or None if not found.
        """
        pass
    
    @abstractmethod
    async def get_public_menu_structure(self, restaurant_id: UUID) -> Optional[PublicMenuStructure]:
        """Get complete public menu structure for a restaurant.
        
        Args:
            restaurant_id: Restaurant UUID.
            
        Returns:
            Complete menu structure or None if not found.
        """
        pass
    
    @abstractmethod
    async def get_menu_categories(self, restaurant_id: UUID) -> List[PublicMenuCategory]:
        """Get menu categories for a restaurant.
        
        Args:
            restaurant_id: Restaurant UUID.
            
        Returns:
            List of menu categories.
        """
        pass
    
    @abstractmethod
    async def get_menu_items_by_category(self, restaurant_id: UUID, category_id: UUID) -> List[PublicMenuItem]:
        """Get menu items for a specific category.
        
        Args:
            restaurant_id: Restaurant UUID.
            category_id: Category UUID.
            
        Returns:
            List of menu items in the category.
        """
        pass
    
    @abstractmethod
    async def search_menu_items(
        self, 
        restaurant_id: UUID, 
        query: str, 
        limit: int = 50
    ) -> PublicMenuSearchResult:
        """Search menu items by name or description.
        
        Args:
            restaurant_id: Restaurant UUID.
            query: Search query string.
            limit: Maximum number of results.
            
        Returns:
            Search results with matching items.
        """
        pass
    
    @abstractmethod
    async def get_featured_items(self, restaurant_id: UUID, limit: int = 10) -> List[PublicMenuItem]:
        """Get featured menu items for a restaurant.
        
        Args:
            restaurant_id: Restaurant UUID.
            limit: Maximum number of featured items.
            
        Returns:
            List of featured menu items.
        """
        pass
