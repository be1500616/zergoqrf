"""Table management repository interfaces.

This module contains abstract repository interfaces for table management.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from .table_entities import (
    Floor,
    Table,
    TableMaintenanceLog,
    TableReservation,
    TableSession,
    TableStatus,
)


class IFloorRepository(ABC):
    """Abstract repository interface for floor management."""
    
    @abstractmethod
    async def create_floor(self, floor_data: dict) -> Floor:
        """Create a new floor.
        
        Args:
            floor_data: Dictionary containing floor information.
            
        Returns:
            The created floor entity.
            
        Raises:
            Exception: If floor creation fails.
        """
        pass
    
    @abstractmethod
    async def get_floor_by_id(self, floor_id: UUID) -> Optional[Floor]:
        """Get floor by ID.
        
        Args:
            floor_id: The floor ID.
            
        Returns:
            The floor entity if found, None otherwise.
        """
        pass
    
    @abstractmethod
    async def get_floors_by_restaurant(self, restaurant_id: UUID) -> List[Floor]:
        """Get all floors for a restaurant.
        
        Args:
            restaurant_id: The restaurant ID.
            
        Returns:
            List of floor entities.
        """
        pass
    
    @abstractmethod
    async def update_floor(self, floor_id: UUID, floor_data: dict) -> Optional[Floor]:
        """Update floor information.
        
        Args:
            floor_id: The floor ID.
            floor_data: Dictionary containing updated floor information.
            
        Returns:
            The updated floor entity if found, None otherwise.
        """
        pass
    
    @abstractmethod
    async def delete_floor(self, floor_id: UUID) -> bool:
        """Delete a floor.
        
        Args:
            floor_id: The floor ID.
            
        Returns:
            True if deletion was successful, False otherwise.
        """
        pass


class ITableRepository(ABC):
    """Abstract repository interface for table management."""
    
    @abstractmethod
    async def create_table(self, table_data: dict) -> Table:
        """Create a new table.
        
        Args:
            table_data: Dictionary containing table information.
            
        Returns:
            The created table entity.
            
        Raises:
            Exception: If table creation fails.
        """
        pass
    
    @abstractmethod
    async def get_table_by_id(self, table_id: UUID) -> Optional[Table]:
        """Get table by ID.
        
        Args:
            table_id: The table ID.
            
        Returns:
            The table entity if found, None otherwise.
        """
        pass
    
    @abstractmethod
    async def get_table_by_number(self, restaurant_id: UUID, table_number: str) -> Optional[Table]:
        """Get table by number within a restaurant.
        
        Args:
            restaurant_id: The restaurant ID.
            table_number: The table number.
            
        Returns:
            The table entity if found, None otherwise.
        """
        pass
    
    @abstractmethod
    async def get_tables_by_restaurant(self, restaurant_id: UUID) -> List[Table]:
        """Get all tables for a restaurant.
        
        Args:
            restaurant_id: The restaurant ID.
            
        Returns:
            List of table entities.
        """
        pass
    
    @abstractmethod
    async def get_tables_by_floor(self, floor_id: UUID) -> List[Table]:
        """Get all tables for a floor.
        
        Args:
            floor_id: The floor ID.
            
        Returns:
            List of table entities.
        """
        pass
    
    @abstractmethod
    async def get_tables_by_status(self, restaurant_id: UUID, status: TableStatus) -> List[Table]:
        """Get tables by status.
        
        Args:
            restaurant_id: The restaurant ID.
            status: The table status.
            
        Returns:
            List of table entities with the specified status.
        """
        pass
    
    @abstractmethod
    async def update_table(self, table_id: UUID, table_data: dict) -> Optional[Table]:
        """Update table information.
        
        Args:
            table_id: The table ID.
            table_data: Dictionary containing updated table information.
            
        Returns:
            The updated table entity if found, None otherwise.
        """
        pass
    
    @abstractmethod
    async def update_table_status(self, table_id: UUID, status: TableStatus) -> bool:
        """Update table status.
        
        Args:
            table_id: The table ID.
            status: The new table status.
            
        Returns:
            True if update was successful, False otherwise.
        """
        pass
    
    @abstractmethod
    async def delete_table(self, table_id: UUID) -> bool:
        """Delete a table.
        
        Args:
            table_id: The table ID.
            
        Returns:
            True if deletion was successful, False otherwise.
        """
        pass
    
    @abstractmethod
    async def get_available_tables(self, restaurant_id: UUID, party_size: int) -> List[Table]:
        """Get available tables that can accommodate a party.
        
        Args:
            restaurant_id: The restaurant ID.
            party_size: Number of people in the party.
            
        Returns:
            List of available table entities.
        """
        pass


class ITableReservationRepository(ABC):
    """Abstract repository interface for table reservation management."""
    
    @abstractmethod
    async def create_reservation(self, reservation_data: dict) -> TableReservation:
        """Create a new table reservation.
        
        Args:
            reservation_data: Dictionary containing reservation information.
            
        Returns:
            The created reservation entity.
        """
        pass
    
    @abstractmethod
    async def get_reservation_by_id(self, reservation_id: UUID) -> Optional[TableReservation]:
        """Get reservation by ID.
        
        Args:
            reservation_id: The reservation ID.
            
        Returns:
            The reservation entity if found, None otherwise.
        """
        pass
    
    @abstractmethod
    async def get_reservations_by_table(self, table_id: UUID) -> List[TableReservation]:
        """Get all reservations for a table.
        
        Args:
            table_id: The table ID.
            
        Returns:
            List of reservation entities.
        """
        pass
    
    @abstractmethod
    async def get_reservations_by_restaurant(self, restaurant_id: UUID) -> List[TableReservation]:
        """Get all reservations for a restaurant.
        
        Args:
            restaurant_id: The restaurant ID.
            
        Returns:
            List of reservation entities.
        """
        pass
    
    @abstractmethod
    async def get_reservations_by_date_range(
        self, 
        restaurant_id: UUID, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[TableReservation]:
        """Get reservations within a date range.
        
        Args:
            restaurant_id: The restaurant ID.
            start_date: Start of date range.
            end_date: End of date range.
            
        Returns:
            List of reservation entities.
        """
        pass
    
    @abstractmethod
    async def update_reservation(self, reservation_id: UUID, reservation_data: dict) -> Optional[TableReservation]:
        """Update reservation information.
        
        Args:
            reservation_id: The reservation ID.
            reservation_data: Dictionary containing updated reservation information.
            
        Returns:
            The updated reservation entity if found, None otherwise.
        """
        pass
    
    @abstractmethod
    async def cancel_reservation(self, reservation_id: UUID) -> bool:
        """Cancel a reservation.
        
        Args:
            reservation_id: The reservation ID.
            
        Returns:
            True if cancellation was successful, False otherwise.
        """
        pass


class ITableSessionRepository(ABC):
    """Abstract repository interface for table session management."""
    
    @abstractmethod
    async def create_session(self, session_data: dict) -> TableSession:
        """Create a new table session.
        
        Args:
            session_data: Dictionary containing session information.
            
        Returns:
            The created session entity.
        """
        pass
    
    @abstractmethod
    async def get_session_by_id(self, session_id: UUID) -> Optional[TableSession]:
        """Get session by ID.
        
        Args:
            session_id: The session ID.
            
        Returns:
            The session entity if found, None otherwise.
        """
        pass
    
    @abstractmethod
    async def get_active_session_by_table(self, table_id: UUID) -> Optional[TableSession]:
        """Get active session for a table.
        
        Args:
            table_id: The table ID.
            
        Returns:
            The active session entity if found, None otherwise.
        """
        pass
    
    @abstractmethod
    async def get_sessions_by_restaurant(self, restaurant_id: UUID) -> List[TableSession]:
        """Get all sessions for a restaurant.
        
        Args:
            restaurant_id: The restaurant ID.
            
        Returns:
            List of session entities.
        """
        pass
    
    @abstractmethod
    async def end_session(self, session_id: UUID, order_total: Optional[float] = None) -> bool:
        """End a table session.
        
        Args:
            session_id: The session ID.
            order_total: Optional order total amount.
            
        Returns:
            True if session was ended successfully, False otherwise.
        """
        pass


class ITableMaintenanceRepository(ABC):
    """Abstract repository interface for table maintenance management."""
    
    @abstractmethod
    async def create_maintenance_log(self, log_data: dict) -> TableMaintenanceLog:
        """Create a new maintenance log entry.
        
        Args:
            log_data: Dictionary containing maintenance log information.
            
        Returns:
            The created maintenance log entity.
        """
        pass
    
    @abstractmethod
    async def get_maintenance_logs_by_table(self, table_id: UUID) -> List[TableMaintenanceLog]:
        """Get maintenance logs for a table.
        
        Args:
            table_id: The table ID.
            
        Returns:
            List of maintenance log entities.
        """
        pass
    
    @abstractmethod
    async def get_maintenance_logs_by_restaurant(self, restaurant_id: UUID) -> List[TableMaintenanceLog]:
        """Get maintenance logs for a restaurant.
        
        Args:
            restaurant_id: The restaurant ID.
            
        Returns:
            List of maintenance log entities.
        """
        pass
