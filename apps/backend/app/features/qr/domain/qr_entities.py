"""QR generation domain entities.

This module contains the core business entities for QR code generation.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class QRFormat(str, Enum):
    """QR code output format enumeration."""
    
    PNG = "png"
    SVG = "svg"
    PDF = "pdf"


class QRErrorCorrection(str, Enum):
    """QR code error correction level enumeration."""
    
    LOW = "L"      # ~7% error correction
    MEDIUM = "M"   # ~15% error correction
    QUARTILE = "Q" # ~25% error correction
    HIGH = "H"     # ~30% error correction


class QRSize(str, Enum):
    """QR code size presets."""
    
    SMALL = "small"    # 200x200px
    MEDIUM = "medium"  # 400x400px
    LARGE = "large"    # 800x800px
    XLARGE = "xlarge"  # 1200x1200px


class QRCodeConfig(BaseModel):
    """QR code generation configuration."""
    
    format: QRFormat = QRFormat.PNG
    size: QRSize = QRSize.MEDIUM
    error_correction: QRErrorCorrection = QRErrorCorrection.MEDIUM
    border: int = Field(default=4, ge=0, le=20, description="Border size in modules")
    include_logo: bool = Field(default=False, description="Include restaurant logo in center")
    logo_size_ratio: float = Field(default=0.3, ge=0.1, le=0.5, description="Logo size as ratio of QR code")
    background_color: str = Field(default="white", description="Background color")
    foreground_color: str = Field(default="black", description="Foreground color")
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class QRCodeData(BaseModel):
    """QR code data and metadata."""
    
    url: str = Field(..., description="The URL encoded in the QR code")
    table_id: UUID = Field(..., description="Table ID this QR code belongs to")
    restaurant_id: UUID = Field(..., description="Restaurant ID")
    restaurant_code: str = Field(..., description="Restaurant unique code")
    table_number: str = Field(..., description="Table number")
    config: QRCodeConfig = Field(default_factory=QRCodeConfig, description="QR code configuration")
    
    @property
    def filename(self) -> str:
        """Generate filename for the QR code."""
        return f"table_{self.table_number}_qr.{self.config.format.value}"
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class GeneratedQRCode(BaseModel):
    """Generated QR code with metadata."""
    
    qr_data: QRCodeData
    file_content: bytes = Field(..., description="Generated QR code file content")
    file_size: int = Field(..., description="File size in bytes")
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Generation timestamp")
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class BulkQRGeneration(BaseModel):
    """Bulk QR code generation request."""
    
    restaurant_id: UUID
    table_ids: List[UUID] = Field(..., description="List of table IDs to generate QR codes for")
    config: QRCodeConfig = Field(default_factory=QRCodeConfig, description="QR code configuration")
    include_zip: bool = Field(default=True, description="Package results in ZIP file")
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class BulkQRResult(BaseModel):
    """Result of bulk QR code generation."""
    
    request_id: str = Field(..., description="Unique request identifier")
    restaurant_id: UUID
    total_requested: int = Field(..., description="Total QR codes requested")
    total_generated: int = Field(..., description="Total QR codes successfully generated")
    failed_tables: List[str] = Field(default_factory=list, description="Table numbers that failed to generate")
    zip_file_content: Optional[bytes] = Field(None, description="ZIP file content if requested")
    zip_file_size: Optional[int] = Field(None, description="ZIP file size in bytes")
    generation_time_seconds: float = Field(..., description="Total generation time")
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Generation timestamp")
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_requested == 0:
            return 0.0
        return (self.total_generated / self.total_requested) * 100
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class QRCodePreview(BaseModel):
    """QR code preview data."""
    
    qr_data: QRCodeData
    preview_url: str = Field(..., description="URL to preview the QR code")
    preview_content: bytes = Field(..., description="Small preview image content")
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class QRGenerationStats(BaseModel):
    """QR code generation statistics."""
    
    restaurant_id: UUID
    total_tables: int = Field(..., description="Total tables in restaurant")
    tables_with_qr: int = Field(..., description="Tables that have QR codes generated")
    tables_without_qr: int = Field(..., description="Tables without QR codes")
    last_generation_date: Optional[datetime] = Field(None, description="Last QR generation date")
    total_generations: int = Field(default=0, description="Total QR codes generated")
    
    @property
    def qr_coverage_percentage(self) -> float:
        """Calculate QR code coverage percentage."""
        if self.total_tables == 0:
            return 0.0
        return (self.tables_with_qr / self.total_tables) * 100
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
