"""Public menu repository implementation.

This module contains the concrete implementation of public menu repositories.
"""

from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from supabase import Client

from ..domain.public_menu_entities import (
    PublicDietaryIndicator,
    PublicItemStatus,
    PublicMenuCategory,
    PublicMenuItem,
    PublicMenuSearchResult,
    PublicMenuStructure,
    PublicRestaurantBranding,
)
from ..domain.public_menu_repos import IPublicMenuRepository


class PublicMenuRepositoryImpl(IPublicMenuRepository):
    """Concrete implementation of public menu repository."""

    def __init__(self, supabase: Client):
        """Initialize the repository.

        Args:
            supabase: Supabase client instance.
        """
        self._supabase = supabase

    async def get_restaurant_by_code(
        self, restaurant_code: str
    ) -> Optional[PublicRestaurantBranding]:
        """Get restaurant branding information by code.

        Args:
            restaurant_code: Restaurant code from QR code URL.

        Returns:
            Restaurant branding information or None if not found.

        Raises:
            Exception: If database query fails.
        """
        try:
            result = (
                self._supabase.table("restaurants")
                .select(
                    "id, name, code, description, cuisine_type, phone, address, logo_url, primary_color, secondary_color, accent_color"
                )
                .eq("code", restaurant_code)
                .eq("is_active", True)
                .single()
                .execute()
            )

            if not result.data:
                return None

            data = result.data
            return PublicRestaurantBranding(
                id=UUID(data["id"]),
                name=data["name"],
                code=data["code"],
                logo_url=data.get("logo_url"),
                primary_color=data.get("primary_color", "#FF6B35"),
                secondary_color=data.get("secondary_color", "#2C3E50"),
                accent_color=data.get("accent_color", "#F39C12"),
                description=data.get("description"),
                cuisine_type=data.get("cuisine_type"),
                phone=data.get("phone"),
                address=data.get("address"),
            )

        except Exception as e:
            # Log the exception with context for debugging
            print(f"Error fetching restaurant by code '{restaurant_code}': {e}")
            import traceback

            traceback.print_exc()
            return None

    async def get_restaurant_by_id(
        self, restaurant_id: UUID
    ) -> Optional[PublicRestaurantBranding]:
        """Get restaurant branding information by ID.

        Args:
            restaurant_id: Restaurant UUID.

        Returns:
            Restaurant branding information or None if not found.

        Raises:
            Exception: If database query fails.
        """
        try:
            result = (
                self._supabase.table("restaurants")
                .select(
                    "id, name, code, description, cuisine_type, phone, "
                    "address, logo_url, primary_color, secondary_color, "
                    "accent_color"
                )
                .eq("id", str(restaurant_id))
                .eq("is_active", True)
                .single()
                .execute()
            )

            if not result.data:
                return None

            data = result.data
            return PublicRestaurantBranding(
                id=UUID(data["id"]),
                name=data["name"],
                code=data["code"],
                logo_url=data.get("logo_url"),
                primary_color=data.get("primary_color", "#FF6B35"),
                secondary_color=data.get("secondary_color", "#2C3E50"),
                accent_color=data.get("accent_color", "#F39C12"),
                description=data.get("description"),
                cuisine_type=data.get("cuisine_type"),
                phone=data.get("phone"),
                address=data.get("address"),
            )

        except Exception as e:
            # Log the exception with context for debugging
            print(f"Error fetching restaurant by ID '{restaurant_id}': {e}")
            import traceback

            traceback.print_exc()
            return None

    async def get_public_menu_structure(
        self, restaurant_id: UUID
    ) -> Optional[PublicMenuStructure]:
        """Get complete public menu structure for a restaurant."""
        try:
            # Get restaurant branding
            restaurant = await self.get_restaurant_by_id(restaurant_id)
            if not restaurant:
                return None

            # Get categories
            categories = await self.get_menu_categories(restaurant_id)

            # Get all menu items
            items_result = (
                self._supabase.table("menu_items")
                .select(
                    "id, category_id, name, description, base_price, image_url, gallery_images, status, dietary_indicators, allergen_info, preparation_time, sort_order"
                )
                .eq("restaurant_id", str(restaurant_id))
                .eq("is_active", True)
                .order("sort_order")
                .execute()
            )

            items = []
            for item_data in items_result.data or []:
                # Map status
                status = PublicItemStatus.AVAILABLE
                if item_data.get("status") == "unavailable":
                    status = PublicItemStatus.UNAVAILABLE
                elif item_data.get("status") == "featured":
                    status = PublicItemStatus.FEATURED

                # Map dietary indicators
                dietary_indicators = []
                for indicator in item_data.get("dietary_indicators", []):
                    try:
                        dietary_indicators.append(PublicDietaryIndicator(indicator))
                    except ValueError:
                        continue

                items.append(
                    PublicMenuItem(
                        id=UUID(item_data["id"]),
                        category_id=UUID(item_data["category_id"]),
                        name=item_data["name"],
                        description=item_data.get("description"),
                        base_price=float(item_data["base_price"]),
                        image_url=item_data.get("image_url"),
                        gallery_images=item_data.get("gallery_images")
                        or [],  # Handle None values
                        status=status,
                        dietary_indicators=dietary_indicators,
                        allergen_info=item_data.get("allergen_info")
                        or [],  # Handle None values
                        preparation_time=item_data.get("preparation_time"),
                        sort_order=item_data.get("sort_order", 0),
                        is_featured=(status == PublicItemStatus.FEATURED),
                    )
                )

            return PublicMenuStructure(
                restaurant=restaurant,
                categories=categories,
                items=items,
                last_updated=datetime.now(timezone.utc),
            )

        except Exception as e:
            # Log the exception for debugging
            print(f"Error in get_public_menu_structure: {e}")
            return None

    async def get_menu_categories(
        self, restaurant_id: UUID
    ) -> List[PublicMenuCategory]:
        """Get menu categories for a restaurant."""
        try:
            result = (
                self._supabase.table("menu_categories")
                .select("id, name, description, sort_order")
                .eq("restaurant_id", str(restaurant_id))
                .eq("is_active", True)
                .order("sort_order")
                .execute()
            )

            categories = []
            for category_data in result.data or []:
                # Count items in category
                items_count_result = (
                    self._supabase.table("menu_items")
                    .select("id", count="exact")
                    .eq("restaurant_id", str(restaurant_id))
                    .eq("category_id", category_data["id"])
                    .eq("is_active", True)
                    .execute()
                )

                item_count = items_count_result.count or 0

                categories.append(
                    PublicMenuCategory(
                        id=UUID(category_data["id"]),
                        name=category_data["name"],
                        description=category_data.get("description"),
                        sort_order=category_data.get("sort_order", 0),
                        item_count=item_count,
                    )
                )

            return categories

        except Exception:
            return []

    async def get_menu_items_by_category(
        self, restaurant_id: UUID, category_id: UUID
    ) -> List[PublicMenuItem]:
        """Get menu items for a specific category."""
        try:
            result = (
                self._supabase.table("menu_items")
                .select(
                    "id, category_id, name, description, base_price, image_url, gallery_images, status, dietary_indicators, allergen_info, preparation_time, sort_order"
                )
                .eq("restaurant_id", str(restaurant_id))
                .eq("category_id", str(category_id))
                .eq("is_active", True)
                .order("sort_order")
                .execute()
            )

            items = []
            for item_data in result.data or []:
                # Map status
                status = PublicItemStatus.AVAILABLE
                if item_data.get("status") == "unavailable":
                    status = PublicItemStatus.UNAVAILABLE
                elif item_data.get("status") == "featured":
                    status = PublicItemStatus.FEATURED

                # Map dietary indicators
                dietary_indicators = []
                for indicator in item_data.get("dietary_indicators", []):
                    try:
                        dietary_indicators.append(PublicDietaryIndicator(indicator))
                    except ValueError:
                        continue

                items.append(
                    PublicMenuItem(
                        id=UUID(item_data["id"]),
                        category_id=UUID(item_data["category_id"]),
                        name=item_data["name"],
                        description=item_data.get("description"),
                        base_price=float(item_data["base_price"]),
                        image_url=item_data.get("image_url"),
                        gallery_images=item_data.get("gallery_images", []),
                        status=status,
                        dietary_indicators=dietary_indicators,
                        allergen_info=item_data.get("allergen_info", []),
                        preparation_time=item_data.get("preparation_time"),
                        sort_order=item_data.get("sort_order", 0),
                        is_featured=(status == PublicItemStatus.FEATURED),
                    )
                )

            return items

        except Exception:
            return []

    async def search_menu_items(
        self, restaurant_id: UUID, query: str, limit: int = 50
    ) -> PublicMenuSearchResult:
        """Search menu items by name or description."""
        try:
            # Search in menu items
            search_query = f"%{query.lower()}%"
            result = (
                self._supabase.table("menu_items")
                .select(
                    "id, category_id, name, description, base_price, image_url, gallery_images, status, dietary_indicators, allergen_info, preparation_time, sort_order"
                )
                .eq("restaurant_id", str(restaurant_id))
                .eq("is_active", True)
                .or_(f"name.ilike.{search_query},description.ilike.{search_query}")
                .order("sort_order")
                .limit(limit)
                .execute()
            )

            items = []
            category_ids = set()

            for item_data in result.data or []:
                category_ids.add(item_data["category_id"])

                # Map status
                status = PublicItemStatus.AVAILABLE
                if item_data.get("status") == "unavailable":
                    status = PublicItemStatus.UNAVAILABLE
                elif item_data.get("status") == "featured":
                    status = PublicItemStatus.FEATURED

                # Map dietary indicators
                dietary_indicators = []
                for indicator in item_data.get("dietary_indicators", []):
                    try:
                        dietary_indicators.append(PublicDietaryIndicator(indicator))
                    except ValueError:
                        continue

                items.append(
                    PublicMenuItem(
                        id=UUID(item_data["id"]),
                        category_id=UUID(item_data["category_id"]),
                        name=item_data["name"],
                        description=item_data.get("description"),
                        base_price=float(item_data["base_price"]),
                        image_url=item_data.get("image_url"),
                        gallery_images=item_data.get("gallery_images", []),
                        status=status,
                        dietary_indicators=dietary_indicators,
                        allergen_info=item_data.get("allergen_info", []),
                        preparation_time=item_data.get("preparation_time"),
                        sort_order=item_data.get("sort_order", 0),
                        is_featured=(status == PublicItemStatus.FEATURED),
                    )
                )

            # Get categories for found items
            categories_found = []
            if category_ids:
                categories_result = (
                    self._supabase.table("menu_categories")
                    .select("id, name, description, sort_order")
                    .eq("restaurant_id", str(restaurant_id))
                    .in_("id", list(category_ids))
                    .eq("is_active", True)
                    .execute()
                )

                for category_data in categories_result.data or []:
                    categories_found.append(
                        PublicMenuCategory(
                            id=UUID(category_data["id"]),
                            name=category_data["name"],
                            description=category_data.get("description"),
                            sort_order=category_data.get("sort_order", 0),
                            item_count=0,  # Not needed for search results
                        )
                    )

            return PublicMenuSearchResult(
                items=items,
                total_count=len(items),
                search_query=query,
                categories_found=categories_found,
            )

        except Exception:
            return PublicMenuSearchResult(
                items=[],
                total_count=0,
                search_query=query,
                categories_found=[],
            )

    async def get_featured_items(
        self, restaurant_id: UUID, limit: int = 10
    ) -> List[PublicMenuItem]:
        """Get featured menu items for a restaurant."""
        try:
            result = (
                self._supabase.table("menu_items")
                .select(
                    "id, category_id, name, description, base_price, image_url, gallery_images, status, dietary_indicators, allergen_info, preparation_time, sort_order"
                )
                .eq("restaurant_id", str(restaurant_id))
                .eq("is_active", True)
                .eq("status", "featured")
                .order("sort_order")
                .limit(limit)
                .execute()
            )

            items = []
            for item_data in result.data or []:
                # Map dietary indicators
                dietary_indicators = []
                for indicator in item_data.get("dietary_indicators", []):
                    try:
                        dietary_indicators.append(PublicDietaryIndicator(indicator))
                    except ValueError:
                        continue

                items.append(
                    PublicMenuItem(
                        id=UUID(item_data["id"]),
                        category_id=UUID(item_data["category_id"]),
                        name=item_data["name"],
                        description=item_data.get("description"),
                        base_price=float(item_data["base_price"]),
                        image_url=item_data.get("image_url"),
                        gallery_images=item_data.get("gallery_images", []),
                        status=PublicItemStatus.FEATURED,
                        dietary_indicators=dietary_indicators,
                        allergen_info=item_data.get("allergen_info", []),
                        preparation_time=item_data.get("preparation_time"),
                        sort_order=item_data.get("sort_order", 0),
                        is_featured=True,
                    )
                )

            return items

        except Exception:
            return []
