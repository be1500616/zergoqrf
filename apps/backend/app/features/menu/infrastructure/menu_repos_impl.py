"""Menu repository implementations.

This module contains concrete implementations of menu repository interfaces.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from supabase import Client

from ..domain.menu_repos import IMenuCategoryRepository, IMenuItemRepository, IMenuVersionRepository
from ..domain.menu_entities import MenuCategory, MenuItem, MenuVersion, ItemStatus, MenuStatus


class MenuCategoryRepositoryImpl(IMenuCategoryRepository):
    """Concrete implementation of menu category repository using Supabase."""

    def __init__(self, supabase: Client):
        """Initialize the repository.
        
        Args:
            supabase: Supabase client instance.
        """
        self._supabase = supabase

    async def create_category(self, category_data: dict) -> MenuCategory:
        """Create a new menu category."""
        try:
            # Convert UUID to string for Supabase
            category_data_copy = category_data.copy()
            if "restaurant_id" in category_data_copy:
                category_data_copy["restaurant_id"] = str(category_data_copy["restaurant_id"])
            if "parent_category_id" in category_data_copy and category_data_copy["parent_category_id"]:
                category_data_copy["parent_category_id"] = str(category_data_copy["parent_category_id"])
            
            result = self._supabase.table("menu_categories").insert(category_data_copy).execute()
            
            if not result.data:
                raise Exception("Failed to create menu category")
            
            return MenuCategory(**result.data[0])
        except Exception as e:
            raise Exception(f"Failed to create menu category: {str(e)}")

    async def get_category_by_id(self, category_id: UUID) -> Optional[MenuCategory]:
        """Get category by ID."""
        try:
            result = (
                self._supabase.table("menu_categories")
                .select("*")
                .eq("id", str(category_id))
                .execute()
            )
            
            if result.data:
                return MenuCategory(**result.data[0])
            return None
        except Exception:
            return None

    async def get_restaurant_categories(self, restaurant_id: UUID, include_inactive: bool = False) -> List[MenuCategory]:
        """Get all categories for a restaurant."""
        try:
            query = (
                self._supabase.table("menu_categories")
                .select("*")
                .eq("restaurant_id", str(restaurant_id))
                .order("sort_order", desc=False)
            )
            
            if not include_inactive:
                query = query.eq("is_active", True)
            
            result = query.execute()
            
            return [MenuCategory(**category) for category in result.data]
        except Exception:
            return []

    async def get_category_hierarchy(self, restaurant_id: UUID) -> List[MenuCategory]:
        """Get hierarchical category structure for a restaurant."""
        try:
            result = (
                self._supabase.table("menu_categories")
                .select("*")
                .eq("restaurant_id", str(restaurant_id))
                .eq("is_active", True)
                .order("parent_category_id", desc=False)
                .order("sort_order", desc=False)
                .execute()
            )
            
            return [MenuCategory(**category) for category in result.data]
        except Exception:
            return []

    async def update_category(self, category_id: UUID, update_data: dict) -> MenuCategory:
        """Update category information."""
        try:
            # Convert UUID to string for Supabase
            update_data_copy = update_data.copy()
            if "parent_category_id" in update_data_copy and update_data_copy["parent_category_id"]:
                update_data_copy["parent_category_id"] = str(update_data_copy["parent_category_id"])
            
            result = (
                self._supabase.table("menu_categories")
                .update(update_data_copy)
                .eq("id", str(category_id))
                .execute()
            )
            
            if not result.data:
                raise Exception("Category not found or update failed")
            
            return MenuCategory(**result.data[0])
        except Exception as e:
            raise Exception(f"Failed to update menu category: {str(e)}")

    async def delete_category(self, category_id: UUID) -> bool:
        """Delete a category."""
        try:
            result = (
                self._supabase.table("menu_categories")
                .delete()
                .eq("id", str(category_id))
                .execute()
            )
            
            return len(result.data) > 0
        except Exception as e:
            raise Exception(f"Failed to delete menu category: {str(e)}")

    async def reorder_categories(self, category_orders: List[Dict[str, Any]]) -> bool:
        """Reorder categories."""
        try:
            # Update sort orders in batch
            for order_data in category_orders:
                await self.update_category(
                    UUID(order_data["id"]),
                    {"sort_order": order_data["sort_order"]}
                )
            return True
        except Exception:
            return False


class MenuItemRepositoryImpl(IMenuItemRepository):
    """Concrete implementation of menu item repository using Supabase."""

    def __init__(self, supabase: Client):
        """Initialize the repository.
        
        Args:
            supabase: Supabase client instance.
        """
        self._supabase = supabase

    async def create_item(self, item_data: dict) -> MenuItem:
        """Create a new menu item."""
        try:
            # Convert UUIDs to strings for Supabase
            item_data_copy = item_data.copy()
            if "restaurant_id" in item_data_copy:
                item_data_copy["restaurant_id"] = str(item_data_copy["restaurant_id"])
            if "category_id" in item_data_copy:
                item_data_copy["category_id"] = str(item_data_copy["category_id"])
            
            result = self._supabase.table("menu_items").insert(item_data_copy).execute()
            
            if not result.data:
                raise Exception("Failed to create menu item")
            
            return MenuItem(**result.data[0])
        except Exception as e:
            raise Exception(f"Failed to create menu item: {str(e)}")

    async def get_item_by_id(self, item_id: UUID, include_relations: bool = True) -> Optional[MenuItem]:
        """Get item by ID."""
        try:
            if include_relations:
                # Get item with variants and modifier groups
                result = (
                    self._supabase.table("menu_items")
                    .select("*, menu_item_variants(*), menu_item_modifier_groups(*, menu_item_modifiers(*))")
                    .eq("id", str(item_id))
                    .execute()
                )
            else:
                result = (
                    self._supabase.table("menu_items")
                    .select("*")
                    .eq("id", str(item_id))
                    .execute()
                )
            
            if result.data:
                return MenuItem(**result.data[0])
            return None
        except Exception:
            return None

    async def get_category_items(self, category_id: UUID, include_inactive: bool = False) -> List[MenuItem]:
        """Get all items in a category."""
        try:
            query = (
                self._supabase.table("menu_items")
                .select("*")
                .eq("category_id", str(category_id))
                .order("sort_order", desc=False)
            )
            
            if not include_inactive:
                query = query.eq("is_active", True)
            
            result = query.execute()
            
            return [MenuItem(**item) for item in result.data]
        except Exception:
            return []

    async def get_restaurant_items(self, restaurant_id: UUID, include_inactive: bool = False) -> List[MenuItem]:
        """Get all items for a restaurant."""
        try:
            query = (
                self._supabase.table("menu_items")
                .select("*")
                .eq("restaurant_id", str(restaurant_id))
                .order("sort_order", desc=False)
            )
            
            if not include_inactive:
                query = query.eq("is_active", True)
            
            result = query.execute()
            
            return [MenuItem(**item) for item in result.data]
        except Exception:
            return []

    async def update_item(self, item_id: UUID, update_data: dict) -> MenuItem:
        """Update item information."""
        try:
            # Convert UUIDs to strings for Supabase
            update_data_copy = update_data.copy()
            if "category_id" in update_data_copy:
                update_data_copy["category_id"] = str(update_data_copy["category_id"])
            
            result = (
                self._supabase.table("menu_items")
                .update(update_data_copy)
                .eq("id", str(item_id))
                .execute()
            )
            
            if not result.data:
                raise Exception("Item not found or update failed")
            
            return MenuItem(**result.data[0])
        except Exception as e:
            raise Exception(f"Failed to update menu item: {str(e)}")

    async def delete_item(self, item_id: UUID) -> bool:
        """Delete an item."""
        try:
            result = (
                self._supabase.table("menu_items")
                .delete()
                .eq("id", str(item_id))
                .execute()
            )
            
            return len(result.data) > 0
        except Exception as e:
            raise Exception(f"Failed to delete menu item: {str(e)}")

    async def update_item_status(self, item_id: UUID, status: ItemStatus) -> MenuItem:
        """Update item status."""
        return await self.update_item(item_id, {"status": status.value})

    async def search_items(self, restaurant_id: UUID, query: str, filters: Dict[str, Any] = None) -> List[MenuItem]:
        """Search items by name or description."""
        try:
            supabase_query = (
                self._supabase.table("menu_items")
                .select("*")
                .eq("restaurant_id", str(restaurant_id))
            )
            
            if query:
                supabase_query = supabase_query.or_(f"name.ilike.%{query}%,description.ilike.%{query}%")
            
            if filters:
                if "category_id" in filters:
                    supabase_query = supabase_query.eq("category_id", str(filters["category_id"]))
                if "status" in filters:
                    supabase_query = supabase_query.eq("status", filters["status"])
                if not filters.get("include_inactive", False):
                    supabase_query = supabase_query.eq("is_active", True)
            
            result = supabase_query.execute()
            
            return [MenuItem(**item) for item in result.data]
        except Exception:
            return []


class MenuVersionRepositoryImpl(IMenuVersionRepository):
    """Concrete implementation of menu version repository using Supabase."""

    def __init__(self, supabase: Client):
        """Initialize the repository.
        
        Args:
            supabase: Supabase client instance.
        """
        self._supabase = supabase

    async def create_version(self, version_data: dict) -> MenuVersion:
        """Create a new menu version."""
        try:
            # Convert UUIDs to strings for Supabase
            version_data_copy = version_data.copy()
            if "restaurant_id" in version_data_copy:
                version_data_copy["restaurant_id"] = str(version_data_copy["restaurant_id"])
            if "created_by" in version_data_copy:
                version_data_copy["created_by"] = str(version_data_copy["created_by"])
            
            result = self._supabase.table("menu_versions").insert(version_data_copy).execute()
            
            if not result.data:
                raise Exception("Failed to create menu version")
            
            return MenuVersion(**result.data[0])
        except Exception as e:
            raise Exception(f"Failed to create menu version: {str(e)}")

    async def get_version_by_id(self, version_id: UUID) -> Optional[MenuVersion]:
        """Get version by ID."""
        try:
            result = (
                self._supabase.table("menu_versions")
                .select("*")
                .eq("id", str(version_id))
                .execute()
            )
            
            if result.data:
                return MenuVersion(**result.data[0])
            return None
        except Exception:
            return None

    async def get_restaurant_versions(self, restaurant_id: UUID) -> List[MenuVersion]:
        """Get all versions for a restaurant."""
        try:
            result = (
                self._supabase.table("menu_versions")
                .select("*")
                .eq("restaurant_id", str(restaurant_id))
                .order("created_at", desc=True)
                .execute()
            )
            
            return [MenuVersion(**version) for version in result.data]
        except Exception:
            return []

    async def get_current_live_version(self, restaurant_id: UUID) -> Optional[MenuVersion]:
        """Get the current live version for a restaurant."""
        try:
            result = (
                self._supabase.table("menu_versions")
                .select("*")
                .eq("restaurant_id", str(restaurant_id))
                .eq("is_current_live", True)
                .execute()
            )
            
            if result.data:
                return MenuVersion(**result.data[0])
            return None
        except Exception:
            return None

    async def publish_version(self, version_id: UUID, publish_data: dict) -> MenuVersion:
        """Publish a menu version."""
        try:
            # First, set all other versions as not current
            restaurant_result = await self.get_version_by_id(version_id)
            if restaurant_result:
                self._supabase.table("menu_versions").update({
                    "is_current_live": False
                }).eq("restaurant_id", str(restaurant_result.restaurant_id)).execute()
            
            # Then publish this version
            update_data = {
                "status": MenuStatus.LIVE.value,
                "is_current_live": True,
                "published_at": publish_data.get("published_at"),
                **publish_data
            }
            
            result = (
                self._supabase.table("menu_versions")
                .update(update_data)
                .eq("id", str(version_id))
                .execute()
            )
            
            if not result.data:
                raise Exception("Version not found or publish failed")
            
            return MenuVersion(**result.data[0])
        except Exception as e:
            raise Exception(f"Failed to publish menu version: {str(e)}")

    async def rollback_to_version(self, restaurant_id: UUID, version_id: UUID) -> MenuVersion:
        """Rollback to a previous version."""
        try:
            # Set all versions as not current
            self._supabase.table("menu_versions").update({
                "is_current_live": False
            }).eq("restaurant_id", str(restaurant_id)).execute()
            
            # Set the target version as current
            result = (
                self._supabase.table("menu_versions")
                .update({
                    "is_current_live": True,
                    "status": MenuStatus.LIVE.value
                })
                .eq("id", str(version_id))
                .execute()
            )
            
            if not result.data:
                raise Exception("Version not found or rollback failed")
            
            return MenuVersion(**result.data[0])
        except Exception as e:
            raise Exception(f"Failed to rollback to menu version: {str(e)}")
