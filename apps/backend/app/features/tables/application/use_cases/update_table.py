"""Update table use case.

This module contains the use case for updating table information.
"""

from typing import Optional
from uuid import UUID

from ...domain.table_entities import Table
from ...domain.table_repos import ITableRepository
from ..table_dtos import TableDTO, UpdateTableDTO


class UpdateTableUseCase:
    """Use case for updating table information."""
    
    def __init__(self, table_repository: ITableRepository):
        """Initialize the use case.
        
        Args:
            table_repository: The table repository instance.
        """
        self._table_repository = table_repository
    
    async def execute(self, table_id: UUID, update_table_dto: UpdateTableDTO) -> Optional[TableDTO]:
        """Execute the update table use case.
        
        Args:
            table_id: The table ID.
            update_table_dto: The update table data.
            
        Returns:
            The updated table DTO if found, None otherwise.
            
        Raises:
            ValueError: If table number already exists or validation fails.
        """
        # Get the existing table
        existing_table = await self._table_repository.get_table_by_id(table_id)
        if not existing_table:
            return None
        
        # Check if table number is being changed and already exists
        if (update_table_dto.table_number and 
            update_table_dto.table_number != existing_table.table_number):
            
            existing_with_number = await self._table_repository.get_table_by_number(
                existing_table.restaurant_id, update_table_dto.table_number
            )
            if existing_with_number:
                raise ValueError(f"Table number '{update_table_dto.table_number}' already exists")
        
        # Prepare update data
        update_data = {}
        
        if update_table_dto.floor_id is not None:
            update_data["floor_id"] = update_table_dto.floor_id
        
        if update_table_dto.table_number is not None:
            update_data["table_number"] = update_table_dto.table_number
        
        if update_table_dto.capacity is not None:
            update_data["capacity"] = update_table_dto.capacity
        
        if update_table_dto.shape is not None:
            update_data["shape"] = update_table_dto.shape.value
        
        if update_table_dto.category is not None:
            update_data["category"] = update_table_dto.category.value
        
        if update_table_dto.position is not None:
            update_data["position"] = update_table_dto.position.dict()
        
        if update_table_dto.dimensions is not None:
            update_data["dimensions"] = update_table_dto.dimensions.dict()
        
        if update_table_dto.rotation is not None:
            update_data["rotation"] = update_table_dto.rotation
        
        if update_table_dto.special_requirements is not None:
            update_data["special_requirements"] = update_table_dto.special_requirements
        
        if update_table_dto.is_accessible is not None:
            update_data["is_accessible"] = update_table_dto.is_accessible
        
        if update_table_dto.has_power_outlet is not None:
            update_data["has_power_outlet"] = update_table_dto.has_power_outlet
        
        if update_table_dto.has_window_view is not None:
            update_data["has_window_view"] = update_table_dto.has_window_view
        
        if update_table_dto.min_party_size is not None:
            update_data["min_party_size"] = update_table_dto.min_party_size
        
        if update_table_dto.max_party_size is not None:
            update_data["max_party_size"] = update_table_dto.max_party_size
        
        if update_table_dto.notes is not None:
            update_data["notes"] = update_table_dto.notes
        
        if update_table_dto.is_active is not None:
            update_data["is_active"] = update_table_dto.is_active
        
        # Validate party size constraints
        min_party_size = update_table_dto.min_party_size or existing_table.min_party_size
        max_party_size = update_table_dto.max_party_size or existing_table.max_party_size
        
        if max_party_size and max_party_size < min_party_size:
            raise ValueError("max_party_size must be >= min_party_size")
        
        # Update the table
        updated_table = await self._table_repository.update_table(table_id, update_data)
        
        return self._table_to_dto(updated_table) if updated_table else None
    
    def _table_to_dto(self, table: Table) -> TableDTO:
        """Convert table entity to DTO.
        
        Args:
            table: The table entity.
            
        Returns:
            The table DTO.
        """
        return TableDTO(
            id=table.id,
            restaurant_id=table.restaurant_id,
            floor_id=table.floor_id,
            table_number=table.table_number,
            capacity=table.capacity,
            status=table.status,
            shape=table.shape,
            category=table.category,
            position=table.position,
            dimensions=table.dimensions,
            rotation=table.rotation,
            special_requirements=table.special_requirements,
            is_accessible=table.is_accessible,
            has_power_outlet=table.has_power_outlet,
            has_window_view=table.has_window_view,
            min_party_size=table.min_party_size,
            max_party_size=table.max_party_size,
            qr_code_data=table.qr_code_data,
            last_cleaned_at=table.last_cleaned_at,
            last_occupied_at=table.last_occupied_at,
            notes=table.notes,
            is_active=table.is_active,
            created_at=table.created_at,
            updated_at=table.updated_at,
        )
