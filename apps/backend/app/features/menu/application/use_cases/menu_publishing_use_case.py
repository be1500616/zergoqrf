"""Menu publishing use case.

This module contains the business logic for menu publishing and versioning.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from uuid import UUID

from ..menu_dtos import MenuPublishDTO, MenuVersionResponseDTO
from ...domain.menu_repos import IMenuVersionRepository, IMenuCategoryRepository, IMenuItemRepository
from ...domain.menu_entities import MenuStatus


class MenuPublishingUseCase:
    """Use case for menu publishing operations."""

    def __init__(
        self,
        version_repo: IMenuVersionRepository,
        category_repo: IMenuCategoryRepository,
        item_repo: IMenuItemRepository,
    ):
        """Initialize the use case.
        
        Args:
            version_repo: Menu version repository.
            category_repo: Menu category repository.
            item_repo: Menu item repository.
        """
        self._version_repo = version_repo
        self._category_repo = category_repo
        self._item_repo = item_repo

    async def create_draft_version(
        self,
        restaurant_id: UUID,
        created_by: UUID,
        version_name: str,
        description: Optional[str] = None,
    ) -> MenuVersionResponseDTO:
        """Create a new draft menu version.
        
        Args:
            restaurant_id: The restaurant ID.
            created_by: User ID creating the version.
            version_name: Name for the version.
            description: Optional description.
            
        Returns:
            The created version DTO.
            
        Raises:
            ValueError: If validation fails.
        """
        # Validate version name uniqueness
        existing_versions = await self._version_repo.get_restaurant_versions(restaurant_id)
        if any(v.version_name == version_name for v in existing_versions):
            raise ValueError(f"Version name '{version_name}' already exists")
        
        # Create version data
        version_data = {
            "restaurant_id": restaurant_id,
            "version_name": version_name,
            "description": description,
            "status": MenuStatus.DRAFT,
            "created_by": created_by,
        }
        
        # Create version
        version = await self._version_repo.create_version(version_data)
        
        return MenuVersionResponseDTO.model_validate(version)

    async def publish_menu_version(
        self,
        version_id: UUID,
        publish_data: MenuPublishDTO,
    ) -> MenuVersionResponseDTO:
        """Publish a menu version.
        
        Args:
            version_id: The version ID to publish.
            publish_data: Publishing configuration.
            
        Returns:
            The published version DTO.
            
        Raises:
            ValueError: If validation fails.
        """
        # Get the version to publish
        version = await self._version_repo.get_version_by_id(version_id)
        if not version:
            raise ValueError("Version not found")
        
        if version.status == MenuStatus.LIVE:
            raise ValueError("Version is already live")
        
        # Validate menu has content
        await self._validate_menu_content(version.restaurant_id)
        
        # Prepare publish data
        publish_dict = publish_data.model_dump()
        
        if publish_data.publish_immediately:
            publish_dict["published_at"] = datetime.utcnow()
            publish_dict["status"] = MenuStatus.LIVE
        else:
            publish_dict["status"] = MenuStatus.SCHEDULED
        
        # Publish the version
        published_version = await self._version_repo.publish_version(version_id, publish_dict)
        
        return MenuVersionResponseDTO.model_validate(published_version)

    async def rollback_menu_version(
        self,
        restaurant_id: UUID,
        version_id: UUID,
    ) -> MenuVersionResponseDTO:
        """Rollback to a previous menu version.
        
        Args:
            restaurant_id: The restaurant ID.
            version_id: The version ID to rollback to.
            
        Returns:
            The new current version DTO.
            
        Raises:
            ValueError: If validation fails.
        """
        # Get the version to rollback to
        version = await self._version_repo.get_version_by_id(version_id)
        if not version:
            raise ValueError("Version not found")
        
        if version.restaurant_id != restaurant_id:
            raise ValueError("Version does not belong to this restaurant")
        
        if version.status not in [MenuStatus.LIVE, MenuStatus.ARCHIVED]:
            raise ValueError("Can only rollback to live or archived versions")
        
        # Perform rollback
        rolled_back_version = await self._version_repo.rollback_to_version(restaurant_id, version_id)
        
        return MenuVersionResponseDTO.model_validate(rolled_back_version)

    async def get_menu_preview(
        self,
        restaurant_id: UUID,
        version_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """Get menu preview for a specific version.
        
        Args:
            restaurant_id: The restaurant ID.
            version_id: Optional version ID (defaults to current live).
            
        Returns:
            Menu preview data.
        """
        # Get version info
        if version_id:
            version = await self._version_repo.get_version_by_id(version_id)
        else:
            version = await self._version_repo.get_current_live_version(restaurant_id)
        
        if not version:
            raise ValueError("No menu version found")
        
        # Get menu structure
        categories = await self._category_repo.get_category_hierarchy(restaurant_id)
        items = await self._item_repo.get_restaurant_items(restaurant_id)
        
        # Build hierarchical structure
        category_map = {str(cat.id): cat for cat in categories}
        item_map = {}
        
        # Group items by category
        for item in items:
            category_id = str(item.category_id)
            if category_id not in item_map:
                item_map[category_id] = []
            item_map[category_id].append(item)
        
        # Build preview structure
        preview_categories = []
        for category in categories:
            if category.parent_category_id is None:  # Root categories only
                category_data = {
                    "id": str(category.id),
                    "name": category.name,
                    "description": category.description,
                    "items": item_map.get(str(category.id), []),
                    "subcategories": []
                }
                
                # Add subcategories
                for subcat in categories:
                    if subcat.parent_category_id == category.id:
                        subcat_data = {
                            "id": str(subcat.id),
                            "name": subcat.name,
                            "description": subcat.description,
                            "items": item_map.get(str(subcat.id), []),
                        }
                        category_data["subcategories"].append(subcat_data)
                
                preview_categories.append(category_data)
        
        return {
            "version": version,
            "categories": preview_categories,
            "total_items": len(items),
            "active_items": len([item for item in items if item.is_active]),
        }

    async def _validate_menu_content(self, restaurant_id: UUID) -> None:
        """Validate that menu has sufficient content for publishing.
        
        Args:
            restaurant_id: The restaurant ID.
            
        Raises:
            ValueError: If validation fails.
        """
        # Check for at least one category
        categories = await self._category_repo.get_restaurant_categories(restaurant_id)
        if not categories:
            raise ValueError("Menu must have at least one category before publishing")
        
        # Check for at least one active item
        items = await self._item_repo.get_restaurant_items(restaurant_id)
        active_items = [item for item in items if item.is_active]
        if not active_items:
            raise ValueError("Menu must have at least one active item before publishing")
        
        # Validate that all items have valid categories
        category_ids = {str(cat.id) for cat in categories}
        for item in active_items:
            if str(item.category_id) not in category_ids:
                raise ValueError(f"Item '{item.name}' belongs to an invalid category")

    async def get_version_statistics(self, version_id: UUID) -> Dict[str, Any]:
        """Get statistics for a menu version.
        
        Args:
            version_id: The version ID.
            
        Returns:
            Version statistics.
        """
        version = await self._version_repo.get_version_by_id(version_id)
        if not version:
            raise ValueError("Version not found")
        
        # Get menu data
        categories = await self._category_repo.get_restaurant_categories(version.restaurant_id)
        items = await self._item_repo.get_restaurant_items(version.restaurant_id)
        
        # Calculate statistics
        active_categories = len([cat for cat in categories if cat.is_active])
        active_items = len([item for item in items if item.is_active])
        featured_items = len([item for item in items if item.status.value == "featured"])
        
        # Price statistics
        prices = [item.base_price for item in items if item.is_active]
        avg_price = sum(prices) / len(prices) if prices else 0
        
        return {
            "version_id": str(version_id),
            "version_name": version.version_name,
            "status": version.status,
            "total_categories": len(categories),
            "active_categories": active_categories,
            "total_items": len(items),
            "active_items": active_items,
            "featured_items": featured_items,
            "average_price": avg_price,
            "price_range": {
                "min": min(prices) if prices else 0,
                "max": max(prices) if prices else 0,
            },
            "created_at": version.created_at,
            "published_at": version.published_at,
        }
