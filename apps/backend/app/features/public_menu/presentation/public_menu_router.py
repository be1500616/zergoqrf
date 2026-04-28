"""Public menu FastAPI router.

This module contains the FastAPI router for public menu endpoints.
No authentication required for these endpoints.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from supabase import Client

from app.common.supabase_client import get_supabase

from ..application.use_cases.get_public_menu import GetPublicMenuUseCase
from ..application.use_cases.search_menu_items import SearchMenuItemsUseCase
from ..application.public_menu_dtos import PublicMenuSearchRequestDTO
from ..infrastructure.public_menu_repos_impl import PublicMenuRepositoryImpl
from .public_menu_schemas import (
    PublicMenuStructureSchema,
    PublicRestaurantBrandingSchema,
    PublicMenuCategorySchema,
    PublicMenuItemSchema,
    PublicMenuSearchRequestSchema,
    PublicMenuSearchResponseSchema,
    PublicMenuCategoryItemsSchema,
    ErrorResponseSchema,
)

router = APIRouter(prefix="/public/menu", tags=["Public Menu"])


# Dependency injection functions
def get_public_menu_repository(
    supabase: Client = Depends(get_supabase),
) -> PublicMenuRepositoryImpl:
    """Get public menu repository instance."""
    return PublicMenuRepositoryImpl(supabase)


def get_public_menu_use_case(
    repository: PublicMenuRepositoryImpl = Depends(get_public_menu_repository),
) -> GetPublicMenuUseCase:
    """Get public menu use case instance."""
    return GetPublicMenuUseCase(repository)


def get_search_menu_use_case(
    repository: PublicMenuRepositoryImpl = Depends(get_public_menu_repository),
) -> SearchMenuItemsUseCase:
    """Get search menu use case instance."""
    return SearchMenuItemsUseCase(repository)


# Public Menu Endpoints (No Authentication Required)


@router.get(
    "/restaurant/{restaurant_code}", response_model=PublicRestaurantBrandingSchema
)
async def get_restaurant_branding(
    restaurant_code: str,
    use_case: GetPublicMenuUseCase = Depends(get_public_menu_use_case),
):
    """Get restaurant branding information by code.

    This endpoint provides restaurant branding data for PWA theming.
    No authentication required.

    Args:
        restaurant_code: Restaurant code from QR code URL.
        use_case: Get public menu use case.

    Returns:
        Restaurant branding information.

    Raises:
        HTTPException: If restaurant not found.
    """
    try:
        branding = await use_case.get_restaurant_branding(restaurant_code)

        if not branding:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found"
            )

        return PublicRestaurantBrandingSchema.model_validate(branding)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve restaurant branding: {str(e)}",
        )


@router.get("/{restaurant_code}", response_model=PublicMenuStructureSchema)
async def get_public_menu(
    restaurant_code: str,
    use_case: GetPublicMenuUseCase = Depends(get_public_menu_use_case),
):
    """Get complete public menu structure by restaurant code.

    This is the main endpoint for PWA menu loading.
    No authentication required.

    Args:
        restaurant_code: Restaurant code from QR code URL.
        use_case: Get public menu use case.

    Returns:
        Complete menu structure with restaurant branding, categories, and items.

    Raises:
        HTTPException: If menu not found.
    """
    try:
        menu_structure = await use_case.execute_by_code(restaurant_code)

        if not menu_structure:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Menu not found for this restaurant",
            )

        return PublicMenuStructureSchema.model_validate(menu_structure)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve menu: {str(e)}",
        )


@router.get(
    "/{restaurant_code}/categories", response_model=List[PublicMenuCategorySchema]
)
async def get_menu_categories(
    restaurant_code: str,
    repository: PublicMenuRepositoryImpl = Depends(get_public_menu_repository),
):
    """Get menu categories for a restaurant.

    Args:
        restaurant_code: Restaurant code from QR code URL.
        repository: Public menu repository.

    Returns:
        List of menu categories.

    Raises:
        HTTPException: If restaurant not found.
    """
    try:
        # Get restaurant by code
        restaurant = await repository.get_restaurant_by_code(restaurant_code)
        if not restaurant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found"
            )

        # Get categories
        categories = await repository.get_menu_categories(restaurant.id)

        return [
            PublicMenuCategorySchema.model_validate(category) for category in categories
        ]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve categories: {str(e)}",
        )


@router.get(
    "/{restaurant_code}/categories/{category_id}/items",
    response_model=PublicMenuCategoryItemsSchema,
)
async def get_category_items(
    restaurant_code: str,
    category_id: UUID,
    repository: PublicMenuRepositoryImpl = Depends(get_public_menu_repository),
):
    """Get menu items for a specific category.

    Args:
        restaurant_code: Restaurant code from QR code URL.
        category_id: Category UUID.
        repository: Public menu repository.

    Returns:
        Category information with its menu items.

    Raises:
        HTTPException: If restaurant or category not found.
    """
    try:
        # Get restaurant by code
        restaurant = await repository.get_restaurant_by_code(restaurant_code)
        if not restaurant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found"
            )

        # Get category
        categories = await repository.get_menu_categories(restaurant.id)
        category = next((c for c in categories if c.id == category_id), None)

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
            )

        # Get items
        items = await repository.get_menu_items_by_category(restaurant.id, category_id)

        return PublicMenuCategoryItemsSchema(
            category=PublicMenuCategorySchema.model_validate(category),
            items=[PublicMenuItemSchema.model_validate(item) for item in items],
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve category items: {str(e)}",
        )


@router.get("/{restaurant_code}/search", response_model=PublicMenuSearchResponseSchema)
async def search_menu_items(
    restaurant_code: str,
    query: str = Query(..., min_length=1, max_length=100, description="Search query"),
    limit: int = Query(
        default=50, ge=1, le=100, description="Maximum number of results"
    ),
    repository: PublicMenuRepositoryImpl = Depends(get_public_menu_repository),
    use_case: SearchMenuItemsUseCase = Depends(get_search_menu_use_case),
):
    """Search menu items by name or description.

    Args:
        restaurant_code: Restaurant code from QR code URL.
        query: Search query string.
        limit: Maximum number of results.
        repository: Public menu repository.
        use_case: Search menu use case.

    Returns:
        Search results with matching items and categories.

    Raises:
        HTTPException: If restaurant not found.
    """
    try:
        # Get restaurant by code
        restaurant = await repository.get_restaurant_by_code(restaurant_code)
        if not restaurant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found"
            )

        # Perform search
        search_request = PublicMenuSearchRequestDTO(query=query, limit=limit)
        search_result = await use_case.execute(restaurant.id, search_request)

        return PublicMenuSearchResponseSchema.model_validate(search_result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search menu items: {str(e)}",
        )


@router.get("/{restaurant_code}/featured", response_model=List[PublicMenuItemSchema])
async def get_featured_items(
    restaurant_code: str,
    limit: int = Query(
        default=10, ge=1, le=20, description="Maximum number of featured items"
    ),
    repository: PublicMenuRepositoryImpl = Depends(get_public_menu_repository),
    use_case: SearchMenuItemsUseCase = Depends(get_search_menu_use_case),
):
    """Get featured menu items for a restaurant.

    Args:
        restaurant_code: Restaurant code from QR code URL.
        limit: Maximum number of featured items.
        repository: Public menu repository.
        use_case: Search menu use case.

    Returns:
        List of featured menu items.

    Raises:
        HTTPException: If restaurant not found.
    """
    try:
        # Get restaurant by code
        restaurant = await repository.get_restaurant_by_code(restaurant_code)
        if not restaurant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found"
            )

        # Get featured items
        featured_items = await use_case.get_featured_items(restaurant.id, limit)

        return [PublicMenuItemSchema.model_validate(item) for item in featured_items]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve featured items: {str(e)}",
        )
