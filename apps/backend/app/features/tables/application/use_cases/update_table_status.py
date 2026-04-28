"""Update table status use case.

This module contains the use case for updating table status.
"""

from datetime import datetime
from uuid import UUID

from ...domain.table_entities import TableStatus
from ...domain.table_repos import ITableRepository


class UpdateTableStatusUseCase:
    """Use case for updating table status."""
    
    def __init__(self, table_repository: ITableRepository):
        """Initialize the use case.
        
        Args:
            table_repository: The table repository instance.
        """
        self._table_repository = table_repository
    
    async def execute(self, table_id: UUID, status: TableStatus) -> bool:
        """Execute the update table status use case.
        
        Args:
            table_id: The table ID.
            status: The new table status.
            
        Returns:
            True if update was successful, False otherwise.
        """
        # Get the existing table to validate
        existing_table = await self._table_repository.get_table_by_id(table_id)
        if not existing_table:
            return False
        
        # Prepare update data based on status
        update_data = {"status": status.value}
        
        # Update timestamps based on status
        now = datetime.utcnow()
        
        if status == TableStatus.OCCUPIED:
            update_data["last_occupied_at"] = now
        elif status == TableStatus.CLEANING:
            update_data["last_cleaned_at"] = now
        
        # Update the table
        updated_table = await self._table_repository.update_table(table_id, update_data)
        
        return updated_table is not None
    
    async def mark_table_available(self, table_id: UUID) -> bool:
        """Mark a table as available.
        
        Args:
            table_id: The table ID.
            
        Returns:
            True if update was successful, False otherwise.
        """
        return await self.execute(table_id, TableStatus.AVAILABLE)
    
    async def mark_table_occupied(self, table_id: UUID) -> bool:
        """Mark a table as occupied.
        
        Args:
            table_id: The table ID.
            
        Returns:
            True if update was successful, False otherwise.
        """
        return await self.execute(table_id, TableStatus.OCCUPIED)
    
    async def mark_table_reserved(self, table_id: UUID) -> bool:
        """Mark a table as reserved.
        
        Args:
            table_id: The table ID.
            
        Returns:
            True if update was successful, False otherwise.
        """
        return await self.execute(table_id, TableStatus.RESERVED)
    
    async def mark_table_cleaning(self, table_id: UUID) -> bool:
        """Mark a table as being cleaned.
        
        Args:
            table_id: The table ID.
            
        Returns:
            True if update was successful, False otherwise.
        """
        return await self.execute(table_id, TableStatus.CLEANING)
    
    async def mark_table_maintenance(self, table_id: UUID) -> bool:
        """Mark a table as under maintenance.
        
        Args:
            table_id: The table ID.
            
        Returns:
            True if update was successful, False otherwise.
        """
        return await self.execute(table_id, TableStatus.MAINTENANCE)
    
    async def mark_table_out_of_order(self, table_id: UUID) -> bool:
        """Mark a table as out of order.
        
        Args:
            table_id: The table ID.
            
        Returns:
            True if update was successful, False otherwise.
        """
        return await self.execute(table_id, TableStatus.OUT_OF_ORDER)
