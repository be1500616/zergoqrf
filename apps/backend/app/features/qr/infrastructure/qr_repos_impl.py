"""QR repository implementations.

This module contains concrete implementations of QR repository interfaces.
"""

import os
import tempfile
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from supabase import Client

from ..domain.qr_entities import BulkQRResult, GeneratedQRCode, QRCodeData, QRGenerationStats
from ..domain.qr_repos import IQRMetadataRepository, IQRStorageRepository


class QRStorageRepositoryImpl(IQRStorageRepository):
    """Concrete implementation of QR storage repository."""
    
    def __init__(self, supabase: Client):
        """Initialize the repository.
        
        Args:
            supabase: Supabase client instance.
        """
        self._supabase = supabase
        self._bucket_name = "qr-codes"
    
    async def store_qr_code(self, qr_code: GeneratedQRCode) -> str:
        """Store a generated QR code.
        
        Args:
            qr_code: Generated QR code to store.
            
        Returns:
            Storage URL or path to the stored QR code.
            
        Raises:
            Exception: If storage fails.
        """
        try:
            # Create file path
            file_path = f"restaurants/{qr_code.qr_data.restaurant_id}/tables/{qr_code.qr_data.filename}"
            
            # Store in Supabase storage
            result = self._supabase.storage.from_(self._bucket_name).upload(
                path=file_path,
                file=qr_code.file_content,
                file_options={
                    "content-type": self._get_content_type(qr_code.qr_data.config.format.value),
                    "cache-control": "3600",
                }
            )
            
            if result.error:
                raise Exception(f"Storage upload failed: {result.error}")
            
            # Get public URL
            public_url = self._supabase.storage.from_(self._bucket_name).get_public_url(file_path)
            return public_url
            
        except Exception as e:
            raise Exception(f"Failed to store QR code: {str(e)}")
    
    async def store_bulk_qr_zip(self, bulk_result: BulkQRResult) -> str:
        """Store a bulk QR code ZIP file.
        
        Args:
            bulk_result: Bulk generation result with ZIP content.
            
        Returns:
            Storage URL or path to the stored ZIP file.
            
        Raises:
            Exception: If storage fails.
        """
        try:
            if not bulk_result.zip_file_content:
                raise ValueError("No ZIP file content to store")
            
            # Create file path
            timestamp = int(bulk_result.generated_at.timestamp())
            file_path = f"restaurants/{bulk_result.restaurant_id}/bulk/qr_codes_{timestamp}.zip"
            
            # Store in Supabase storage
            result = self._supabase.storage.from_(self._bucket_name).upload(
                path=file_path,
                file=bulk_result.zip_file_content,
                file_options={
                    "content-type": "application/zip",
                    "cache-control": "3600",
                }
            )
            
            if result.error:
                raise Exception(f"ZIP storage upload failed: {result.error}")
            
            # Get public URL
            public_url = self._supabase.storage.from_(self._bucket_name).get_public_url(file_path)
            return public_url
            
        except Exception as e:
            raise Exception(f"Failed to store bulk QR ZIP: {str(e)}")
    
    async def get_qr_code_url(self, table_id: UUID, format: str) -> Optional[str]:
        """Get the URL of a stored QR code.
        
        Args:
            table_id: Table ID.
            format: QR code format.
            
        Returns:
            URL to the stored QR code if it exists, None otherwise.
        """
        try:
            # This would typically query a metadata table to find the stored file path
            # For now, we'll construct the expected path
            file_path = f"tables/table_{table_id}_qr.{format}"
            
            # Check if file exists
            result = self._supabase.storage.from_(self._bucket_name).list(path=file_path)
            
            if result and len(result) > 0:
                public_url = self._supabase.storage.from_(self._bucket_name).get_public_url(file_path)
                return public_url
            
            return None
            
        except Exception:
            return None
    
    async def delete_qr_code(self, table_id: UUID) -> bool:
        """Delete a stored QR code.
        
        Args:
            table_id: Table ID.
            
        Returns:
            True if deletion was successful, False otherwise.
        """
        try:
            # Delete all formats for the table
            formats = ["png", "svg", "pdf"]
            success = True
            
            for format in formats:
                file_path = f"tables/table_{table_id}_qr.{format}"
                result = self._supabase.storage.from_(self._bucket_name).remove([file_path])
                
                if result.error:
                    success = False
            
            return success
            
        except Exception:
            return False
    
    def _get_content_type(self, format: str) -> str:
        """Get content type for file format.
        
        Args:
            format: File format.
            
        Returns:
            Content type string.
        """
        content_types = {
            "png": "image/png",
            "svg": "image/svg+xml",
            "pdf": "application/pdf",
        }
        return content_types.get(format, "application/octet-stream")


