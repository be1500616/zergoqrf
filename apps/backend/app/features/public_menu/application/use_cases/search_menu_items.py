"""Search menu items use case.

This module contains the use case for searching public menu items.
"""

from typing import List
from uuid import UUID

from ..public_menu_dtos import PublicMenuSearchRequestDTO, PublicMenuSearchResultDTO, PublicMenuItemDTO
from ...domain.public_menu_repos import IPublicMenuRepository


class SearchMenuItemsUseCase:
    """Use case for searching menu items."""
    
    def __init__(self, public_menu_repository: IPublicMenuRepository):
        """Initialize the use case.
        
        Args:
            public_menu_repository: Public menu repository instance.
        """
        self._repository = public_menu_repository
    
    async def execute(
        self, 
        restaurant_id: UUID, 
        search_request: PublicMenuSearchRequestDTO
    ) -> PublicMenuSearchResultDTO:
        """Execute the search use case.
        
        Args:
            restaurant_id: Restaurant UUID.
            search_request: Search request parameters.
            
        Returns:
            Search results DTO.
            
        Raises:
            Exception: If search fails.
        """
        try:
            # Perform search
            search_result = await self._repository.search_menu_items(
                restaurant_id=restaurant_id,
                query=search_request.query,
                limit=search_request.limit
            )
            
            # Convert to DTO
            return PublicMenuSearchResultDTO(
                items=[
                    PublicMenuItemDTO.model_validate(item) 
                    for item in search_result.items
                ],
                total_count=search_result.total_count,
                search_query=search_result.search_query,
                categories_found=[
                    PublicMenuCategoryDTO.model_validate(category) 
                    for category in search_result.categories_found
                ],
            )
            
        except Exception as e:
            raise Exception(f"Failed to search menu items: {str(e)}")
    
    async def get_featured_items(self, restaurant_id: UUID, limit: int = 10) -> List[PublicMenuItemDTO]:
        """Get featured menu items.
        
        Args:
            restaurant_id: Restaurant UUID.
            limit: Maximum number of featured items.
            
        Returns:
            List of featured menu item DTOs.
            
        Raises:
            Exception: If retrieval fails.
        """
        try:
            featured_items = await self._repository.get_featured_items(restaurant_id, limit)
            
            return [
                PublicMenuItemDTO.model_validate(item) 
                for item in featured_items
            ]
            
        except Exception as e:
            raise Exception(f"Failed to get featured items: {str(e)}")
