"""QR generation Pydantic schemas.

This module contains Pydantic schemas for API request/response validation.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from ..domain.qr_entities import QRErrorCorrection, QRFormat, QRSize


class QRConfigSchema(BaseModel):
    """QR code configuration schema."""
    
    format: QRFormat = Field(default=QRFormat.PNG, description="QR code output format")
    size: QRSize = Field(default=QRSize.MEDIUM, description="QR code size preset")
    error_correction: QRErrorCorrection = Field(default=QRErrorCorrection.MEDIUM, description="Error correction level")
    border: int = Field(default=4, ge=0, le=20, description="Border size in modules")
    include_logo: bool = Field(default=False, description="Include restaurant logo in center")
    logo_size_ratio: float = Field(default=0.3, ge=0.1, le=0.5, description="Logo size as ratio of QR code")
    background_color: str = Field(default="white", description="Background color")
    foreground_color: str = Field(default="black", description="Foreground color")


class GenerateQRSchema(BaseModel):
    """Schema for generating a single QR code."""
    
    table_id: UUID = Field(..., description="Table ID to generate QR code for")
    config: QRConfigSchema = Field(default_factory=QRConfigSchema, description="QR code configuration")


class QRResponseSchema(BaseModel):
    """Schema for QR code generation response."""
    
    table_id: UUID
    table_number: str
    url: str = Field(..., description="The URL encoded in the QR code")
    filename: str = Field(..., description="Generated filename")
    file_size: int = Field(..., description="File size in bytes")
    format: QRFormat
    download_url: Optional[str] = Field(None, description="URL to download the QR code")
    generated_at: datetime
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class BulkQRGenerateSchema(BaseModel):
    """Schema for bulk QR code generation."""
    
    table_ids: Optional[List[UUID]] = Field(None, description="Specific table IDs, or None for all tables")
    config: QRConfigSchema = Field(default_factory=QRConfigSchema, description="QR code configuration")
    include_zip: bool = Field(default=True, description="Package results in ZIP file")


class BulkQRResponseSchema(BaseModel):
    """Schema for bulk QR code generation response."""
    
    request_id: str
    total_requested: int
    total_generated: int
    failed_tables: List[str]
    success_rate: float = Field(..., description="Success rate percentage")
    generation_time_seconds: float
    zip_download_url: Optional[str] = Field(None, description="URL to download ZIP file")
    individual_qr_codes: List[QRResponseSchema] = Field(default_factory=list, description="Individual QR code details")
    generated_at: datetime
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class QRPreviewSchema(BaseModel):
    """Schema for QR code preview request."""
    
    table_id: UUID = Field(..., description="Table ID to preview QR code for")
    config: QRConfigSchema = Field(default_factory=QRConfigSchema, description="QR code configuration")


class QRPreviewResponseSchema(BaseModel):
    """Schema for QR code preview response."""
    
    table_id: UUID
    table_number: str
    url: str = Field(..., description="The URL that will be encoded in the QR code")
    preview_data_url: str = Field(..., description="Data URL for preview image")
    config: QRConfigSchema
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class TableQRStatusSchema(BaseModel):
    """Schema for table QR code status."""
    
    table_id: UUID
    table_number: str
    has_qr_code: bool
    qr_url: Optional[str] = None
    last_generated: Optional[datetime] = None
    formats_available: List[QRFormat] = Field(default_factory=list)
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class QRStatsSchema(BaseModel):
    """Schema for QR code statistics."""
    
    total_tables: int
    tables_with_qr: int
    tables_without_qr: int
    qr_coverage_percentage: float
    last_generation_date: Optional[datetime] = None
    total_generations: int
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class QRManagementGridSchema(BaseModel):
    """Schema for QR management grid response."""
    
    restaurant_id: UUID
    restaurant_name: str
    restaurant_code: str
    tables: List[TableQRStatusSchema]
    stats: QRStatsSchema
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class RegenerateQRSchema(BaseModel):
    """Schema for regenerating QR codes."""
    
    table_ids: List[UUID] = Field(..., description="Table IDs to regenerate QR codes for")
    config: QRConfigSchema = Field(default_factory=QRConfigSchema, description="QR code configuration")
    force_regenerate: bool = Field(default=False, description="Force regeneration even if QR exists")


class QRValidationSchema(BaseModel):
    """Schema for QR code validation request."""
    
    table_ids: Optional[List[UUID]] = Field(None, description="Specific table IDs to validate, or None for all")


class QRValidationResultSchema(BaseModel):
    """Schema for QR code validation result."""
    
    table_id: UUID
    table_number: str
    is_scannable: bool
    validation_errors: List[str] = Field(default_factory=list)
    validation_warnings: List[str] = Field(default_factory=list)
    tested_at: datetime
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class QRBatchValidationResponseSchema(BaseModel):
    """Schema for batch QR code validation response."""
    
    restaurant_id: UUID
    total_tested: int
    scannable_count: int
    failed_count: int
    validation_results: List[QRValidationResultSchema]
    overall_success_rate: float
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class QRDownloadSchema(BaseModel):
    """Schema for QR code download request."""
    
    table_id: UUID = Field(..., description="Table ID")
    format: QRFormat = Field(default=QRFormat.PNG, description="Desired format")


class ErrorResponseSchema(BaseModel):
    """Schema for error responses."""
    
    error: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Additional error details")
    code: Optional[str] = Field(None, description="Error code")
