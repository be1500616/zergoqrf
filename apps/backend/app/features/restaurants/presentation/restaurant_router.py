"""Restaurant API router.

This module contains FastAPI routes for restaurant management.
"""

from typing import Any, Dict, List
from uuid import UUID

from app.common.supabase_client import get_supabase
from app.features.auth.presentation.supabase_dependencies import (
    UserContext,
    get_current_user,
    get_user_supabase,
)
from app.features.restaurants.application.restaurant_dtos import (
    BusinessHoursUpdateDTO,
    RestaurantCreateDTO,
    RestaurantSettingsUpdateDTO,
    RestaurantUpdateDTO,
    StaffCreateDTO,
    StaffUpdateDTO,
)
from app.features.restaurants.application.use_cases.create_restaurant import (
    CreateRestaurantUseCase,
)
from app.features.restaurants.application.use_cases.create_staff import (
    CreateStaffUseCase,
)
from app.features.restaurants.infrastructure.restaurant_repos_impl import (
    RestaurantRepositoryImpl,
    RestaurantStaffRepositoryImpl,
)
from app.features.restaurants.presentation.restaurant_schemas import (
    BusinessHoursSchema,
    RestaurantCreateSchema,
    RestaurantRegistrationResponseSchema,
    RestaurantResponseSchema,
    RestaurantSettingsSchema,
    RestaurantUpdateSchema,
    StaffCreateSchema,
    StaffListResponseSchema,
    StaffResponseSchema,
    StaffUpdateSchema,
)
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from supabase import Client

router = APIRouter()


@router.post(
    "/register",
    response_model=RestaurantRegistrationResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def register_restaurant(
    restaurant_data: RestaurantCreateSchema,
    supabase: Client = Depends(get_supabase),
):
    """Register a new restaurant with owner account.

    Creates a new restaurant, owner user account, and staff record in a single transaction.
    Returns authentication tokens for immediate login.
    """
    try:
        # Initialize repositories
        restaurant_repo = RestaurantRepositoryImpl(supabase)
        staff_repo = RestaurantStaffRepositoryImpl(supabase)

        # Initialize use case
        create_restaurant_use_case = CreateRestaurantUseCase(
            restaurant_repo, staff_repo
        )

        # Convert schema to DTO
        restaurant_dto = RestaurantCreateDTO(**restaurant_data.model_dump())

        # Execute use case
        result = await create_restaurant_use_case.execute(restaurant_dto)

        return result

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}",
        )


@router.get("/validate/name")
async def validate_restaurant_name(
    name: str, supabase: Client = Depends(get_supabase)
) -> dict[str, bool]:
    """Validate restaurant name availability.

    Args:
        name: Proposed restaurant name
        supabase: Supabase client

    Returns:
        JSON indicating availability status
    """
    try:
        restaurant_repo = RestaurantRepositoryImpl(supabase)
        exists = await restaurant_repo.name_exists(name.strip())
        return {"available": not exists}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: {str(e)}",
        )


@router.get("/me", response_model=RestaurantResponseSchema)
async def get_my_restaurant(
    user_context: UserContext = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
):
    """Get current user's restaurant information."""
    try:
        # Get restaurant ID from user context
        restaurant_id = user_context.restaurant_id
        if not restaurant_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No restaurant associated with user",
            )

        # Get restaurant
        restaurant_repo = RestaurantRepositoryImpl(supabase)
        restaurant = await restaurant_repo.get_restaurant_by_id(UUID(restaurant_id))

        if not restaurant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found"
            )

        return RestaurantResponseSchema.model_validate(restaurant)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.put("/me", response_model=RestaurantResponseSchema)
async def update_my_restaurant(
    update_data: RestaurantUpdateSchema,
    user_context: UserContext = Depends(get_current_user),
    user_supabase: Client = Depends(get_user_supabase),
):
    """Update current user's restaurant information."""
    try:
        # Get restaurant ID from user context
        restaurant_id = user_context.restaurant_id
        if not restaurant_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No restaurant associated with user",
            )

        # Update restaurant using user-authenticated client for RLS
        restaurant_repo = RestaurantRepositoryImpl(user_supabase)
        update_dto = RestaurantUpdateDTO(**update_data.model_dump(exclude_unset=True))

        restaurant = await restaurant_repo.update_restaurant(
            UUID(restaurant_id), update_dto.model_dump(exclude_unset=True)
        )

        return RestaurantResponseSchema.model_validate(restaurant)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.put("/me/business-hours", response_model=RestaurantResponseSchema)
