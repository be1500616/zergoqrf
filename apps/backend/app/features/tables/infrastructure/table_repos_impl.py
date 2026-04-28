"""Table repository implementations.

This module contains concrete implementations of table repository interfaces.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from supabase import Client

from ..domain.table_entities import (
    Dimensions,
    Floor,
    Position,
    QRCodeData,
    Table,
    TableMaintenanceLog,
    TableReservation,
    TableSession,
    TableStatus,
)
from ..domain.table_repos import (
    IFloorRepository,
    ITableMaintenanceRepository,
    ITableRepository,
    ITableReservationRepository,
    ITableSessionRepository,
)


class FloorRepositoryImpl(IFloorRepository):
    """Concrete implementation of floor repository using Supabase."""
    
    def __init__(self, supabase: Client):
        """Initialize the repository.
        
        Args:
            supabase: Supabase client instance.
        """
        self._supabase = supabase
    
    async def create_floor(self, floor_data: dict) -> Floor:
        """Create a new floor.
        
        Args:
            floor_data: Dictionary containing floor information.
            
        Returns:
            The created floor entity.
            
        Raises:
            Exception: If floor creation fails.
        """
        try:
            result = self._supabase.table("floors").insert(floor_data).execute()
            
            if not result.data:
                raise Exception("Failed to create floor")
            
            return Floor(**result.data[0])
        except Exception as e:
            raise Exception(f"Failed to create floor: {str(e)}")
    
    async def get_floor_by_id(self, floor_id: UUID) -> Optional[Floor]:
        """Get floor by ID.
        
        Args:
            floor_id: The floor ID.
            
        Returns:
            The floor entity if found, None otherwise.
        """
        try:
            result = (
                self._supabase.table("floors")
                .select("*")
                .eq("id", str(floor_id))
                .execute()
            )
            
            if result.data:
                return Floor(**result.data[0])
            return None
        except Exception:
            return None
    
    async def get_floors_by_restaurant(self, restaurant_id: UUID) -> List[Floor]:
        """Get all floors for a restaurant.
        
        Args:
            restaurant_id: The restaurant ID.
            
        Returns:
            List of floor entities.
        """
        try:
            result = (
                self._supabase.table("floors")
                .select("*")
                .eq("restaurant_id", str(restaurant_id))
                .order("floor_number")
                .execute()
            )
            
            return [Floor(**floor_data) for floor_data in result.data]
        except Exception:
            return []
    
    async def update_floor(self, floor_id: UUID, floor_data: dict) -> Optional[Floor]:
        """Update floor information.
        
        Args:
            floor_id: The floor ID.
            floor_data: Dictionary containing updated floor information.
            
        Returns:
            The updated floor entity if found, None otherwise.
        """
        try:
            result = (
                self._supabase.table("floors")
                .update(floor_data)
                .eq("id", str(floor_id))
                .execute()
            )
            
            if result.data:
                return Floor(**result.data[0])
            return None
        except Exception:
            return None
    
    async def delete_floor(self, floor_id: UUID) -> bool:
        """Delete a floor.
        
        Args:
            floor_id: The floor ID.
            
        Returns:
            True if deletion was successful, False otherwise.
        """
        try:
            result = (
                self._supabase.table("floors")
                .delete()
                .eq("id", str(floor_id))
                .execute()
            )
            
            return len(result.data) > 0
        except Exception:
            return False


class TableRepositoryImpl(ITableRepository):
    """Concrete implementation of table repository using Supabase."""
    
    def __init__(self, supabase: Client):
        """Initialize the repository.
        
        Args:
            supabase: Supabase client instance.
        """
        self._supabase = supabase
    
    async def create_table(self, table_data: dict) -> Table:
        """Create a new table.
        
        Args:
            table_data: Dictionary containing table information.
            
        Returns:
            The created table entity.
            
        Raises:
            Exception: If table creation fails.
        """
        try:
            result = self._supabase.table("tables").insert(table_data).execute()
            
            if not result.data:
                raise Exception("Failed to create table")
            
            return self._dict_to_table(result.data[0])
        except Exception as e:
            raise Exception(f"Failed to create table: {str(e)}")
    
    async def get_table_by_id(self, table_id: UUID) -> Optional[Table]:
        """Get table by ID.
        
        
        Args:
            table_id: The table ID.
            
        Returns:
            The table entity if found, None otherwise.
        """
        try:
            result = (
                self._supabase.table("tables")
                .select("*")
                .eq("id", str(table_id))
                .execute()
            )
            
            if result.data:
                return self._dict_to_table(result.data[0])
            return None
        except Exception:
            return None
    
    async def get_table_by_number(self, restaurant_id: UUID, table_number: str) -> Optional[Table]:
        """Get table by number within a restaurant.
        
        Args:
            restaurant_id: The restaurant ID.
            table_number: The table number.
            
        Returns:
            The table entity if found, None otherwise.
        """
        try:
            result = (
                self._supabase.table("tables")
                .select("*")
                .eq("restaurant_id", str(restaurant_id))
                .eq("table_number", table_number)
                .execute()
            )
            
            if result.data:
                return self._dict_to_table(result.data[0])
            return None
        except Exception:
            return None
    
    async def get_tables_by_restaurant(self, restaurant_id: UUID) -> List[Table]:
        """Get all tables for a restaurant.
        
        Args:
            restaurant_id: The restaurant ID.
            
        Returns:
            List of table entities.
        """
        try:
            result = (
                self._supabase.table("tables")
                .select("*")
                .eq("restaurant_id", str(restaurant_id))
                .order("table_number")
                .execute()
            )
            
            return [self._dict_to_table(table_data) for table_data in result.data]
        except Exception:
            return []
    
    async def get_tables_by_floor(self, floor_id: UUID) -> List[Table]:
        """Get all tables for a floor.
        
        Args:
            floor_id: The floor ID.
            
        Returns:
            List of table entities.
        """
        try:
            result = (
                self._supabase.table("tables")
                .select("*")
                .eq("floor_id", str(floor_id))
                .order("table_number")
                .execute()
            )
            
            return [self._dict_to_table(table_data) for table_data in result.data]
        except Exception:
            return []
    
    async def get_tables_by_status(self, restaurant_id: UUID, status: TableStatus) -> List[Table]:
        """Get tables by status.
        
        Args:
            restaurant_id: The restaurant ID.
            status: The table status.
            
        Returns:
            List of table entities with the specified status.
        """
        try:
            result = (
                self._supabase.table("tables")
                .select("*")
                .eq("restaurant_id", str(restaurant_id))
                .eq("status", status.value)
                .order("table_number")
                .execute()
            )
            
            return [self._dict_to_table(table_data) for table_data in result.data]
        except Exception:
            return []
    
    async def update_table(self, table_id: UUID, table_data: dict) -> Optional[Table]:
        """Update table information.
        
        Args:
            table_id: The table ID.
            table_data: Dictionary containing updated table information.
            
        Returns:
            The updated table entity if found, None otherwise.
        """
        try:
            result = (
                self._supabase.table("tables")
                .update(table_data)
                .eq("id", str(table_id))
                .execute()
            )
            
            if result.data:
                return self._dict_to_table(result.data[0])
            return None
        except Exception:
            return None
    
    async def update_table_status(self, table_id: UUID, status: TableStatus) -> bool:
        """Update table status.
        
        Args:
            table_id: The table ID.
            status: The new table status.
            
        Returns:
            True if update was successful, False otherwise.
        """
        try:
            result = (
                self._supabase.table("tables")
                .update({"status": status.value})
                .eq("id", str(table_id))
                .execute()
            )
            
            return len(result.data) > 0
        except Exception:
            return False
    
    async def delete_table(self, table_id: UUID) -> bool:
        """Delete a table.
        
        Args:
            table_id: The table ID.
            
        Returns:
            True if deletion was successful, False otherwise.
        """
        try:
            result = (
                self._supabase.table("tables")
                .delete()
                .eq("id", str(table_id))
                .execute()
            )
            
            return len(result.data) > 0
        except Exception:
            return False
    
    async def get_available_tables(self, restaurant_id: UUID, party_size: int) -> List[Table]:
        """Get available tables that can accommodate a party.
        
        Args:
            restaurant_id: The restaurant ID.
            party_size: Number of people in the party.
            
        Returns:
            List of available table entities.
        """
        try:
            result = (
                self._supabase.table("tables")
                .select("*")
                .eq("restaurant_id", str(restaurant_id))
                .eq("status", "available")
                .eq("is_active", True)
                .gte("max_party_size", party_size)
                .lte("min_party_size", party_size)
                .order("capacity")
                .execute()
            )
            
            return [self._dict_to_table(table_data) for table_data in result.data]
        except Exception:
            return []
    
    def _dict_to_table(self, data: Dict[str, Any]) -> Table:
        """Convert dictionary data to Table entity.
        
        Args:
            data: Dictionary containing table data.
            
        Returns:
            Table entity.
        """
        # Parse position if present
        position = None
        if data.get("position"):
            position = Position(**data["position"])
        
        # Parse dimensions if present
        dimensions = None
        if data.get("dimensions"):
            dimensions = Dimensions(**data["dimensions"])
        
        # Parse QR code data if present
        qr_code_data = None
        if data.get("qr_code_data"):
            qr_code_data = QRCodeData(**data["qr_code_data"])
        
        # Parse timestamps
        created_at = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
        updated_at = datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00"))
        
        last_cleaned_at = None
        if data.get("last_cleaned_at"):
            last_cleaned_at = datetime.fromisoformat(data["last_cleaned_at"].replace("Z", "+00:00"))
        
        last_occupied_at = None
        if data.get("last_occupied_at"):
            last_occupied_at = datetime.fromisoformat(data["last_occupied_at"].replace("Z", "+00:00"))
        
        return Table(
            id=UUID(data["id"]),
            restaurant_id=UUID(data["restaurant_id"]),
            floor_id=UUID(data["floor_id"]) if data.get("floor_id") else None,
            table_number=data["table_number"],
            capacity=data["capacity"],
            status=TableStatus(data["status"]),
            shape=data.get("shape", "round"),
            category=data.get("category", "regular"),
            position=position,
            dimensions=dimensions,
            rotation=data.get("rotation", 0.0),
            special_requirements=data.get("special_requirements", []),
            is_accessible=data.get("is_accessible", False),
            has_power_outlet=data.get("has_power_outlet", False),
            has_window_view=data.get("has_window_view", False),
            min_party_size=data.get("min_party_size", 1),
            max_party_size=data.get("max_party_size"),
            qr_code_data=qr_code_data,
            last_cleaned_at=last_cleaned_at,
            last_occupied_at=last_occupied_at,
            notes=data.get("notes"),
            is_active=data.get("is_active", True),
            created_at=created_at,
            updated_at=updated_at,
        )


class TableReservationRepositoryImpl(ITableReservationRepository):
    """Concrete implementation of table reservation repository using Supabase."""

    def __init__(self, supabase: Client):
        """Initialize the repository.

        Args:
            supabase: Supabase client instance.
        """
        self._supabase = supabase

    async def create_reservation(self, reservation_data: dict) -> TableReservation:
        """Create a new table reservation.

        Args:
            reservation_data: Dictionary containing reservation information.

        Returns:
            The created reservation entity.
        """
        try:
            result = self._supabase.table("table_reservations").insert(reservation_data).execute()

            if not result.data:
                raise Exception("Failed to create reservation")

            return TableReservation(**result.data[0])
        except Exception as e:
            raise Exception(f"Failed to create reservation: {str(e)}")

    async def get_reservation_by_id(self, reservation_id: UUID) -> Optional[TableReservation]:
        """Get reservation by ID.

        Args:
            reservation_id: The reservation ID.

        Returns:
            The reservation entity if found, None otherwise.
        """
        try:
            result = (
                self._supabase.table("table_reservations")
                .select("*")
                .eq("id", str(reservation_id))
                .execute()
            )

            if result.data:
                return TableReservation(**result.data[0])
            return None
        except Exception:
            return None

    async def get_reservations_by_table(self, table_id: UUID) -> List[TableReservation]:
        """Get all reservations for a table.

        Args:
            table_id: The table ID.

        Returns:
            List of reservation entities.
        """
        try:
            result = (
                self._supabase.table("table_reservations")
                .select("*")
                .eq("table_id", str(table_id))
                .order("reservation_time")
                .execute()
            )

            return [TableReservation(**res_data) for res_data in result.data]
        except Exception:
            return []

    async def get_reservations_by_restaurant(self, restaurant_id: UUID) -> List[TableReservation]:
        """Get all reservations for a restaurant.

        Args:
            restaurant_id: The restaurant ID.

        Returns:
            List of reservation entities.
        """
        try:
            result = (
                self._supabase.table("table_reservations")
                .select("*")
                .eq("restaurant_id", str(restaurant_id))
                .order("reservation_time")
                .execute()
            )

            return [TableReservation(**res_data) for res_data in result.data]
        except Exception:
            return []

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
        try:
            result = (
                self._supabase.table("table_reservations")
                .select("*")
                .eq("restaurant_id", str(restaurant_id))
                .gte("reservation_time", start_date.isoformat())
                .lte("reservation_time", end_date.isoformat())
                .order("reservation_time")
                .execute()
            )

            return [TableReservation(**res_data) for res_data in result.data]
        except Exception:
            return []

    async def update_reservation(self, reservation_id: UUID, reservation_data: dict) -> Optional[TableReservation]:
        """Update reservation information.

        Args:
            reservation_id: The reservation ID.
            reservation_data: Dictionary containing updated reservation information.

        Returns:
            The updated reservation entity if found, None otherwise.
        """
        try:
            result = (
                self._supabase.table("table_reservations")
                .update(reservation_data)
                .eq("id", str(reservation_id))
                .execute()
            )

            if result.data:
                return TableReservation(**result.data[0])
            return None
        except Exception:
            return None

    async def cancel_reservation(self, reservation_id: UUID) -> bool:
        """Cancel a reservation.

        Args:
            reservation_id: The reservation ID.

        Returns:
            True if cancellation was successful, False otherwise.
        """
        try:
            result = (
                self._supabase.table("table_reservations")
                .update({"status": "cancelled"})
                .eq("id", str(reservation_id))
                .execute()
            )

            return len(result.data) > 0
        except Exception:
            return False


class TableSessionRepositoryImpl(ITableSessionRepository):
    """Concrete implementation of table session repository using Supabase."""

    def __init__(self, supabase: Client):
        """Initialize the repository.

        Args:
            supabase: Supabase client instance.
        """
        self._supabase = supabase

    async def create_session(self, session_data: dict) -> TableSession:
        """Create a new table session.

        Args:
            session_data: Dictionary containing session information.

        Returns:
            The created session entity.
        """
        try:
            result = self._supabase.table("table_sessions").insert(session_data).execute()

            if not result.data:
                raise Exception("Failed to create session")

            return TableSession(**result.data[0])
        except Exception as e:
            raise Exception(f"Failed to create session: {str(e)}")

    async def get_session_by_id(self, session_id: UUID) -> Optional[TableSession]:
        """Get session by ID.

        Args:
            session_id: The session ID.

        Returns:
            The session entity if found, None otherwise.
        """
        try:
            result = (
                self._supabase.table("table_sessions")
                .select("*")
                .eq("id", str(session_id))
                .execute()
            )

            if result.data:
                return TableSession(**result.data[0])
            return None
        except Exception:
            return None

    async def get_active_session_by_table(self, table_id: UUID) -> Optional[TableSession]:
        """Get active session for a table.

        Args:
            table_id: The table ID.

        Returns:
            The active session entity if found, None otherwise.
        """
        try:
            result = (
                self._supabase.table("table_sessions")
                .select("*")
                .eq("table_id", str(table_id))
                .eq("status", "active")
                .execute()
            )

            if result.data:
                return TableSession(**result.data[0])
            return None
        except Exception:
            return None

    async def get_sessions_by_restaurant(self, restaurant_id: UUID) -> List[TableSession]:
        """Get all sessions for a restaurant.

        Args:
            restaurant_id: The restaurant ID.

        Returns:
            List of session entities.
        """
        try:
            result = (
                self._supabase.table("table_sessions")
                .select("*")
                .eq("restaurant_id", str(restaurant_id))
                .order("session_start", desc=True)
                .execute()
            )

            return [TableSession(**session_data) for session_data in result.data]
        except Exception:
            return []

    async def end_session(self, session_id: UUID, order_total: Optional[float] = None) -> bool:
        """End a table session.

        Args:
            session_id: The session ID.
            order_total: Optional order total amount.

        Returns:
            True if session was ended successfully, False otherwise.
        """
        try:
            update_data = {
                "session_end": datetime.utcnow().isoformat(),
                "status": "completed"
            }

            if order_total is not None:
                update_data["order_total"] = order_total

            result = (
                self._supabase.table("table_sessions")
                .update(update_data)
                .eq("id", str(session_id))
                .execute()
            )

            return len(result.data) > 0
        except Exception:
            return False


class TableMaintenanceRepositoryImpl(ITableMaintenanceRepository):
    """Concrete implementation of table maintenance repository using Supabase."""

    def __init__(self, supabase: Client):
        """Initialize the repository.

        Args:
            supabase: Supabase client instance.
        """
        self._supabase = supabase

    async def create_maintenance_log(self, log_data: dict) -> TableMaintenanceLog:
        """Create a new maintenance log entry.

        Args:
            log_data: Dictionary containing maintenance log information.

        Returns:
            The created maintenance log entity.
        """
        try:
            result = self._supabase.table("table_maintenance_logs").insert(log_data).execute()

            if not result.data:
                raise Exception("Failed to create maintenance log")

            return TableMaintenanceLog(**result.data[0])
        except Exception as e:
            raise Exception(f"Failed to create maintenance log: {str(e)}")

    async def get_maintenance_logs_by_table(self, table_id: UUID) -> List[TableMaintenanceLog]:
        """Get maintenance logs for a table.

        Args:
            table_id: The table ID.

        Returns:
            List of maintenance log entities.
        """
        try:
            result = (
                self._supabase.table("table_maintenance_logs")
                .select("*")
                .eq("table_id", str(table_id))
                .order("performed_at", desc=True)
                .execute()
            )

            return [TableMaintenanceLog(**log_data) for log_data in result.data]
        except Exception:
            return []

    async def get_maintenance_logs_by_restaurant(self, restaurant_id: UUID) -> List[TableMaintenanceLog]:
        """Get maintenance logs for a restaurant.

        Args:
            restaurant_id: The restaurant ID.

        Returns:
            List of maintenance log entities.
        """
        try:
            result = (
                self._supabase.table("table_maintenance_logs")
                .select("*")
                .eq("restaurant_id", str(restaurant_id))
                .order("performed_at", desc=True)
                .execute()
            )

            return [TableMaintenanceLog(**log_data) for log_data in result.data]
        except Exception:
            return []