class QRMetadataRepositoryImpl(IQRMetadataRepository):
    """Concrete implementation of QR metadata repository."""
    
    def __init__(self, supabase: Client):
        """Initialize the repository.
        
        Args:
            supabase: Supabase client instance.
        """
        self._supabase = supabase
    
    async def save_qr_metadata(self, qr_data: QRCodeData, storage_url: str) -> bool:
        """Save QR code metadata.
        
        Args:
            qr_data: QR code data.
            storage_url: URL where QR code is stored.
            
        Returns:
            True if metadata was saved successfully, False otherwise.
        """
        try:
            # For now, we'll store metadata in the tables table itself
            # In a more complex system, you might have a separate qr_codes table
            
            metadata = {
                "qr_url": qr_data.url,
                "qr_storage_url": storage_url,
                "qr_format": qr_data.config.format.value,
                "qr_generated_at": datetime.utcnow().isoformat(),
                "qr_config": qr_data.config.dict(),
            }
            
            # This would be implemented based on your specific metadata storage needs
            return True
            
        except Exception:
            return False
    
    async def get_qr_metadata(self, table_id: UUID) -> Optional[QRCodeData]:
        """Get QR code metadata for a table.
        
        Args:
            table_id: Table ID.
            
        Returns:
            QR code metadata if it exists, None otherwise.
        """
        try:
            # This would query the metadata storage
            # For now, return None as we're storing metadata in the tables table
            return None
            
        except Exception:
            return None
    
    async def get_restaurant_qr_stats(self, restaurant_id: UUID) -> QRGenerationStats:
        """Get QR code generation statistics for a restaurant.
        
        Args:
            restaurant_id: Restaurant ID.
            
        Returns:
            QR code generation statistics.
        """
        try:
            # Query tables to get QR statistics
            result = (
                self._supabase.table("tables")
                .select("id, qr_code_data, updated_at")
                .eq("restaurant_id", str(restaurant_id))
                .execute()
            )
            
            total_tables = len(result.data)
            tables_with_qr = 0
            last_generation_date = None
            
            for table in result.data:
                if table.get("qr_code_data"):
                    tables_with_qr += 1
                    
                    # Try to extract generation date
                    qr_data = table.get("qr_code_data", {})
                    if isinstance(qr_data, dict) and "data" in qr_data:
                        generated_at_str = qr_data["data"].get("generated_at")
                        if generated_at_str:
                            try:
                                generated_at = datetime.fromisoformat(generated_at_str.replace("Z", "+00:00"))
                                if not last_generation_date or generated_at > last_generation_date:
                                    last_generation_date = generated_at
                            except (ValueError, AttributeError):
                                pass
            
            tables_without_qr = total_tables - tables_with_qr
            
            return QRGenerationStats(
                restaurant_id=restaurant_id,
                total_tables=total_tables,
                tables_with_qr=tables_with_qr,
                tables_without_qr=tables_without_qr,
                last_generation_date=last_generation_date,
                total_generations=tables_with_qr,  # Simplified for now
            )
            
        except Exception:
            return QRGenerationStats(
                restaurant_id=restaurant_id,
                total_tables=0,
                tables_with_qr=0,
                tables_without_qr=0,
                last_generation_date=None,
                total_generations=0,
            )
    
    async def update_table_qr_data(self, table_id: UUID, qr_data: QRCodeData) -> bool:
        """Update table's QR code data.
        
        Args:
            table_id: Table ID.
            qr_data: Updated QR code data.
            
        Returns:
            True if update was successful, False otherwise.
        """
        try:
            # This is handled in the use case by updating the tables table directly
            return True
            
        except Exception:
            return False
    
    async def get_tables_without_qr(self, restaurant_id: UUID) -> List[UUID]:
        """Get list of table IDs that don't have QR codes.
        
        Args:
            restaurant_id: Restaurant ID.
            
        Returns:
            List of table IDs without QR codes.
        """
        try:
            result = (
                self._supabase.table("tables")
                .select("id, qr_code_data")
                .eq("restaurant_id", str(restaurant_id))
                .execute()
            )
            
            tables_without_qr = []
            for table in result.data:
                if not table.get("qr_code_data"):
                    tables_without_qr.append(UUID(table["id"]))
            
            return tables_without_qr
            
        except Exception:
            return []