async def update_business_hours(
    hours_data: BusinessHoursSchema,
    current_user: UserContext = Depends(get_current_user),
    user_supabase: Client = Depends(get_user_supabase),
):
    """Update restaurant business hours."""
    try:
        # Get restaurant ID from user context
        restaurant_id = current_user.restaurant_id
        if not restaurant_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No restaurant associated with user",
            )

        # Update business hours using user-authenticated client for RLS
        restaurant_repo = RestaurantRepositoryImpl(user_supabase)
        hours_dto = BusinessHoursUpdateDTO(**hours_data.model_dump(exclude_unset=True))

        restaurant = await restaurant_repo.update_restaurant(
            UUID(restaurant_id),
            {"business_hours": hours_dto.model_dump(exclude_unset=True)},
        )

        return RestaurantResponseSchema.model_validate(restaurant)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.put("/me/settings", response_model=RestaurantResponseSchema)
async def update_restaurant_settings(
    settings_data: RestaurantSettingsSchema,
    current_user: UserContext = Depends(get_current_user),
    user_supabase: Client = Depends(get_user_supabase),
):
    """Update restaurant settings."""
    try:
        # Get restaurant ID from user context
        restaurant_id = current_user.restaurant_id
        if not restaurant_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No restaurant associated with user",
            )

        # Update settings using user-authenticated client for RLS
        restaurant_repo = RestaurantRepositoryImpl(user_supabase)
        settings_dto = RestaurantSettingsUpdateDTO(
            **settings_data.model_dump(exclude_unset=True)
        )

        restaurant = await restaurant_repo.update_restaurant(
            UUID(restaurant_id),
            {"settings": settings_dto.model_dump(exclude_unset=True)},
        )

        return RestaurantResponseSchema.model_validate(restaurant)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/{restaurant_code}", response_model=RestaurantResponseSchema)
async def get_restaurant_by_code(
    restaurant_code: str,
    supabase: Client = Depends(get_supabase),
):
    """Get restaurant information by code (public endpoint for QR codes)."""
    try:
        restaurant_repo = RestaurantRepositoryImpl(supabase)
        restaurant = await restaurant_repo.get_restaurant_by_code(restaurant_code)

        if not restaurant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found"
            )

        if not restaurant.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant is not active"
            )

        return RestaurantResponseSchema.model_validate(restaurant)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post(
    "/me/staff", response_model=StaffResponseSchema, status_code=status.HTTP_201_CREATED
)
async def create_staff_member(
    staff_data: StaffCreateSchema,
    current_user=Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
):
    """Create a new staff member."""
    try:
        # Get restaurant ID from user context
        restaurant_id = current_user.restaurant_id
        if not restaurant_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No restaurant associated with user",
            )

        # Check if user has permission to manage staff
        user_role = current_user.role
        if user_role not in ["owner", "manager"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
            )

        # Initialize repositories and use case
        staff_repo = RestaurantStaffRepositoryImpl(supabase)
        create_staff_use_case = CreateStaffUseCase(staff_repo)

        # Convert schema to DTO
        staff_dto = StaffCreateDTO(**staff_data.model_dump())

        # Execute use case
        staff = await create_staff_use_case.execute(
            staff_dto, UUID(restaurant_id), supabase
        )

        return StaffResponseSchema(
            id=staff.id,
            restaurant_id=staff.restaurant_id,
            user_id=staff.user_id,
            role=staff.role,
            permissions=staff.permissions,
            is_active=staff.is_active,
            created_at=staff.created_at,
            updated_at=staff.updated_at,
            email=staff_data.email,
            name=staff_data.name,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create staff: {str(e)}",
        )


