"""Manage floor plan use case.

This module contains use cases for managing restaurant floor plans.
"""

from typing import List, Optional
from uuid import UUID

from ...domain.table_entities import Floor, Table
from ...domain.table_repos import IFloorRepository, ITableRepository
from ..table_dtos import (
    CreateFloorDTO,
    FloorDTO,
    FloorPlanDTO,
    TableDTO,
    TableOccupancyStatsDTO,
    UpdateFloorDTO,
)


class ManageFloorPlanUseCase:
    """Use case for managing floor plans."""
    
    def __init__(self, floor_repository: IFloorRepository, table_repository: ITableRepository):
        """Initialize the use case.
        
        Args:
            floor_repository: The floor repository instance.
            table_repository: The table repository instance.
        """
        self._floor_repository = floor_repository
        self._table_repository = table_repository
    
    async def create_floor(self, restaurant_id: UUID, create_floor_dto: CreateFloorDTO) -> FloorDTO:
        """Create a new floor.
        
        Args:
            restaurant_id: The restaurant ID.
            create_floor_dto: The create floor data.
            
        Returns:
            The created floor DTO.
            
        Raises:
            ValueError: If floor number already exists.
            Exception: If floor creation fails.
        """
        # Check if floor number already exists
        existing_floors = await self._floor_repository.get_floors_by_restaurant(restaurant_id)
        if any(floor.floor_number == create_floor_dto.floor_number for floor in existing_floors):
            raise ValueError(f"Floor number {create_floor_dto.floor_number} already exists")
        
        # Prepare floor data
        floor_data = {
            "restaurant_id": restaurant_id,
            "name": create_floor_dto.name,
            "description": create_floor_dto.description,
            "floor_number": create_floor_dto.floor_number,
            "layout_config": create_floor_dto.layout_config,
            "is_active": True,
        }
        
        # Create the floor
        floor = await self._floor_repository.create_floor(floor_data)
        
        return self._floor_to_dto(floor)
    
    async def get_floor_by_id(self, floor_id: UUID) -> Optional[FloorDTO]:
        """Get a floor by ID.
        
        Args:
            floor_id: The floor ID.
            
        Returns:
            The floor DTO if found, None otherwise.
        """
        floor = await self._floor_repository.get_floor_by_id(floor_id)
        return self._floor_to_dto(floor) if floor else None
    
    async def get_floors_by_restaurant(self, restaurant_id: UUID) -> List[FloorDTO]:
        """Get all floors for a restaurant.
        
        Args:
            restaurant_id: The restaurant ID.
            
        Returns:
            List of floor DTOs.
        """
        floors = await self._floor_repository.get_floors_by_restaurant(restaurant_id)
        return [self._floor_to_dto(floor) for floor in floors]
    
    async def get_floor_plan(self, floor_id: UUID) -> Optional[FloorPlanDTO]:
        """Get complete floor plan with tables and occupancy stats.
        
        Args:
            floor_id: The floor ID.
            
        Returns:
            The floor plan DTO if found, None otherwise.
        """
        floor = await self._floor_repository.get_floor_by_id(floor_id)
        if not floor:
            return None
        
        # Get tables for this floor
        tables = await self._table_repository.get_tables_by_floor(floor_id)
        table_dtos = [self._table_to_dto(table) for table in tables]
        
        # Calculate occupancy stats
        occupancy_stats = self._calculate_occupancy_stats(tables)
        
        return FloorPlanDTO(
            floor=self._floor_to_dto(floor),
            tables=table_dtos,
            occupancy_stats=occupancy_stats
        )
    
    async def update_floor(self, floor_id: UUID, update_floor_dto: UpdateFloorDTO) -> Optional[FloorDTO]:
        """Update floor information.
        
        Args:
            floor_id: The floor ID.
            update_floor_dto: The update floor data.
            
        Returns:
            The updated floor DTO if found, None otherwise.
        """
        # Prepare update data
        update_data = {}
        
        if update_floor_dto.name is not None:
            update_data["name"] = update_floor_dto.name
        
        if update_floor_dto.description is not None:
            update_data["description"] = update_floor_dto.description
        
        if update_floor_dto.is_active is not None:
            update_data["is_active"] = update_floor_dto.is_active
        
        if update_floor_dto.layout_config is not None:
            update_data["layout_config"] = update_floor_dto.layout_config
        
        # Update the floor
        updated_floor = await self._floor_repository.update_floor(floor_id, update_data)
        
        return self._floor_to_dto(updated_floor) if updated_floor else None
    
    async def delete_floor(self, floor_id: UUID) -> bool:
        """Delete a floor.
        
        Args:
            floor_id: The floor ID.
            
        Returns:
            True if deletion was successful, False otherwise.
            
        Raises:
            ValueError: If floor has tables assigned to it.
        """
        # Check if floor has tables
        tables = await self._table_repository.get_tables_by_floor(floor_id)
        if tables:
            raise ValueError("Cannot delete floor with tables assigned to it")
        
        return await self._floor_repository.delete_floor(floor_id)
    
    def _floor_to_dto(self, floor: Floor) -> FloorDTO:
        """Convert floor entity to DTO.
        
        Args:
            floor: The floor entity.
            
        Returns:
            The floor DTO.
        """
        return FloorDTO(
            id=floor.id,
            restaurant_id=floor.restaurant_id,
            name=floor.name,
            description=floor.description,
            floor_number=floor.floor_number,
            is_active=floor.is_active,
            layout_config=floor.layout_config,
            created_at=floor.created_at,
            updated_at=floor.updated_at,
        )
    
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
    
    def _calculate_occupancy_stats(self, tables: List[Table]) -> TableOccupancyStatsDTO:
        """Calculate occupancy statistics for tables.
        
        Args:
            tables: List of table entities.
            
        Returns:
            Table occupancy statistics DTO.
        """
        active_tables = [table for table in tables if table.is_active]
        
        total_tables = len(active_tables)
        available_tables = len([t for t in active_tables if t.status.value == "available"])
        occupied_tables = len([t for t in active_tables if t.status.value == "occupied"])
        reserved_tables = len([t for t in active_tables if t.status.value == "reserved"])
        cleaning_tables = len([t for t in active_tables if t.status.value == "cleaning"])
        maintenance_tables = len([t for t in active_tables if t.status.value == "maintenance"])
        
        # Calculate occupancy rate
        occupancy_rate = 0.0
        if total_tables > 0:
            occupancy_rate = ((occupied_tables + reserved_tables) / total_tables) * 100
        
        return TableOccupancyStatsDTO(
            total_tables=total_tables,
            available_tables=available_tables,
            occupied_tables=occupied_tables,
            reserved_tables=reserved_tables,
            cleaning_tables=cleaning_tables,
            maintenance_tables=maintenance_tables,
            occupancy_rate=round(occupancy_rate, 2)
        )
