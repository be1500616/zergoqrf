"""Table management domain entities.

This module contains the core business entities for table management.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class TableStatus(str, Enum):
    """Table status enumeration."""
    
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    RESERVED = "reserved"
    CLEANING = "cleaning"
    MAINTENANCE = "maintenance"
    OUT_OF_ORDER = "out_of_order"


class TableShape(str, Enum):
    """Table shape enumeration."""
    
    ROUND = "round"
    SQUARE = "square"
    RECTANGULAR = "rectangular"
    OVAL = "oval"


class TableCategory(str, Enum):
    """Table category enumeration."""
    
    REGULAR = "regular"
    VIP = "vip"
    OUTDOOR = "outdoor"
    BAR = "bar"
    COUNTER = "counter"
    BOOTH = "booth"


class Position(BaseModel):
    """Table position value object."""
    
    x: float = Field(..., description="X coordinate on floor plan")
    y: float = Field(..., description="Y coordinate on floor plan")
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class Dimensions(BaseModel):
    """Table dimensions value object."""
    
    width: float = Field(..., gt=0, description="Table width in pixels")
    height: float = Field(..., gt=0, description="Table height in pixels")
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class QRCodeData(BaseModel):
    """QR code data value object."""
    
    token: str = Field(..., description="Unique QR code token")
    url: Optional[str] = Field(None, description="Generated QR code URL")
    data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional QR code metadata")
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class Floor(BaseModel):
    """Floor entity representing a restaurant floor."""
    
    id: UUID
    restaurant_id: UUID
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    floor_number: int = Field(..., ge=0)
    is_active: bool = True
    layout_config: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class Table(BaseModel):
    """Table entity representing a restaurant table."""
    
    id: UUID
    restaurant_id: UUID
    floor_id: Optional[UUID] = None
    table_number: str = Field(..., min_length=1, max_length=50)
    capacity: int = Field(..., gt=0)
    status: TableStatus = TableStatus.AVAILABLE
    shape: TableShape = TableShape.ROUND
    category: TableCategory = TableCategory.REGULAR
    position: Optional[Position] = None
    dimensions: Optional[Dimensions] = None
    rotation: float = Field(default=0.0, ge=0, lt=360)
    special_requirements: List[str] = Field(default_factory=list)
    is_accessible: bool = False
    has_power_outlet: bool = False
    has_window_view: bool = False
    min_party_size: int = Field(default=1, gt=0)
    max_party_size: Optional[int] = None
    qr_code_data: Optional[QRCodeData] = None
    last_cleaned_at: Optional[datetime] = None
    last_occupied_at: Optional[datetime] = None
    notes: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    
    def __post_init__(self):
        """Post-initialization validation."""
        if self.max_party_size is None:
            self.max_party_size = self.capacity
        
        if self.max_party_size < self.min_party_size:
            raise ValueError("max_party_size must be >= min_party_size")
    
    def can_accommodate(self, party_size: int) -> bool:
        """Check if table can accommodate a party of given size.
        
        Args:
            party_size: Number of people in the party.
            
        Returns:
            True if table can accommodate the party, False otherwise.
        """
        return (
            self.is_active and
            self.status == TableStatus.AVAILABLE and
            self.min_party_size <= party_size <= (self.max_party_size or self.capacity)
        )
    
    def is_available_for_reservation(self) -> bool:
        """Check if table is available for reservation.
        
        Returns:
            True if table can be reserved, False otherwise.
        """
        return (
            self.is_active and
            self.status in [TableStatus.AVAILABLE, TableStatus.RESERVED]
        )
    
    def needs_cleaning(self) -> bool:
        """Check if table needs cleaning.
        
        Returns:
            True if table needs cleaning, False otherwise.
        """
        if not self.last_cleaned_at:
            return True
        
        # If table was occupied after last cleaning, it needs cleaning
        if self.last_occupied_at and self.last_occupied_at > self.last_cleaned_at:
            return True
        
        return False
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class TableReservation(BaseModel):
    """Table reservation entity."""
    
    id: UUID
    table_id: UUID
    restaurant_id: UUID
    customer_name: str = Field(..., min_length=1, max_length=255)
    customer_phone: Optional[str] = Field(None, max_length=20)
    customer_email: Optional[str] = Field(None, max_length=255)
    party_size: int = Field(..., gt=0)
    reservation_time: datetime
    duration_minutes: int = Field(default=120, gt=0)
    status: str = Field(default="confirmed")
    special_requests: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class TableSession(BaseModel):
    """Table session entity for tracking occupancy."""
    
    id: UUID
    table_id: UUID
    restaurant_id: UUID
    session_start: datetime
    session_end: Optional[datetime] = None
    party_size: Optional[int] = None
    server_id: Optional[UUID] = None
    order_total: Optional[float] = None
    status: str = Field(default="active")
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    @property
    def duration_minutes(self) -> Optional[int]:
        """Calculate session duration in minutes.
        
        Returns:
            Duration in minutes if session has ended, None otherwise.
        """
        if not self.session_end:
            return None
        
        duration = self.session_end - self.session_start
        return int(duration.total_seconds() / 60)
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class TableMaintenanceLog(BaseModel):
    """Table maintenance log entity."""
    
    id: UUID
    table_id: UUID
    restaurant_id: UUID
    maintenance_type: str = Field(..., description="Type of maintenance performed")
    performed_by: Optional[UUID] = None
    performed_at: datetime
    description: Optional[str] = None
    duration_minutes: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
