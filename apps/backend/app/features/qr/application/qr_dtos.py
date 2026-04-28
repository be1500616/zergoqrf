"""QR generation Data Transfer Objects (DTOs).

This module contains DTOs for transferring data between application layers.
"""

from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from ..domain.qr_entities import QRErrorCorrection, QRFormat, QRSize


class QRConfigDTO(BaseModel):
    """QR code configuration DTO."""
    
    format: QRFormat = QRFormat.PNG
    size: QRSize = QRSize.MEDIUM
    error_correction: QRErrorCorrection = QRErrorCorrection.MEDIUM
    border: int = Field(default=4, ge=0, le=20)
    include_logo: bool = False
    logo_size_ratio: float = Field(default=0.3, ge=0.1, le=0.5)
    background_color: str = "white"
    foreground_color: str = "black"


class GenerateQRRequestDTO(BaseModel):
    """Request DTO for generating a single QR code."""
    
    table_id: UUID
    config: QRConfigDTO = Field(default_factory=QRConfigDTO)


class GenerateQRResponseDTO(BaseModel):
    """Response DTO for generated QR code."""
    
    table_id: UUID
    table_number: str
    url: str
    filename: str
    file_size: int
    format: QRFormat
    generated_at: datetime


class BulkQRRequestDTO(BaseModel):
    """Request DTO for bulk QR code generation."""
    
    table_ids: Optional[List[UUID]] = Field(None, description="Specific table IDs, or None for all tables")
    config: QRConfigDTO = Field(default_factory=QRConfigDTO)
    include_zip: bool = True


class BulkQRResponseDTO(BaseModel):
    """Response DTO for bulk QR code generation."""
    
    request_id: str
    total_requested: int
    total_generated: int
    failed_tables: List[str]
    success_rate: float
    generation_time_seconds: float
    zip_download_url: Optional[str] = None
    generated_at: datetime


class QRPreviewRequestDTO(BaseModel):
    """Request DTO for QR code preview."""
    
    table_id: UUID
    config: QRConfigDTO = Field(default_factory=QRConfigDTO)


class QRPreviewResponseDTO(BaseModel):
    """Response DTO for QR code preview."""
    
    table_id: UUID
    table_number: str
    url: str
    preview_url: str
    config: QRConfigDTO


class QRStatsDTO(BaseModel):
    """QR code statistics DTO."""
    
    total_tables: int
    tables_with_qr: int
    tables_without_qr: int
    qr_coverage_percentage: float
    last_generation_date: Optional[datetime] = None
    total_generations: int


class TableQRStatusDTO(BaseModel):
    """Table QR code status DTO."""
    
    table_id: UUID
    table_number: str
    has_qr_code: bool
    qr_url: Optional[str] = None
    last_generated: Optional[datetime] = None
    formats_available: List[QRFormat] = Field(default_factory=list)


class QRManagementGridDTO(BaseModel):
    """QR management grid DTO for UI display."""
    
    restaurant_id: UUID
    restaurant_name: str
    restaurant_code: str
    tables: List[TableQRStatusDTO]
    stats: QRStatsDTO


class RegenerateQRRequestDTO(BaseModel):
    """Request DTO for regenerating QR codes."""
    
    table_ids: List[UUID]
    config: QRConfigDTO = Field(default_factory=QRConfigDTO)
    force_regenerate: bool = Field(default=False, description="Force regeneration even if QR exists")


class QRValidationResultDTO(BaseModel):
    """QR code validation result DTO."""
    
    table_id: UUID
    is_scannable: bool
    validation_errors: List[str] = Field(default_factory=list)
    validation_warnings: List[str] = Field(default_factory=list)
    tested_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class QRBatchValidationDTO(BaseModel):
    """Batch QR code validation DTO."""
    
    restaurant_id: UUID
    total_tested: int
    scannable_count: int
    failed_count: int
    validation_results: List[QRValidationResultDTO]
    overall_success_rate: float
