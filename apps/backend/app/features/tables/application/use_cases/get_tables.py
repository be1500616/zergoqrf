"""Get tables use case.

This module contains use cases for retrieving table information.
"""

from typing import List, Optional
from uuid import UUID

from ...domain.table_entities import Table, TableStatus
from ...domain.table_repos import ITableRepository
from ..table_dtos import TableDTO, TableOccupancyStatsDTO


class GetTablesUseCase:
    """Use case for retrieving tables."""
    
    def __init__(self, table_repository: ITableRepository):
        """Initialize the use case.
        
        Args:
            table_repository: The table repository instance.
        """
        self._table_repository = table_repository
    
    async def get_table_by_id(self, table_id: UUID) -> Optional[TableDTO]:
        """Get a table by ID.
        
        Args:
            table_id: The table ID.
            
        Returns:
            The table DTO if found, None otherwise.
        """
        table = await self._table_repository.get_table_by_id(table_id)
        return self._table_to_dto(table) if table else None
    
    async def get_tables_by_restaurant(self, restaurant_id: UUID) -> List[TableDTO]:
        """Get all tables for a restaurant.
        
        Args:
            restaurant_id: The restaurant ID.
            
        Returns:
            List of table DTOs.
        """
        tables = await self._table_repository.get_tables_by_restaurant(restaurant_id)
        return [self._table_to_dto(table) for table in tables]
    
    async def get_tables_by_floor(self, floor_id: UUID) -> List[TableDTO]:
        """Get all tables for a floor.
        
        Args:
            floor_id: The floor ID.
            
        Returns:
            List of table DTOs.
        """
        tables = await self._table_repository.get_tables_by_floor(floor_id)
        return [self._table_to_dto(table) for table in tables]
    
    async def get_tables_by_status(self, restaurant_id: UUID, status: TableStatus) -> List[TableDTO]:
        """Get tables by status.
        
        Args:
            restaurant_id: The restaurant ID.
            status: The table status.
            
        Returns:
            List of table DTOs with the specified status.
        """
        tables = await self._table_repository.get_tables_by_status(restaurant_id, status)
        return [self._table_to_dto(table) for table in tables]
    
    async def get_available_tables(self, restaurant_id: UUID, party_size: int) -> List[TableDTO]:
        """Get available tables that can accommodate a party.
        
        Args:
            restaurant_id: The restaurant ID.
            party_size: Number of people in the party.
            
        Returns:
            List of available table DTOs.
        """
        tables = await self._table_repository.get_available_tables(restaurant_id, party_size)
        return [self._table_to_dto(table) for table in tables]
    
    async def get_occupancy_stats(self, restaurant_id: UUID) -> TableOccupancyStatsDTO:
        """Get table occupancy statistics for a restaurant.
        
        Args:
            restaurant_id: The restaurant ID.
            
        Returns:
            Table occupancy statistics DTO.
        """
        all_tables = await self._table_repository.get_tables_by_restaurant(restaurant_id)
        active_tables = [table for table in all_tables if table.is_active]
        
        total_tables = len(active_tables)
        available_tables = len([t for t in active_tables if t.status == TableStatus.AVAILABLE])
        occupied_tables = len([t for t in active_tables if t.status == TableStatus.OCCUPIED])
        reserved_tables = len([t for t in active_tables if t.status == TableStatus.RESERVED])
        cleaning_tables = len([t for t in active_tables if t.status == TableStatus.CLEANING])
        maintenance_tables = len([t for t in active_tables if t.status == TableStatus.MAINTENANCE])
        
        # Calculate occupancy rate (occupied + reserved / total)
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
