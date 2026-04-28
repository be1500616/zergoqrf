"""Create restaurant use case.

This module contains the business logic for creating a new restaurant.
"""

import secrets
import string
from typing import Any, Dict
from uuid import UUID

from app.common.supabase_client import get_supabase
from app.features.restaurants.application.restaurant_dtos import (
    RestaurantCreateDTO,
    RestaurantRegistrationResponseDTO,
    RestaurantResponseDTO,
    StaffResponseDTO,
)
from app.features.restaurants.domain.restaurant_repos import (
    IRestaurantRepository,
    IRestaurantStaffRepository,
)


class CreateRestaurantUseCase:
    """Use case for creating a new restaurant with owner account."""

    def __init__(
        self,
        restaurant_repository: IRestaurantRepository,
        staff_repository: IRestaurantStaffRepository,
    ):
        """Initialize the use case.

        Args:
            restaurant_repository: Repository for restaurant data access.
            staff_repository: Repository for staff data access.
        """
        self._restaurant_repository = restaurant_repository
        self._staff_repository = staff_repository

    async def execute(
        self, restaurant_data: RestaurantCreateDTO
    ) -> RestaurantRegistrationResponseDTO:
        """Execute the create restaurant use case.

        Args:
            restaurant_data: The restaurant creation data.

        Returns:
            The registration response with restaurant, owner, and tokens.

        Raises:
            ValueError: If restaurant code generation fails or data is invalid.
            Exception: If restaurant creation fails.
        """
        # Generate unique restaurant code
        restaurant_code = await self._generate_unique_code()

        # Create restaurant data
        restaurant_dict = {
            "name": restaurant_data.name,
            "code": restaurant_code,
            "description": restaurant_data.description,
            "address": restaurant_data.address,
            "phone": restaurant_data.phone,
            "email": restaurant_data.email,
            "website": restaurant_data.website,
            "cuisine_type": restaurant_data.cuisine_type,
            "dining_style": restaurant_data.dining_style,
            "business_hours": {},
            "settings": self._get_default_settings(),
            "is_active": True,
        }

        # Create restaurant
        restaurant = await self._restaurant_repository.create_restaurant(
            restaurant_dict
        )

        try:
            # Create owner user account
            supabase = get_supabase()

            # First, try to sign up the user
            auth_response = supabase.auth.sign_up(
                {
                    "email": restaurant_data.owner_email,
                    "password": restaurant_data.owner_password,
                    "options": {
                        "data": {
                            "restaurant_id": str(restaurant.id),
                            "role": "owner",
                            "name": restaurant_data.owner_name,
                        }
                    },
                }
            )

            if not auth_response.user:
                raise Exception("Failed to create owner user account")

            # Create staff record for owner
            staff_dict = {
                "restaurant_id": restaurant.id,
                "user_id": UUID(auth_response.user.id),
                "role": "owner",
                "permissions": self._get_owner_permissions(),
                "is_active": True,
            }

            try:
                staff = await self._staff_repository.create_staff(staff_dict)
            except Exception as staff_error:
                # Check if this is a duplicate key error
                error_str = str(staff_error)
                if "duplicate key value violates unique constraint" in error_str:
                    # This means the user already exists and has a staff record
                    # This can happen if a previous registration attempt failed
                    # after creating the user but before completing registration
                    raise Exception(
                        f"A user with email {restaurant_data.owner_email} is "
                        "already associated with a restaurant. Please use a "
                        "different email address or contact support if you "
                        "believe this is an error."
                    )
                else:
                    # Re-raise the original error
                    raise staff_error

            # Prepare response
            restaurant_response = RestaurantResponseDTO.model_validate(restaurant)
            staff_response = StaffResponseDTO(
                id=staff.id,
                restaurant_id=staff.restaurant_id,
                user_id=staff.user_id,
                role=staff.role,
                permissions=staff.permissions,
                is_active=staff.is_active,
                created_at=staff.created_at,
                updated_at=staff.updated_at,
                email=restaurant_data.owner_email,
                name=restaurant_data.owner_name,
            )

            return RestaurantRegistrationResponseDTO(
                restaurant=restaurant_response,
                owner=staff_response,
                access_token=auth_response.session.access_token,
                refresh_token=auth_response.session.refresh_token,
                token_type="bearer",
                expires_in=auth_response.session.expires_in or 3600,
            )

        except Exception as e:
            # Rollback restaurant creation if user/staff creation fails
            try:
                await self._restaurant_repository.delete_restaurant(restaurant.id)
            except Exception:
                # If rollback fails, log it but don't mask the original error
                pass

            # Check if this is a duplicate key error (user already exists)
            error_str = str(e)
            if "duplicate key value violates unique constraint" in error_str:
                raise Exception(
                    f"A user with email {restaurant_data.owner_email} already exists. "
                    "Please use a different email address or contact support if you "
                    "believe this is an error."
                )

            raise Exception(f"Failed to create restaurant owner: {error_str}")

    async def _generate_unique_code(self, max_attempts: int = 10) -> str:
        """Generate a unique restaurant code.

        Args:
            max_attempts: Maximum number of attempts to generate unique code.

        Returns:
            A unique restaurant code.

        Raises:
            ValueError: If unable to generate unique code after max attempts.
        """
        # Characters to use (avoiding confusing ones like 0, O, I, 1)
        chars = string.ascii_uppercase + string.digits
        chars = (
            chars.replace("0", "").replace("O", "").replace("I", "").replace("1", "")
        )

        for _ in range(max_attempts):
            # Generate 6-character code
            code = "".join(secrets.choice(chars) for _ in range(6))

            # Check if code already exists
            if not await self._restaurant_repository.code_exists(code):
                return code

        raise ValueError("Unable to generate unique restaurant code")

    def _get_default_settings(self) -> Dict[str, Any]:
        """Get default restaurant settings.

        Returns:
            Dictionary containing default settings.
        """
        return {
            "currency": "INR",
            "tax_rate": 0.18,  # 18% GST
            "service_charge_rate": 0.0,
            "service_model": "self_service",
            "auto_accept_orders": True,
            "estimated_prep_time": 30,
            "email_notifications": True,
            "sms_notifications": False,
            "whatsapp_notifications": False,
        }

    def _get_owner_permissions(self) -> Dict[str, Any]:
        """Get owner permissions.

        Returns:
            Dictionary containing owner permissions.
        """
        return {
            "create_restaurant": True,
            "manage_restaurant": True,
            "manage_tables": True,
            "manage_menu": True,
            "manage_orders": True,
            "manage_staff": True,
            "view_analytics": True,
            "manage_payments": True,
        }
