"""Menu API router.

This module contains FastAPI routes for menu management.
"""

from typing import List, Optional
from uuid import UUID

from app.common.supabase_client import get_supabase
from app.features.auth.presentation.supabase_dependencies import (
    UserContext,
    get_current_user,
)
from app.features.menu.application.menu_dtos import (
    MenuCategoryCreateDTO,
    MenuCategoryUpdateDTO,
    MenuItemCreateDTO,
    MenuItemUpdateDTO,
    MenuPublishDTO,
    MenuSearchDTO,
    MenuVersionCreateDTO,
)
from app.features.menu.infrastructure.menu_repos_impl import (
    MenuCategoryRepositoryImpl,
    MenuItemRepositoryImpl,
    MenuVersionRepositoryImpl,
)
from app.features.menu.presentation.menu_schemas import (
    CategoryReorderSchema,
    MenuAnalyticsResponseSchema,
    MenuCategoryCreateSchema,
    MenuCategoryResponseSchema,
    MenuCategoryUpdateSchema,
    MenuItemBulkUpdateSchema,
    MenuItemCreateSchema,
    MenuItemResponseSchema,
    MenuItemUpdateSchema,
    MenuPublishSchema,
    MenuSearchSchema,
    MenuStructureResponseSchema,
    MenuVersionCreateSchema,
    MenuVersionResponseSchema,
)
from fastapi import APIRouter, Depends, HTTPException, Query, status
from supabase import Client

router = APIRouter()


# Category Management Endpoints


@router.post(
    "/categories",
    response_model=MenuCategoryResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_category(
    category_data: MenuCategoryCreateSchema,
    current_user: UserContext = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
):
    """Create a new menu category."""
    try:
        # Get restaurant ID from user context
        restaurant_id = current_user.restaurant_id
        if not restaurant_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No restaurant associated with user",
            )

        # Initialize repository
        category_repo = MenuCategoryRepositoryImpl(supabase)

        # Convert schema to DTO
        category_dto = MenuCategoryCreateDTO(**category_data.model_dump())
        category_dict = category_dto.model_dump()
        category_dict["restaurant_id"] = UUID(restaurant_id)

        # Create category
        category = await category_repo.create_category(category_dict)

        return MenuCategoryResponseSchema.model_validate(category)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create category: {str(e)}",
        )


@router.get("/categories", response_model=List[MenuCategoryResponseSchema])
async def get_categories(
    include_inactive: bool = Query(
        default=False, description="Include inactive categories"
    ),
    current_user: UserContext = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
):
    """Get all categories for the restaurant."""
    try:
        # Get restaurant ID from user context
        restaurant_id = current_user.restaurant_id
        if not restaurant_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No restaurant associated with user",
            )

        # Initialize repository
        category_repo = MenuCategoryRepositoryImpl(supabase)

        # Get categories
        categories = await category_repo.get_restaurant_categories(
            UUID(restaurant_id), include_inactive
        )

        return [
            MenuCategoryResponseSchema.model_validate(category)
            for category in categories
        ]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/categories/hierarchy", response_model=List[MenuCategoryResponseSchema])
async def get_category_hierarchy(
    current_user: UserContext = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
):
    """Get hierarchical category structure."""
    try:
        # Get restaurant ID from user context
        restaurant_id = current_user.restaurant_id
        if not restaurant_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No restaurant associated with user",
            )

        # Initialize repository
        category_repo = MenuCategoryRepositoryImpl(supabase)

        # Get hierarchy
        categories = await category_repo.get_category_hierarchy(UUID(restaurant_id))

        return [
            MenuCategoryResponseSchema.model_validate(category)
            for category in categories
        ]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.put("/categories/{category_id}", response_model=MenuCategoryResponseSchema)
async def update_category(
    category_id: UUID,
    update_data: MenuCategoryUpdateSchema,
    current_user: UserContext = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
):
    """Update a menu category."""
    try:
        # Initialize repository
        category_repo = MenuCategoryRepositoryImpl(supabase)

        # Convert schema to DTO
        update_dto = MenuCategoryUpdateDTO(**update_data.model_dump(exclude_unset=True))

        # Update category
        category = await category_repo.update_category(
            category_id, update_dto.model_dump(exclude_unset=True)
        )

        return MenuCategoryResponseSchema.model_validate(category)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: UUID,
    current_user: UserContext = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
):
    """Delete a menu category."""
    try:
        # Initialize repository
        category_repo = MenuCategoryRepositoryImpl(supabase)

        # Delete category
        success = await category_repo.delete_category(category_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/categories/reorder", status_code=status.HTTP_200_OK)
async def reorder_categories(
    reorder_data: CategoryReorderSchema,
    current_user: UserContext = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
):
    """Reorder menu categories."""
    try:
        # Initialize repository
        category_repo = MenuCategoryRepositoryImpl(supabase)

        # Reorder categories
        success = await category_repo.reorder_categories(reorder_data.category_orders)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to reorder categories",
            )

        return {"message": "Categories reordered successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


# Menu Item Management Endpoints


@router.post(
    "/items", response_model=MenuItemResponseSchema, status_code=status.HTTP_201_CREATED
)
async def create_menu_item(
    item_data: MenuItemCreateSchema,
    current_user: UserContext = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
):
    """Create a new menu item."""
    try:
        # Get restaurant ID from user context
        restaurant_id = current_user.restaurant_id
        if not restaurant_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No restaurant associated with user",
            )

        # Initialize repository
        item_repo = MenuItemRepositoryImpl(supabase)

        # Convert schema to DTO
        item_dto = MenuItemCreateDTO(**item_data.model_dump())
        item_dict = item_dto.model_dump()
        item_dict["restaurant_id"] = UUID(restaurant_id)

        # Create item
        item = await item_repo.create_item(item_dict)

        return MenuItemResponseSchema.model_validate(item)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create menu item: {str(e)}",
        )


