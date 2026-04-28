"""Create table use case.

This module contains the use case for creating new tables.
"""

import secrets
from uuid import UUID

from ...domain.table_entities import QRCodeData, Table
from ...domain.table_repos import ITableRepository
from ..table_dtos import CreateTableDTO, TableDTO


class CreateTableUseCase:
    """Use case for creating a new table."""
    
    def __init__(self, table_repository: ITableRepository):
        """Initialize the use case.
        
        Args:
            table_repository: The table repository instance.
        """
        self._table_repository = table_repository
    
    async def execute(self, restaurant_id: UUID, create_table_dto: CreateTableDTO) -> TableDTO:
        """Execute the create table use case.
        
        Args:
            restaurant_id: The restaurant ID.
            create_table_dto: The create table data.
            
        Returns:
            The created table DTO.
            
        Raises:
            ValueError: If table number already exists or validation fails.
            Exception: If table creation fails.
        """
        # Check if table number already exists
        existing_table = await self._table_repository.get_table_by_number(
            restaurant_id, create_table_dto.table_number
        )
        if existing_table:
            raise ValueError(f"Table number '{create_table_dto.table_number}' already exists")
        
        # Validate max_party_size
        max_party_size = create_table_dto.max_party_size or create_table_dto.capacity
        if max_party_size < create_table_dto.min_party_size:
            raise ValueError("max_party_size must be >= min_party_size")
        
        # Generate QR code token
        qr_token = f"table_{restaurant_id}_{create_table_dto.table_number}_{secrets.token_urlsafe(8)}"
        qr_code_data = QRCodeData(
            token=qr_token,
            data={
                "restaurant_id": str(restaurant_id),
                "table_number": create_table_dto.table_number,
                "table_id": None  # Will be set after creation
            }
        )
        
        # Prepare table data
        table_data = {
            "restaurant_id": restaurant_id,
            "floor_id": create_table_dto.floor_id,
            "table_number": create_table_dto.table_number,
            "capacity": create_table_dto.capacity,
            "shape": create_table_dto.shape.value,
            "category": create_table_dto.category.value,
            "position": create_table_dto.position.dict() if create_table_dto.position else None,
            "dimensions": create_table_dto.dimensions.dict() if create_table_dto.dimensions else None,
            "rotation": create_table_dto.rotation,
            "special_requirements": create_table_dto.special_requirements,
            "is_accessible": create_table_dto.is_accessible,
            "has_power_outlet": create_table_dto.has_power_outlet,
            "has_window_view": create_table_dto.has_window_view,
            "min_party_size": create_table_dto.min_party_size,
            "max_party_size": max_party_size,
            "qr_token": qr_token,
            "qr_code_data": qr_code_data.dict(),
            "notes": create_table_dto.notes,
            "is_active": True,
        }
        
        # Create the table
        table = await self._table_repository.create_table(table_data)
        
        # Update QR code data with table ID
        if table.qr_code_data:
            table.qr_code_data.data["table_id"] = str(table.id)
            await self._table_repository.update_table(
                table.id, 
                {"qr_code_data": table.qr_code_data.dict()}
            )
        
        # Convert to DTO
        return self._table_to_dto(table)
    
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
