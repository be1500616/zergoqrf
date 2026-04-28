"""Create staff use case.

This module contains the use case for creating restaurant staff members.
"""

import logging
from typing import Any, Dict
from uuid import UUID

from app.common.supabase_client import get_supabase
from app.features.restaurants.application.restaurant_dtos import StaffCreateDTO
from app.features.restaurants.domain.restaurant_entities import RestaurantStaff
from app.features.restaurants.domain.restaurant_repos import IRestaurantStaffRepository
from supabase import Client

logger = logging.getLogger(__name__)


class CreateStaffUseCase:
    """Use case for creating restaurant staff members."""

    def __init__(self, staff_repository: IRestaurantStaffRepository):
        """Initialize the use case.

        Args:
            staff_repository: Repository for staff data access.
        """
        self._staff_repository = staff_repository

    async def execute(
        self, staff_data: StaffCreateDTO, restaurant_id: UUID, supabase: Client = None
    ) -> RestaurantStaff:
        """Execute the create staff use case.

        Args:
            staff_data: The staff creation data.
            restaurant_id: The restaurant ID to associate the staff with.
            supabase: Supabase client for user operations.

        Returns:
            The created staff entity.

        Raises:
            ValueError: If staff data is invalid.
            Exception: If staff creation fails.
        """
        if not supabase:
            supabase = get_supabase()

        try:
            # First, try to create a new user account
            user_id = await self._create_or_get_user(
                staff_data, restaurant_id, supabase
            )

            # Check if staff record already exists for this user-restaurant combination
            existing_staff = await self._staff_repository.get_staff_by_user_id(
                user_id, restaurant_id
            )
            if existing_staff:
                logger.info(
                    f"Staff record already exists for user {user_id} in restaurant {restaurant_id}"
                )
                raise Exception(
                    f"User with email {staff_data.email} is already a staff member of this restaurant. "
                    "Please use a different email address."
                )

            # Get default permissions for role
            default_permissions = self._get_default_permissions(staff_data.role)

            # Create staff record
            staff_dict = {
                "restaurant_id": restaurant_id,
                "user_id": user_id,
                "role": staff_data.role,
                "permissions": staff_data.permissions or default_permissions,
                "is_active": True,
            }

            staff = await self._staff_repository.create_staff(staff_dict)

            logger.info(
                f"Successfully created staff member: {staff.id} for restaurant: {restaurant_id}"
            )
            return staff

        except Exception as e:
            logger.error(
                f"Failed to create staff member for restaurant {restaurant_id}: {str(e)}",
                extra={
                    "restaurant_id": str(restaurant_id),
                    "staff_email": staff_data.email,
                    "staff_role": staff_data.role,
                    "error_type": type(e).__name__,
                },
            )
            # Don't re-wrap the exception if it's already a meaningful error
            if "already a staff member" in str(e) or "different email" in str(e):
                raise e
            raise Exception(f"Failed to create staff: {str(e)}")

    async def _create_or_get_user(
        self, staff_data: StaffCreateDTO, restaurant_id: UUID, supabase: Client
    ) -> UUID:
        """Create a new user or get existing user ID.

        Args:
            staff_data: The staff creation data.
            restaurant_id: The restaurant ID.
            supabase: Supabase client.

        Returns:
            The user ID (UUID).

        Raises:
            Exception: If user creation/retrieval fails.
        """
        try:
            # Try to create a new user account
            auth_response = supabase.auth.sign_up(
                {
                    "email": staff_data.email,
                    "password": staff_data.password,
                    "options": {
                        "data": {
                            "restaurant_id": str(restaurant_id),
                            "role": staff_data.role,
                            "name": staff_data.name,
                        }
                    },
                }
            )

            if not auth_response.user:
                raise Exception("Failed to create user account")

            logger.info(f"Created new user account: {auth_response.user.id}")
            return UUID(auth_response.user.id)

        except Exception as e:
            error_str = str(e).lower()

            # Check if this is a "user already registered" error
            if (
                "user already registered" in error_str
                or "already registered" in error_str
            ):
                logger.info(
                    f"User {staff_data.email} already exists, attempting to link to restaurant"
                )

                # Try to get the existing user by email
                try:
                    # Use admin API to get user by email
                    users_response = supabase.auth.admin.list_users()

                    if users_response and hasattr(users_response, "users"):
                        for user in users_response.users:
                            if user.email == staff_data.email:
                                logger.info(f"Found existing user: {user.id}")
                                return UUID(user.id)

                    # If we can't find the user, raise an error
                    raise Exception(
                        f"User with email {staff_data.email} already exists but could not be retrieved. "
                        "Please contact support."
                    )

                except Exception as lookup_error:
                    logger.error(f"Failed to lookup existing user: {str(lookup_error)}")
                    raise Exception(
                        f"User with email {staff_data.email} already exists but could not be linked. "
                        "Please use a different email or contact support."
                    )
            else:
                # Re-raise the original error for other types of failures
                logger.error(f"User creation failed: {str(e)}")
                raise Exception(f"Failed to create user account: {str(e)}")

    def _get_default_permissions(self, role: str) -> Dict[str, Any]:
        """Get default permissions for a staff role.

        Args:
            role: The staff role.

        Returns:
            Dictionary of default permissions.
        """
        permissions_map = {
            "owner": {
                "manage_restaurant": True,
                "manage_staff": True,
                "manage_menu": True,
                "manage_orders": True,
                "manage_tables": True,
                "view_reports": True,
                "manage_settings": True,
            },
            "manager": {
                "manage_menu": True,
                "manage_orders": True,
                "manage_tables": True,
                "view_reports": True,
                "manage_staff": False,
                "manage_restaurant": False,
                "manage_settings": False,
            },
            "kitchen": {
                "view_orders": True,
                "update_order_status": True,
                "manage_menu": False,
                "manage_orders": False,
                "manage_tables": False,
                "view_reports": False,
            },
            "service": {
                "view_orders": True,
                "manage_orders": True,
                "manage_tables": True,
                "view_reports": False,
                "manage_menu": False,
            },
        }

        return permissions_map.get(role, {})