@router.get("/items", response_model=List[MenuItemResponseSchema])
async def get_menu_items(
    category_id: Optional[UUID] = Query(default=None, description="Filter by category"),
    include_inactive: bool = Query(default=False, description="Include inactive items"),
    current_user: UserContext = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
):
    """Get menu items for the restaurant."""
    try:
        # Get restaurant ID from user context
        restaurant_id = current_user.restaurant_id
        if not restaurant_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No restaurant associated with user",
            )

        # Initialize repository
        item_repo = MenuItemRepositoryImpl(supabase)

        # Get items
        if category_id:
            items = await item_repo.get_category_items(category_id, include_inactive)
        else:
            items = await item_repo.get_restaurant_items(
                UUID(restaurant_id), include_inactive
            )

        return [MenuItemResponseSchema.model_validate(item) for item in items]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/items/{item_id}", response_model=MenuItemResponseSchema)
async def get_menu_item(
    item_id: UUID,
    current_user: UserContext = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
):
    """Get a specific menu item."""
    try:
        # Initialize repository
        item_repo = MenuItemRepositoryImpl(supabase)

        # Get item
        item = await item_repo.get_item_by_id(item_id)

        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found"
            )

        return MenuItemResponseSchema.model_validate(item)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.put("/items/{item_id}", response_model=MenuItemResponseSchema)
async def update_menu_item(
    item_id: UUID,
    update_data: MenuItemUpdateSchema,
    current_user: UserContext = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
):
    """Update a menu item."""
    try:
        # Initialize repository
        item_repo = MenuItemRepositoryImpl(supabase)

        # Convert schema to DTO
        update_dto = MenuItemUpdateDTO(**update_data.model_dump(exclude_unset=True))

        # Update item
        item = await item_repo.update_item(
            item_id, update_dto.model_dump(exclude_unset=True)
        )

        return MenuItemResponseSchema.model_validate(item)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_menu_item(
    item_id: UUID,
    current_user: UserContext = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
):
    """Delete a menu item."""
    try:
        # Initialize repository
        item_repo = MenuItemRepositoryImpl(supabase)

        # Delete item
        success = await item_repo.delete_item(item_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/items/search", response_model=List[MenuItemResponseSchema])
async def search_menu_items(
    search_data: MenuSearchSchema,
    current_user: UserContext = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
):
    """Search menu items."""
    try:
        # Get restaurant ID from user context
        restaurant_id = current_user.restaurant_id
        if not restaurant_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No restaurant associated with user",
            )

        # Initialize repository
        item_repo = MenuItemRepositoryImpl(supabase)

        # Convert schema to DTO
        search_dto = MenuSearchDTO(**search_data.model_dump())

        # Search items
        items = await item_repo.search_items(
            UUID(restaurant_id),
            search_dto.query or "",
            search_dto.model_dump(exclude_unset=True),
        )

        return [MenuItemResponseSchema.model_validate(item) for item in items]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


# Menu Versioning and Publishing Endpoints


@router.post(
    "/versions",
    response_model=MenuVersionResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_menu_version(
    version_data: MenuVersionCreateSchema,
    current_user: UserContext = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
):
    """Create a new menu version."""
    try:
        # Get restaurant ID from user context
        restaurant_id = current_user.restaurant_id
        if not restaurant_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No restaurant associated with user",
            )

        # Initialize repository
        version_repo = MenuVersionRepositoryImpl(supabase)

        # Convert schema to DTO
        version_dto = MenuVersionCreateDTO(**version_data.model_dump())
        version_dict = version_dto.model_dump()
        version_dict["restaurant_id"] = UUID(restaurant_id)
        version_dict["created_by"] = UUID(current_user.id)

        # Create version
        version = await version_repo.create_version(version_dict)

        return MenuVersionResponseSchema.model_validate(version)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create menu version: {str(e)}",
        )


@router.get("/structure", response_model=MenuStructureResponseSchema)
async def get_menu_structure(
    version_id: Optional[UUID] = Query(
        default=None, description="Specific version ID (defaults to current live)"
    ),
    current_user: UserContext = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
):
    """Get complete menu structure with categories and items."""
    try:
        # Get restaurant ID from user context
        restaurant_id = current_user.restaurant_id
        if not restaurant_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No restaurant associated with user",
            )

        # Initialize repositories
        category_repo = MenuCategoryRepositoryImpl(supabase)
        item_repo = MenuItemRepositoryImpl(supabase)
        version_repo = MenuVersionRepositoryImpl(supabase)

        # Get categories and items
        categories = await category_repo.get_category_hierarchy(UUID(restaurant_id))
        items = await item_repo.get_restaurant_items(UUID(restaurant_id))

        # Get version info
        version_info = None
        if version_id:
            version_info = await version_repo.get_version_by_id(version_id)
        else:
            version_info = await version_repo.get_current_live_version(
                UUID(restaurant_id)
            )

        return MenuStructureResponseSchema(
            categories=[
                MenuCategoryResponseSchema.model_validate(cat) for cat in categories
            ],
            items=[MenuItemResponseSchema.model_validate(item) for item in items],
            version_info=(
                MenuVersionResponseSchema.model_validate(version_info)
                if version_info
                else None
            ),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
