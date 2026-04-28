"""Table management Pydantic schemas.

This module contains Pydantic schemas for API request/response validation.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from ..domain.table_entities import TableCategory, TableShape, TableStatus


class PositionSchema(BaseModel):
    """Position schema for API requests/responses."""
    
    x: float = Field(..., description="X coordinate on floor plan")
    y: float = Field(..., description="Y coordinate on floor plan")


class DimensionsSchema(BaseModel):
    """Dimensions schema for API requests/responses."""
    
    width: float = Field(..., gt=0, description="Table width in pixels")
    height: float = Field(..., gt=0, description="Table height in pixels")


class QRCodeDataSchema(BaseModel):
    """QR code data schema for API requests/responses."""
    
    token: str = Field(..., description="Unique QR code token")
    url: Optional[str] = Field(None, description="Generated QR code URL")
    data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional QR code metadata")


class CreateFloorSchema(BaseModel):
    """Schema for creating a new floor."""
    
    name: str = Field(..., min_length=1, max_length=100, description="Floor name")
    description: Optional[str] = Field(None, description="Floor description")
    floor_number: int = Field(..., ge=0, description="Floor number")
    layout_config: Dict[str, Any] = Field(default_factory=dict, description="Floor layout configuration")


class UpdateFloorSchema(BaseModel):
    """Schema for updating floor information."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Floor name")
    description: Optional[str] = Field(None, description="Floor description")
    is_active: Optional[bool] = Field(None, description="Whether floor is active")
    layout_config: Optional[Dict[str, Any]] = Field(None, description="Floor layout configuration")


class FloorResponseSchema(BaseModel):
    """Schema for floor response."""
    
    id: UUID
    restaurant_id: UUID
    name: str
    description: Optional[str] = None
    floor_number: int
    is_active: bool
    layout_config: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class CreateTableSchema(BaseModel):
    """Schema for creating a new table."""
    
    floor_id: Optional[UUID] = Field(None, description="Floor ID where table is located")
    table_number: str = Field(..., min_length=1, max_length=50, description="Table number")
    capacity: int = Field(..., gt=0, description="Table seating capacity")
    shape: TableShape = Field(default=TableShape.ROUND, description="Table shape")
    category: TableCategory = Field(default=TableCategory.REGULAR, description="Table category")
    position: Optional[PositionSchema] = Field(None, description="Table position on floor plan")
    dimensions: Optional[DimensionsSchema] = Field(None, description="Table dimensions")
    rotation: float = Field(default=0.0, ge=0, lt=360, description="Table rotation in degrees")
    special_requirements: List[str] = Field(default_factory=list, description="Special requirements")
    is_accessible: bool = Field(default=False, description="Whether table is wheelchair accessible")
    has_power_outlet: bool = Field(default=False, description="Whether table has power outlet")
    has_window_view: bool = Field(default=False, description="Whether table has window view")
    min_party_size: int = Field(default=1, gt=0, description="Minimum party size")
    max_party_size: Optional[int] = Field(None, description="Maximum party size")
    notes: Optional[str] = Field(None, description="Additional notes")


class UpdateTableSchema(BaseModel):
    """Schema for updating table information."""
    
    floor_id: Optional[UUID] = Field(None, description="Floor ID where table is located")
    table_number: Optional[str] = Field(None, min_length=1, max_length=50, description="Table number")
    capacity: Optional[int] = Field(None, gt=0, description="Table seating capacity")
    shape: Optional[TableShape] = Field(None, description="Table shape")
    category: Optional[TableCategory] = Field(None, description="Table category")
    position: Optional[PositionSchema] = Field(None, description="Table position on floor plan")
    dimensions: Optional[DimensionsSchema] = Field(None, description="Table dimensions")
    rotation: Optional[float] = Field(None, ge=0, lt=360, description="Table rotation in degrees")
    special_requirements: Optional[List[str]] = Field(None, description="Special requirements")
    is_accessible: Optional[bool] = Field(None, description="Whether table is wheelchair accessible")
    has_power_outlet: Optional[bool] = Field(None, description="Whether table has power outlet")
    has_window_view: Optional[bool] = Field(None, description="Whether table has window view")
    min_party_size: Optional[int] = Field(None, gt=0, description="Minimum party size")
    max_party_size: Optional[int] = Field(None, description="Maximum party size")
    notes: Optional[str] = Field(None, description="Additional notes")
    is_active: Optional[bool] = Field(None, description="Whether table is active")