@router.get("/me/staff", response_model=StaffListResponseSchema)
async def get_restaurant_staff(
    current_user=Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
):
    """Get all staff members for the restaurant."""
    try:
        # Get restaurant ID from user context
        restaurant_id = current_user.restaurant_id
        if not restaurant_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No restaurant associated with user",
            )

        # Get staff list
        staff_repo = RestaurantStaffRepositoryImpl(supabase)
        staff_list = await staff_repo.get_restaurant_staff(UUID(restaurant_id))

        staff_responses = []
        for staff in staff_list:
            # Get user info for each staff member
            try:
                user_response = supabase.auth.admin.get_user_by_id(str(staff.user_id))
                user_email = user_response.user.email if user_response.user else None
                user_name = (
                    user_response.user.user_metadata.get("name")
                    if user_response.user
                    else None
                )
            except:
                user_email = None
                user_name = None

            staff_responses.append(
                StaffResponseSchema(
                    id=staff.id,
                    restaurant_id=staff.restaurant_id,
                    user_id=staff.user_id,
                    role=staff.role,
                    permissions=staff.permissions,
                    is_active=staff.is_active,
                    created_at=staff.created_at,
                    updated_at=staff.updated_at,
                    email=user_email,
                    name=user_name,
                )
            )

        return StaffListResponseSchema(
            staff=staff_responses,
            total=len(staff_responses),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.put("/me/staff/{staff_id}", response_model=StaffResponseSchema)
async def update_staff_member(
    staff_id: UUID,
    update_data: StaffUpdateSchema,
    current_user=Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
):
    """Update a staff member."""
    try:
        # Get restaurant ID from user context
        restaurant_id = current_user.restaurant_id
        if not restaurant_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No restaurant associated with user",
            )

        # Check if user has permission to manage staff
        user_role = current_user.role
        if user_role not in ["owner", "manager"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
            )

        # Update staff
        staff_repo = RestaurantStaffRepositoryImpl(supabase)
        update_dto = StaffUpdateDTO(**update_data.model_dump(exclude_unset=True))

        staff = await staff_repo.update_staff(
            staff_id, update_dto.model_dump(exclude_unset=True)
        )

        # Get user info
        try:
            user_response = supabase.auth.admin.get_user_by_id(str(staff.user_id))
            user_email = user_response.user.email if user_response.user else None
            user_name = (
                user_response.user.user_metadata.get("name")
                if user_response.user
                else None
            )
        except:
            user_email = None
            user_name = None

        return StaffResponseSchema(
            id=staff.id,
            restaurant_id=staff.restaurant_id,
            user_id=staff.user_id,
            role=staff.role,
            permissions=staff.permissions,
            is_active=staff.is_active,
            created_at=staff.created_at,
            updated_at=staff.updated_at,
            email=user_email,
            name=user_name,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.delete("/me/staff/{staff_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_staff_member(
    staff_id: UUID,
    current_user=Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
):
    """Delete a staff member."""
    try:
        # Get restaurant ID from user context
        restaurant_id = current_user.restaurant_id
        if not restaurant_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No restaurant associated with user",
            )

        # Check if user has permission (only owners can delete staff)
        user_role = current_user.role
        if user_role != "owner":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only owners can delete staff",
            )

        # Delete staff
        staff_repo = RestaurantStaffRepositoryImpl(supabase)
        success = await staff_repo.delete_staff(staff_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Staff member not found"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post(
    "/me/verification/documents",
    status_code=status.HTTP_201_CREATED,
)
async def upload_business_verification_document(
    file: UploadFile,
    doc_type: str | None = None,
    current_user: UserContext = Depends(get_current_user),
    user_supabase: Client = Depends(get_user_supabase),
) -> dict:
    """Upload a business verification document to Supabase storage.

    Stores the file in the private 'business-verification' bucket under the user's
    namespace. Returns the storage path for later retrieval via signed URLs.

    Args:
        file: The uploaded file.
        doc_type: Optional document type label (e.g., 'gst', 'fssai', 'license').
        current_user: Authenticated user context.
        user_supabase: Supabase client authenticated as the current user (RLS).

    Returns:
        JSON with the stored file path and metadata.

    Raises:
        HTTPException: If upload fails or user has no restaurant context.
    """
    try:
        if not current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
            )
        # Build storage path: userId/uuid-filename
        import uuid

        safe_name = file.filename or "document"
        storage_path = f"{current_user.user_id}/{uuid.uuid4()}-{safe_name}"

        # Upload to Supabase Storage using user-authenticated client (RLS policies apply)
        bucket = user_supabase.storage.from_("business-verification")
        # Read file content into bytes
        content = await file.read()
        bucket.upload(
            storage_path,
            content,
            {
                "content-type": file.content_type or "application/octet-stream",
                "upsert": False,
                "cache-control": "3600",
            },
        )

        # Optionally persist minimal metadata in DB in future (out of scope here)
        return {
            "path": storage_path,
            "doc_type": doc_type,
            "content_type": file.content_type,
            "size": len(content),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}",
        )
