"""Table management Data Transfer Objects (DTOs).

This module contains DTOs for transferring data between application layers.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from ..domain.table_entities import TableCategory, TableShape, TableStatus


class PositionDTO(BaseModel):
    """Position data transfer object."""
    
    x: float = Field(..., description="X coordinate on floor plan")
    y: float = Field(..., description="Y coordinate on floor plan")


class DimensionsDTO(BaseModel):
    """Dimensions data transfer object."""
    
    width: float = Field(..., gt=0, description="Table width in pixels")
    height: float = Field(..., gt=0, description="Table height in pixels")


class QRCodeDataDTO(BaseModel):
    """QR code data transfer object."""
    
    token: str = Field(..., description="Unique QR code token")
    url: Optional[str] = Field(None, description="Generated QR code URL")
    data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional QR code metadata")


class FloorDTO(BaseModel):
    """Floor data transfer object."""
    
    id: UUID
    restaurant_id: UUID
    name: str
    description: Optional[str] = None
    floor_number: int
    is_active: bool
    layout_config: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


class TableDTO(BaseModel):
    """Table data transfer object."""
    
    id: UUID
    restaurant_id: UUID
    floor_id: Optional[UUID] = None
    table_number: str
    capacity: int
    status: TableStatus
    shape: TableShape
    category: TableCategory
    position: Optional[PositionDTO] = None
    dimensions: Optional[DimensionsDTO] = None
    rotation: float
    special_requirements: List[str]
    is_accessible: bool
    has_power_outlet: bool
    has_window_view: bool
    min_party_size: int
    max_party_size: Optional[int] = None
    qr_code_data: Optional[QRCodeDataDTO] = None
    last_cleaned_at: Optional[datetime] = None
    last_occupied_at: Optional[datetime] = None
    notes: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class TableReservationDTO(BaseModel):
    """Table reservation data transfer object."""
    
    id: UUID
    table_id: UUID
    restaurant_id: UUID
    customer_name: str
    customer_phone: Optional[str] = None
    customer_email: Optional[str] = None
    party_size: int
    reservation_time: datetime
    duration_minutes: int
    status: str
    special_requests: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class TableSessionDTO(BaseModel):
    """Table session data transfer object."""
    
    id: UUID
    table_id: UUID
    restaurant_id: UUID
    session_start: datetime
    session_end: Optional[datetime] = None
    party_size: Optional[int] = None
    server_id: Optional[UUID] = None
    order_total: Optional[float] = None
    status: str
    notes: Optional[str] = None
    duration_minutes: Optional[int] = None
    created_at: datetime
    updated_at: datetime


class TableMaintenanceLogDTO(BaseModel):
    """Table maintenance log data transfer object."""
    
    id: UUID
    table_id: UUID
    restaurant_id: UUID
    maintenance_type: str
    performed_by: Optional[UUID] = None
    performed_at: datetime
    description: Optional[str] = None
    duration_minutes: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime


class TableOccupancyStatsDTO(BaseModel):
    """Table occupancy statistics data transfer object."""
    
    total_tables: int
    available_tables: int
    occupied_tables: int
    reserved_tables: int
    cleaning_tables: int
    maintenance_tables: int
    occupancy_rate: float
    
    
class FloorPlanDTO(BaseModel):
    """Floor plan data transfer object."""
    
    floor: FloorDTO
    tables: List[TableDTO]
    occupancy_stats: TableOccupancyStatsDTO


class CreateFloorDTO(BaseModel):
    """Create floor request DTO."""
    
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    floor_number: int = Field(..., ge=0)
    layout_config: Dict[str, Any] = Field(default_factory=dict)


class UpdateFloorDTO(BaseModel):
    """Update floor request DTO."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None
    layout_config: Optional[Dict[str, Any]] = None


class CreateTableDTO(BaseModel):
    """Create table request DTO."""
    
    floor_id: Optional[UUID] = None
    table_number: str = Field(..., min_length=1, max_length=50)
    capacity: int = Field(..., gt=0)
    shape: TableShape = TableShape.ROUND
    category: TableCategory = TableCategory.REGULAR
    position: Optional[PositionDTO] = None
    dimensions: Optional[DimensionsDTO] = None
    rotation: float = Field(default=0.0, ge=0, lt=360)
    special_requirements: List[str] = Field(default_factory=list)
    is_accessible: bool = False
    has_power_outlet: bool = False
    has_window_view: bool = False
    min_party_size: int = Field(default=1, gt=0)
    max_party_size: Optional[int] = None
    notes: Optional[str] = None


class UpdateTableDTO(BaseModel):
    """Update table request DTO."""
    
    floor_id: Optional[UUID] = None
    table_number: Optional[str] = Field(None, min_length=1, max_length=50)
    capacity: Optional[int] = Field(None, gt=0)
    shape: Optional[TableShape] = None
    category: Optional[TableCategory] = None
    position: Optional[PositionDTO] = None
    dimensions: Optional[DimensionsDTO] = None
    rotation: Optional[float] = Field(None, ge=0, lt=360)
    special_requirements: Optional[List[str]] = None
    is_accessible: Optional[bool] = None
    has_power_outlet: Optional[bool] = None
    has_window_view: Optional[bool] = None
    min_party_size: Optional[int] = Field(None, gt=0)
    max_party_size: Optional[int] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class CreateReservationDTO(BaseModel):
    """Create reservation request DTO."""
    
    table_id: UUID
    customer_name: str = Field(..., min_length=1, max_length=255)
    customer_phone: Optional[str] = Field(None, max_length=20)
    customer_email: Optional[str] = Field(None, max_length=255)
    party_size: int = Field(..., gt=0)
    reservation_time: datetime
    duration_minutes: int = Field(default=120, gt=0)
    special_requests: Optional[str] = None
    notes: Optional[str] = None


class UpdateReservationDTO(BaseModel):
    """Update reservation request DTO."""
    
    customer_name: Optional[str] = Field(None, min_length=1, max_length=255)
    customer_phone: Optional[str] = Field(None, max_length=20)
    customer_email: Optional[str] = Field(None, max_length=255)
    party_size: Optional[int] = Field(None, gt=0)
    reservation_time: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, gt=0)
    status: Optional[str] = None
    special_requests: Optional[str] = None
    notes: Optional[str] = None


class CreateSessionDTO(BaseModel):
    """Create session request DTO."""
    
    table_id: UUID
    party_size: Optional[int] = None
    server_id: Optional[UUID] = None
    notes: Optional[str] = None


class CreateMaintenanceLogDTO(BaseModel):
    """Create maintenance log request DTO."""
    
    table_id: UUID
    maintenance_type: str = Field(..., description="Type of maintenance performed")
    performed_by: Optional[UUID] = None
    description: Optional[str] = None
    duration_minutes: Optional[int] = None
    notes: Optional[str] = None
