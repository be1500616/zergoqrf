"""QR generation repository interfaces.

This module contains abstract repository interfaces for QR code generation.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from .qr_entities import (
    BulkQRGeneration,
    BulkQRResult,
    GeneratedQRCode,
    QRCodeConfig,
    QRCodeData,
    QRCodePreview,
    QRGenerationStats,
)


class IQRGenerationRepository(ABC):
    """Abstract repository interface for QR code generation."""
    
    @abstractmethod
    async def generate_qr_code(self, qr_data: QRCodeData) -> GeneratedQRCode:
        """Generate a single QR code.
        
        Args:
            qr_data: QR code data and configuration.
            
        Returns:
            Generated QR code with metadata.
            
        Raises:
            Exception: If QR code generation fails.
        """
        pass
    
    @abstractmethod
    async def generate_bulk_qr_codes(self, bulk_request: BulkQRGeneration) -> BulkQRResult:
        """Generate QR codes for multiple tables.
        
        Args:
            bulk_request: Bulk generation request.
            
        Returns:
            Bulk generation result with statistics.
            
        Raises:
            Exception: If bulk generation fails.
        """
        pass
    
    @abstractmethod
    async def generate_qr_preview(self, qr_data: QRCodeData) -> QRCodePreview:
        """Generate a preview of the QR code.
        
        Args:
            qr_data: QR code data and configuration.
            
        Returns:
            QR code preview data.
            
        Raises:
            Exception: If preview generation fails.
        """
        pass
    
    @abstractmethod
    async def validate_qr_scannability(self, qr_code: GeneratedQRCode) -> bool:
        """Validate that a QR code is scannable.
        
        Args:
            qr_code: Generated QR code to validate.
            
        Returns:
            True if QR code is scannable, False otherwise.
        """
        pass


class IQRStorageRepository(ABC):
    """Abstract repository interface for QR code storage."""
    
    @abstractmethod
    async def store_qr_code(self, qr_code: GeneratedQRCode) -> str:
        """Store a generated QR code.
        
        Args:
            qr_code: Generated QR code to store.
            
        Returns:
            Storage URL or path to the stored QR code.
            
        Raises:
            Exception: If storage fails.
        """
        pass
    
    @abstractmethod
    async def store_bulk_qr_zip(self, bulk_result: BulkQRResult) -> str:
        """Store a bulk QR code ZIP file.
        
        Args:
            bulk_result: Bulk generation result with ZIP content.
            
        Returns:
            Storage URL or path to the stored ZIP file.
            
        Raises:
            Exception: If storage fails.
        """
        pass
    
    @abstractmethod
    async def get_qr_code_url(self, table_id: UUID, format: str) -> Optional[str]:
        """Get the URL of a stored QR code.
        
        Args:
            table_id: Table ID.
            format: QR code format.
            
        Returns:
            URL to the stored QR code if it exists, None otherwise.
        """
        pass
    
    @abstractmethod
    async def delete_qr_code(self, table_id: UUID) -> bool:
        """Delete a stored QR code.
        
        Args:
            table_id: Table ID.
            
        Returns:
            True if deletion was successful, False otherwise.
        """
        pass


class IQRMetadataRepository(ABC):
    """Abstract repository interface for QR code metadata management."""
    
    @abstractmethod
    async def save_qr_metadata(self, qr_data: QRCodeData, storage_url: str) -> bool:
        """Save QR code metadata.
        
        Args:
            qr_data: QR code data.
            storage_url: URL where QR code is stored.
            
        Returns:
            True if metadata was saved successfully, False otherwise.
        """
        pass
    
    @abstractmethod
    async def get_qr_metadata(self, table_id: UUID) -> Optional[QRCodeData]:
        """Get QR code metadata for a table.
        
        Args:
            table_id: Table ID.
            
        Returns:
            QR code metadata if it exists, None otherwise.
        """
        pass
    
    @abstractmethod
    async def get_restaurant_qr_stats(self, restaurant_id: UUID) -> QRGenerationStats:
        """Get QR code generation statistics for a restaurant.
        
        Args:
            restaurant_id: Restaurant ID.
            
        Returns:
            QR code generation statistics.
        """
        pass
    
    @abstractmethod
    async def update_table_qr_data(self, table_id: UUID, qr_data: QRCodeData) -> bool:
        """Update table's QR code data.
        
        Args:
            table_id: Table ID.
            qr_data: Updated QR code data.
            
        Returns:
            True if update was successful, False otherwise.
        """
        pass
    
    @abstractmethod
    async def get_tables_without_qr(self, restaurant_id: UUID) -> List[UUID]:
        """Get list of table IDs that don't have QR codes.
        
        Args:
            restaurant_id: Restaurant ID.
            
        Returns:
            List of table IDs without QR codes.
        """
        pass
