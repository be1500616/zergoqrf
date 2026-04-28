"""Restaurant repository interfaces.

This module defines the abstract repository interfaces for restaurant data access.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from .restaurant_entities import Restaurant, RestaurantStaff


class IRestaurantRepository(ABC):
    """Abstract repository interface for restaurant data access."""

    @abstractmethod
    async def create_restaurant(self, restaurant_data: dict) -> Restaurant:
        """Create a new restaurant.

        Args:
            restaurant_data: Dictionary containing restaurant information.

        Returns:
            The created restaurant entity.

        Raises:
            RepositoryError: If restaurant creation fails.
        """
        pass

    @abstractmethod
    async def get_restaurant_by_id(self, restaurant_id: UUID) -> Optional[Restaurant]:
        """Get restaurant by ID.

        Args:
            restaurant_id: The restaurant ID.

        Returns:
            The restaurant entity if found, None otherwise.
        """
        pass

    @abstractmethod
    async def get_restaurant_by_code(self, code: str) -> Optional[Restaurant]:
        """Get restaurant by unique code.

        Args:
            code: The restaurant code.

        Returns:
            The restaurant entity if found, None otherwise.
        """
        pass

    @abstractmethod
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
            RepositoryError: If restaurant update fails.
        """
        pass

    @abstractmethod
    async def delete_restaurant(self, restaurant_id: UUID) -> bool:
        """Delete a restaurant.

        Args:
            restaurant_id: The restaurant ID.

        Returns:
            True if deletion was successful.

        Raises:
            RepositoryError: If restaurant deletion fails.
        """
        pass

    @abstractmethod
    async def code_exists(self, code: str) -> bool:
        """Check if restaurant code already exists.

        Args:
            code: The restaurant code to check.

        Returns:
            True if code exists, False otherwise.
        """
        pass

    @abstractmethod
    async def name_exists(self, name: str) -> bool:
        """Check if a restaurant name already exists.

        Args:
            name: The restaurant name to check.

        Returns:
            True if name exists, False otherwise.
        """
        pass


class IRestaurantStaffRepository(ABC):
    """Abstract repository interface for restaurant staff data access."""

    @abstractmethod
    async def create_staff(self, staff_data: dict) -> RestaurantStaff:
        """Create a new staff member.

        Args:
            staff_data: Dictionary containing staff information.

        Returns:
            The created staff entity.

        Raises:
            RepositoryError: If staff creation fails.
        """
        pass

    @abstractmethod
    async def get_staff_by_id(self, staff_id: UUID) -> Optional[RestaurantStaff]:
        """Get staff member by ID.

        Args:
            staff_id: The staff ID.

        Returns:
            The staff entity if found, None otherwise.
        """
        pass

    @abstractmethod
    async def get_restaurant_staff(self, restaurant_id: UUID) -> List[RestaurantStaff]:
        """Get all staff members for a restaurant.

        Args:
            restaurant_id: The restaurant ID.

        Returns:
            List of staff entities.
        """
        pass

    @abstractmethod
    async def update_staff(self, staff_id: UUID, update_data: dict) -> RestaurantStaff:
        """Update staff member information.

        Args:
            staff_id: The staff ID.
            update_data: Dictionary containing fields to update.

        Returns:
            The updated staff entity.

        Raises:
            RepositoryError: If staff update fails.
        """
        pass

    @abstractmethod
    async def delete_staff(self, staff_id: UUID) -> bool:
        """Delete a staff member.

        Args:
            staff_id: The staff ID.

        Returns:
            True if deletion was successful.

        Raises:
            RepositoryError: If staff deletion fails.
        """
        pass

    @abstractmethod
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
        pass
