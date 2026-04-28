"""Menu repository interfaces.

This module defines the abstract repository interfaces for menu data access.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID

from .menu_entities import (
    MenuCategory, MenuItem, MenuItemVariant, MenuItemModifierGroup,
    MenuItemModifier, MenuVersion, MenuStatus, ItemStatus
)


class IMenuCategoryRepository(ABC):
    """Abstract repository interface for menu category data access."""

    @abstractmethod
    async def create_category(self, category_data: dict) -> MenuCategory:
        """Create a new menu category.
        
        Args:
            category_data: Dictionary containing category information.
            
        Returns:
            The created category entity.
            
        Raises:
            RepositoryError: If category creation fails.
        """
        pass

    @abstractmethod
    async def get_category_by_id(self, category_id: UUID) -> Optional[MenuCategory]:
        """Get category by ID.
        
        Args:
            category_id: The category ID.
            
        Returns:
            The category entity if found, None otherwise.
        """
        pass

    @abstractmethod
    async def get_restaurant_categories(self, restaurant_id: UUID, include_inactive: bool = False) -> List[MenuCategory]:
        """Get all categories for a restaurant.
        
        Args:
            restaurant_id: The restaurant ID.
            include_inactive: Whether to include inactive categories.
            
        Returns:
            List of category entities.
        """
        pass

    @abstractmethod
    async def get_category_hierarchy(self, restaurant_id: UUID) -> List[MenuCategory]:
        """Get hierarchical category structure for a restaurant.
        
        Args:
            restaurant_id: The restaurant ID.
            
        Returns:
            List of categories with hierarchical relationships.
        """
        pass

    @abstractmethod
    async def update_category(self, category_id: UUID, update_data: dict) -> MenuCategory:
        """Update category information.
        
        Args:
            category_id: The category ID.
            update_data: Dictionary containing fields to update.
            
        Returns:
            The updated category entity.
            
        Raises:
            RepositoryError: If category update fails.
        """
        pass

    @abstractmethod
    async def delete_category(self, category_id: UUID) -> bool:
        """Delete a category.
        
        Args:
            category_id: The category ID.
            
        Returns:
            True if deletion was successful.
            
        Raises:
            RepositoryError: If category deletion fails.
        """
        pass

    @abstractmethod
    async def reorder_categories(self, category_orders: List[Dict[str, Any]]) -> bool:
        """Reorder categories.
        
        Args:
            category_orders: List of category ID and sort order mappings.
            
        Returns:
            True if reordering was successful.
        """
        pass


class IMenuItemRepository(ABC):
    """Abstract repository interface for menu item data access."""

    @abstractmethod
    async def create_item(self, item_data: dict) -> MenuItem:
        """Create a new menu item.
        
        Args:
            item_data: Dictionary containing item information.
            
        Returns:
            The created item entity.
            
        Raises:
            RepositoryError: If item creation fails.
        """
        pass

    @abstractmethod
    async def get_item_by_id(self, item_id: UUID, include_relations: bool = True) -> Optional[MenuItem]:
        """Get item by ID.
        
        Args:
            item_id: The item ID.
            include_relations: Whether to include variants and modifiers.
            
        Returns:
            The item entity if found, None otherwise.
        """
        pass

    @abstractmethod
    async def get_category_items(self, category_id: UUID, include_inactive: bool = False) -> List[MenuItem]:
        """Get all items in a category.
        
        Args:
            category_id: The category ID.
            include_inactive: Whether to include inactive items.
            
        Returns:
            List of item entities.
        """
        pass

    @abstractmethod
    async def get_restaurant_items(self, restaurant_id: UUID, include_inactive: bool = False) -> List[MenuItem]:
        """Get all items for a restaurant.
        
        Args:
            restaurant_id: The restaurant ID.
            include_inactive: Whether to include inactive items.
            
        Returns:
            List of item entities.
        """
        pass

    @abstractmethod
    async def update_item(self, item_id: UUID, update_data: dict) -> MenuItem:
        """Update item information.
        
        Args:
            item_id: The item ID.
            update_data: Dictionary containing fields to update.
            
        Returns:
            The updated item entity.
            
        Raises:
            RepositoryError: If item update fails.
        """
        pass

    @abstractmethod
    async def delete_item(self, item_id: UUID) -> bool:
        """Delete an item.
        
        Args:
            item_id: The item ID.
            
        Returns:
            True if deletion was successful.
            
        Raises:
            RepositoryError: If item deletion fails.
        """
        pass

    @abstractmethod
    async def update_item_status(self, item_id: UUID, status: ItemStatus) -> MenuItem:
        """Update item status.
        
        Args:
            item_id: The item ID.
            status: The new status.
            
        Returns:
            The updated item entity.
        """
        pass

    @abstractmethod
    async def search_items(self, restaurant_id: UUID, query: str, filters: Dict[str, Any] = None) -> List[MenuItem]:
        """Search items by name or description.
        
        Args:
            restaurant_id: The restaurant ID.
            query: Search query string.
            filters: Additional filters (category, status, etc.).
            
        Returns:
            List of matching item entities.
        """
        pass


class IMenuVersionRepository(ABC):
    """Abstract repository interface for menu version data access."""

    @abstractmethod
    async def create_version(self, version_data: dict) -> MenuVersion:
        """Create a new menu version.
        
        Args:
            version_data: Dictionary containing version information.
            
        Returns:
            The created version entity.
            
        Raises:
            RepositoryError: If version creation fails.
        """
        pass

    @abstractmethod
    async def get_version_by_id(self, version_id: UUID) -> Optional[MenuVersion]:
        """Get version by ID.
        
        Args:
            version_id: The version ID.
            
        Returns:
            The version entity if found, None otherwise.
        """
        pass

    @abstractmethod
    async def get_restaurant_versions(self, restaurant_id: UUID) -> List[MenuVersion]:
        """Get all versions for a restaurant.
        
        Args:
            restaurant_id: The restaurant ID.
            
        Returns:
            List of version entities.
        """
        pass

    @abstractmethod
    async def get_current_live_version(self, restaurant_id: UUID) -> Optional[MenuVersion]:
        """Get the current live version for a restaurant.
        
        Args:
            restaurant_id: The restaurant ID.
            
        Returns:
            The current live version if found, None otherwise.
        """
        pass

    @abstractmethod
    async def publish_version(self, version_id: UUID, publish_data: dict) -> MenuVersion:
        """Publish a menu version.
        
        Args:
            version_id: The version ID.
            publish_data: Publishing configuration.
            
        Returns:
            The published version entity.
            
        Raises:
            RepositoryError: If publishing fails.
        """
        pass

    @abstractmethod
    async def rollback_to_version(self, restaurant_id: UUID, version_id: UUID) -> MenuVersion:
        """Rollback to a previous version.
        
        Args:
            restaurant_id: The restaurant ID.
            version_id: The version ID to rollback to.
            
        Returns:
            The new current version entity.
            
        Raises:
            RepositoryError: If rollback fails.
        """
        pass
