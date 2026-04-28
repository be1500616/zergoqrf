"""Restaurant repository implementations.

This module contains concrete implementations of restaurant repository interfaces.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from app.core.config import settings
from app.features.restaurants.domain.restaurant_entities import (
    Restaurant,
    RestaurantStaff,
)
from app.features.restaurants.domain.restaurant_repos import (
    IRestaurantRepository,
    IRestaurantStaffRepository,
)
from supabase import Client


class RestaurantRepositoryImpl(IRestaurantRepository):
    """Concrete implementation of restaurant repository using Supabase."""

    def __init__(self, supabase: Client):
        """Initialize the repository.

        Args:
            supabase: Supabase client instance.
        """
        self._supabase = supabase

    async def create_restaurant(self, restaurant_data: dict) -> Restaurant:
        """Create a new restaurant.

        Args:
            restaurant_data: Dictionary containing restaurant information.

        Returns:
            The created restaurant entity.

        Raises:
            Exception: If restaurant creation fails.
        """
        try:
            result = (
                self._supabase.table("restaurants").insert(restaurant_data).execute()
            )

            if not result.data:
                raise Exception("Failed to create restaurant")

            return Restaurant(**result.data[0])
        except Exception as e:
            raise Exception(f"Failed to create restaurant: {str(e)}")

    async def get_restaurant_by_id(self, restaurant_id: UUID) -> Optional[Restaurant]:
        """Get restaurant by ID.

        Args:
            restaurant_id: The restaurant ID.

        Returns:
            The restaurant entity if found, None otherwise.
        """
        try:
            result = (
                self._supabase.table("restaurants")
                .select("*")
                .eq("id", str(restaurant_id))
                .execute()
            )

            if result.data:
                return Restaurant(**result.data[0])
            return None
        except Exception:
            return None

    async def get_restaurant_by_code(self, code: str) -> Optional[Restaurant]:
        """Get restaurant by unique code.

        Args:
            code: The restaurant code.

        Returns:
            The restaurant entity if found, None otherwise.
        """
        try:
            result = (
                self._supabase.table("restaurants")
                .select("*")
                .eq("code", code)
                .execute()
            )

            if result.data:
                return Restaurant(**result.data[0])
            return None
        except Exception:
            return None

    async def update_restaurant(
        self, restaurant_id: UUID, update_data: dict
    ) -> Restaurant:
        """Update restaurant information.

        Args:
            restaurant_id: The restaurant ID.
            update_data: Dictionary containing fields to update.

        Returns:
            The updated restaurant entity.

        Raises:
            Exception: If restaurant update fails.
        """
        try:
            result = (
                self._supabase.table("restaurants")
                .update(update_data)
                .eq("id", str(restaurant_id))
                .execute()
            )

            if not result.data:
                raise Exception("Restaurant not found or update failed")

            return Restaurant(**result.data[0])
        except Exception as e:
            raise Exception(f"Failed to update restaurant: {str(e)}")

    async def delete_restaurant(self, restaurant_id: UUID) -> bool:
        """Delete a restaurant.

        Args:
            restaurant_id: The restaurant ID.

        Returns:
            True if deletion was successful.

        Raises:
            Exception: If restaurant deletion fails.
        """
        try:
            result = (
                self._supabase.table("restaurants")
                .delete()
                .eq("id", str(restaurant_id))
                .execute()
            )

            return len(result.data) > 0
        except Exception as e:
            raise Exception(f"Failed to delete restaurant: {str(e)}")

    async def code_exists(self, code: str) -> bool:
        """Check if restaurant code already exists.

        Args:
            code: The restaurant code to check.

        Returns:
            True if code exists, False otherwise.
        """
        try:
            result = (
                self._supabase.table("restaurants")
                .select("id")
                .eq("code", code)
                .execute()
            )

            return len(result.data) > 0
        except Exception:
            return False

    async def name_exists(self, name: str) -> bool:
        """Check if a restaurant name already exists.

        Args:
            name: The restaurant name to check.

        Returns:
            True if name exists, False otherwise.
        """
        try:
            # Case-insensitive check by comparing lower(name)
            result = (
                self._supabase.table("restaurants")
                .select("id")
                .ilike("name", name)
                .execute()
            )
            # Fallback: exact match if ilike is not supported
            if result.data is None:
                result = (
                    self._supabase.table("restaurants")
                    .select("id")
                    .eq("name", name)
                    .execute()
                )
            return len(result.data or []) > 0
        except Exception:
            return False


class RestaurantStaffRepositoryImpl(IRestaurantStaffRepository):
    """Concrete implementation of restaurant staff repository using Supabase."""

    def __init__(self, supabase: Client):
        """Initialize the repository.

        Args:
            supabase: Supabase client instance.
        """
        self._supabase = supabase

    async def create_staff(self, staff_data: dict) -> RestaurantStaff:
        """Create a new staff member.

        Args:
            staff_data: Dictionary containing staff information.

        Returns:
            The created staff entity.

        Raises:
            Exception: If staff creation fails.
        """
        try:
            # Convert UUID to string for Supabase
            staff_data_copy = staff_data.copy()
            if "restaurant_id" in staff_data_copy:
                staff_data_copy["restaurant_id"] = str(staff_data_copy["restaurant_id"])
            if "user_id" in staff_data_copy:
                staff_data_copy["user_id"] = str(staff_data_copy["user_id"])

            result = (
                self._supabase.table("restaurant_staff")
                .insert(staff_data_copy)
                .execute()
            )

            if not result.data:
                raise Exception("Failed to create staff member")

            return RestaurantStaff(**result.data[0])
        except Exception as e:
            raise Exception(f"Failed to create staff member: {str(e)}")

    async def get_staff_by_id(self, staff_id: UUID) -> Optional[RestaurantStaff]:
        """Get staff member by ID.

        Args:
            staff_id: The staff ID.

        Returns:
            The staff entity if found, None otherwise.
        """
        try:
            result = (
                self._supabase.table("restaurant_staff")
                .select("*")
                .eq("id", str(staff_id))
                .execute()
            )

            if result.data:
                return RestaurantStaff(**result.data[0])
            return None
        except Exception:
            return None

    async def get_restaurant_staff(self, restaurant_id: UUID) -> List[RestaurantStaff]:
        """Get all staff members for a restaurant.

        Args:
            restaurant_id: The restaurant ID.

        Returns:
            List of staff entities.
        """
        try:
            result = (
                self._supabase.table("restaurant_staff")
                .select("*")
                .eq("restaurant_id", str(restaurant_id))
                .eq("is_active", True)
                .execute()
            )

            return [RestaurantStaff(**staff) for staff in result.data]
        except Exception:
            return []

    async def update_staff(self, staff_id: UUID, update_data: dict) -> RestaurantStaff:
        """Update staff member information.

        Args:
            staff_id: The staff ID.
            update_data: Dictionary containing fields to update.

        Returns:
            The updated staff entity.

        Raises:
            Exception: If staff update fails.
        """
        try:
            result = (
                self._supabase.table("restaurant_staff")
                .update(update_data)
                .eq("id", str(staff_id))
                .execute()
            )

            if not result.data:
                raise Exception("Staff member not found or update failed")

            return RestaurantStaff(**result.data[0])
        except Exception as e:
            raise Exception(f"Failed to update staff member: {str(e)}")

    async def delete_staff(self, staff_id: UUID) -> bool:
        """Delete a staff member.

        Args:
            staff_id: The staff ID.

        Returns:
            True if deletion was successful.

        Raises:
            Exception: If staff deletion fails.
        """
        try:
            result = (
                self._supabase.table("restaurant_staff")
                .delete()
                .eq("id", str(staff_id))
                .execute()
            )

            return len(result.data) > 0
        except Exception as e:
            raise Exception(f"Failed to delete staff member: {str(e)}")

    async def get_staff_by_user_id(
        self, user_id: UUID, restaurant_id: UUID
    ) -> Optional[RestaurantStaff]:
        """Get staff member by user ID and restaurant ID.

        Args:
            user_id: The user ID.
            restaurant_id: The restaurant ID.

        Returns:
            The staff entity if found, None otherwise.
        """
        try:
            result = (
                self._supabase.table("restaurant_staff")
                .select("*")
                .eq("user_id", str(user_id))
                .eq("restaurant_id", str(restaurant_id))
                .eq("is_active", True)
                .execute()
            )

            if result.data:
                return RestaurantStaff(**result.data[0])
            return None
        except Exception:
            return None
