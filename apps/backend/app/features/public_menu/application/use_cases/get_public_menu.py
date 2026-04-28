"""Get public menu use case.

This module contains the use case for retrieving public menu data.
"""

from typing import Optional
from uuid import UUID

from ..public_menu_dtos import PublicMenuStructureDTO, PublicRestaurantBrandingDTO, PublicMenuCategoryDTO, PublicMenuItemDTO
from ...domain.public_menu_repos import IPublicMenuRepository


class GetPublicMenuUseCase:
    """Use case for retrieving public menu structure."""
    
    def __init__(self, public_menu_repository: IPublicMenuRepository):
        """Initialize the use case.
        
        Args:
            public_menu_repository: Public menu repository instance.
        """
        self._repository = public_menu_repository
    
    async def execute_by_code(self, restaurant_code: str) -> Optional[PublicMenuStructureDTO]:
        """Execute the use case to get menu by restaurant code.
        
        Args:
            restaurant_code: Restaurant code from QR code URL.
            
        Returns:
            Public menu structure DTO or None if not found.
            
        Raises:
            Exception: If menu retrieval fails.
        """
        try:
            # Get restaurant by code
            restaurant = await self._repository.get_restaurant_by_code(restaurant_code)
            if not restaurant:
                return None

            # Get complete menu structure
            menu_structure = await self._repository.get_public_menu_structure(restaurant.id)
            if not menu_structure:
                return None
            
            # Convert to DTO
            return PublicMenuStructureDTO(
                restaurant=PublicRestaurantBrandingDTO.model_validate(menu_structure.restaurant),
                categories=[
                    PublicMenuCategoryDTO.model_validate(category) 
                    for category in menu_structure.categories
                ],
                items=[
                    PublicMenuItemDTO.model_validate(item) 
                    for item in menu_structure.items
                ],
                last_updated=menu_structure.last_updated,
            )
            
        except Exception as e:
            raise Exception(f"Failed to retrieve public menu: {str(e)}")
    
    async def execute_by_id(self, restaurant_id: UUID) -> Optional[PublicMenuStructureDTO]:
        """Execute the use case to get menu by restaurant ID.
        
        Args:
            restaurant_id: Restaurant UUID.
            
        Returns:
            Public menu structure DTO or None if not found.
            
        Raises:
            Exception: If menu retrieval fails.
        """
        try:
            # Get complete menu structure
            menu_structure = await self._repository.get_public_menu_structure(restaurant_id)
            if not menu_structure:
                return None
            
            # Convert to DTO
            return PublicMenuStructureDTO(
                restaurant=PublicRestaurantBrandingDTO.model_validate(menu_structure.restaurant),
                categories=[
                    PublicMenuCategoryDTO.model_validate(category) 
                    for category in menu_structure.categories
                ],
                items=[
                    PublicMenuItemDTO.model_validate(item) 
                    for item in menu_structure.items
                ],
                last_updated=menu_structure.last_updated,
            )
            
        except Exception as e:
            raise Exception(f"Failed to retrieve public menu: {str(e)}")
    
    async def get_restaurant_branding(self, restaurant_code: str) -> Optional[PublicRestaurantBrandingDTO]:
        """Get restaurant branding information only.
        
        Args:
            restaurant_code: Restaurant code from QR code URL.
            
        Returns:
            Restaurant branding DTO or None if not found.
        """
        try:
            restaurant = await self._repository.get_restaurant_by_code(restaurant_code)
            if not restaurant:
                return None
            
            return PublicRestaurantBrandingDTO.model_validate(restaurant)
            
        except Exception as e:
            raise Exception(f"Failed to retrieve restaurant branding: {str(e)}")