class UpdateTableStatusSchema(BaseModel):
    """Schema for updating table status."""
    
    status: TableStatus = Field(..., description="New table status")


class TableResponseSchema(BaseModel):
    """Schema for table response."""
    
    id: UUID
    restaurant_id: UUID
    floor_id: Optional[UUID] = None
    table_number: str
    capacity: int
    status: TableStatus
    shape: TableShape
    category: TableCategory
    position: Optional[PositionSchema] = None
    dimensions: Optional[DimensionsSchema] = None
    rotation: float
    special_requirements: List[str]
    is_accessible: bool
    has_power_outlet: bool
    has_window_view: bool
    min_party_size: int
    max_party_size: Optional[int] = None
    qr_code_data: Optional[QRCodeDataSchema] = None
    last_cleaned_at: Optional[datetime] = None
    last_occupied_at: Optional[datetime] = None
    notes: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class CreateReservationSchema(BaseModel):
    """Schema for creating a table reservation."""
    
    table_id: UUID = Field(..., description="Table ID")
    customer_name: str = Field(..., min_length=1, max_length=255, description="Customer name")
    customer_phone: Optional[str] = Field(None, max_length=20, description="Customer phone")
    customer_email: Optional[str] = Field(None, max_length=255, description="Customer email")
    party_size: int = Field(..., gt=0, description="Party size")
    reservation_time: datetime = Field(..., description="Reservation date and time")
    duration_minutes: int = Field(default=120, gt=0, description="Reservation duration in minutes")
    special_requests: Optional[str] = Field(None, description="Special requests")
    notes: Optional[str] = Field(None, description="Additional notes")


class UpdateReservationSchema(BaseModel):
    """Schema for updating reservation information."""
    
    customer_name: Optional[str] = Field(None, min_length=1, max_length=255, description="Customer name")
    customer_phone: Optional[str] = Field(None, max_length=20, description="Customer phone")
    customer_email: Optional[str] = Field(None, max_length=255, description="Customer email")
    party_size: Optional[int] = Field(None, gt=0, description="Party size")
    reservation_time: Optional[datetime] = Field(None, description="Reservation date and time")
    duration_minutes: Optional[int] = Field(None, gt=0, description="Reservation duration in minutes")
    status: Optional[str] = Field(None, description="Reservation status")
    special_requests: Optional[str] = Field(None, description="Special requests")
    notes: Optional[str] = Field(None, description="Additional notes")


class ReservationResponseSchema(BaseModel):
    """Schema for reservation response."""
    
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
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class CreateSessionSchema(BaseModel):
    """Schema for creating a table session."""
    
    table_id: UUID = Field(..., description="Table ID")
    party_size: Optional[int] = Field(None, description="Party size")
    server_id: Optional[UUID] = Field(None, description="Server ID")
    notes: Optional[str] = Field(None, description="Session notes")


class SessionResponseSchema(BaseModel):
    """Schema for session response."""
    
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
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class CreateMaintenanceLogSchema(BaseModel):
    """Schema for creating a maintenance log."""
    
    table_id: UUID = Field(..., description="Table ID")
    maintenance_type: str = Field(..., description="Type of maintenance performed")
    performed_by: Optional[UUID] = Field(None, description="Staff member who performed maintenance")
    description: Optional[str] = Field(None, description="Maintenance description")
    duration_minutes: Optional[int] = Field(None, description="Maintenance duration in minutes")
    notes: Optional[str] = Field(None, description="Additional notes")


class MaintenanceLogResponseSchema(BaseModel):
    """Schema for maintenance log response."""
    
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
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class TableOccupancyStatsSchema(BaseModel):
    """Schema for table occupancy statistics."""
    
    total_tables: int
    available_tables: int
    occupied_tables: int
    reserved_tables: int
    cleaning_tables: int
    maintenance_tables: int
    occupancy_rate: float


class FloorPlanResponseSchema(BaseModel):
    """Schema for floor plan response."""
    
    floor: FloorResponseSchema
    tables: List[TableResponseSchema]
    occupancy_stats: TableOccupancyStatsSchema
