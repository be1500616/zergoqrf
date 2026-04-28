"""Generate bulk QR codes use case.

This module contains the use case for generating QR codes for multiple tables.
"""

import asyncio
import time
import uuid
from typing import List
from uuid import UUID

from ...domain.qr_entities import BulkQRGeneration, QRCodeConfig, QRCodeData
from ...domain.qr_repos import IQRGenerationRepository, IQRMetadataRepository, IQRStorageRepository
from ..qr_dtos import BulkQRRequestDTO, BulkQRResponseDTO
from ....tables.domain.table_repos import ITableRepository
from ....restaurants.domain.restaurant_repos import IRestaurantRepository


class GenerateBulkQRUseCase:
    """Use case for generating QR codes for multiple tables."""
    
    def __init__(
        self,
        qr_generation_repo: IQRGenerationRepository,
        qr_storage_repo: IQRStorageRepository,
        qr_metadata_repo: IQRMetadataRepository,
        table_repo: ITableRepository,
        restaurant_repo: IRestaurantRepository,
    ):
        """Initialize the use case.
        
        Args:
            qr_generation_repo: QR generation repository.
            qr_storage_repo: QR storage repository.
            qr_metadata_repo: QR metadata repository.
            table_repo: Table repository.
            restaurant_repo: Restaurant repository.
        """
        self._qr_generation_repo = qr_generation_repo
        self._qr_storage_repo = qr_storage_repo
        self._table_repo = table_repo
        self._restaurant_repo = restaurant_repo
        self._qr_metadata_repo = qr_metadata_repo
    
    async def execute(self, restaurant_id: UUID, request: BulkQRRequestDTO) -> BulkQRResponseDTO:
        """Execute the bulk QR generation use case.
        
        Args:
            restaurant_id: Restaurant ID.
            request: Bulk QR generation request.
            
        Returns:
            Bulk QR generation response.
            
        Raises:
            ValueError: If restaurant not found.
            Exception: If bulk generation fails.
        """
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        # Get restaurant information
        restaurant = await self._restaurant_repo.get_restaurant_by_id(restaurant_id)
        if not restaurant:
            raise ValueError(f"Restaurant with ID {restaurant_id} not found")
        
        # Determine which tables to generate QR codes for
        if request.table_ids:
            # Validate that all tables belong to the restaurant
            tables = []
            for table_id in request.table_ids:
                table = await self._table_repo.get_table_by_id(table_id)
                if not table:
                    continue
                if table.restaurant_id != restaurant_id:
                    continue
                tables.append(table)
        else:
            # Generate for all tables in the restaurant
            tables = await self._table_repo.get_tables_by_restaurant(restaurant_id)
        
        if not tables:
            return BulkQRResponseDTO(
                request_id=request_id,
                total_requested=0,
                total_generated=0,
                failed_tables=[],
                success_rate=0.0,
                generation_time_seconds=time.time() - start_time,
                zip_download_url=None,
                generated_at=time.time(),
            )
        
        # Create QR code configuration
        qr_config = QRCodeConfig(
            format=request.config.format,
            size=request.config.size,
            error_correction=request.config.error_correction,
            border=request.config.border,
            include_logo=request.config.include_logo,
            logo_size_ratio=request.config.logo_size_ratio,
            background_color=request.config.background_color,
            foreground_color=request.config.foreground_color,
        )
        
        # Create bulk generation request
        table_ids = [table.id for table in tables]
        bulk_request = BulkQRGeneration(
            restaurant_id=restaurant_id,
            table_ids=table_ids,
            config=qr_config,
            include_zip=request.include_zip,
        )
        
        # Generate QR codes in bulk
        bulk_result = await self._qr_generation_repo.generate_bulk_qr_codes(bulk_request)
        
        # Store ZIP file if generated
        zip_download_url = None
        if bulk_result.zip_file_content and request.include_zip:
            zip_download_url = await self._qr_storage_repo.store_bulk_qr_zip(bulk_result)
        
        # Update table metadata for successfully generated QR codes
        await self._update_table_metadata(tables, restaurant, bulk_result, qr_config)
        
        generation_time = time.time() - start_time
        
        return BulkQRResponseDTO(
            request_id=request_id,
            total_requested=bulk_result.total_requested,
            total_generated=bulk_result.total_generated,
            failed_tables=bulk_result.failed_tables,
            success_rate=bulk_result.success_rate,
            generation_time_seconds=generation_time,
            zip_download_url=zip_download_url,
            generated_at=bulk_result.generated_at,
        )
    
    async def _update_table_metadata(self, tables, restaurant, bulk_result, qr_config):
        """Update table metadata for successfully generated QR codes.
        
        Args:
            tables: List of table entities.
            restaurant: Restaurant entity.
            bulk_result: Bulk generation result.
            qr_config: QR code configuration.
        """
        failed_table_numbers = set(bulk_result.failed_tables)
        
        update_tasks = []
        for table in tables:
            if table.table_number in failed_table_numbers:
                continue
            
            qr_url = f"https://app.zergoqrf.com/menu/{restaurant.code}/{table.id}"
            
            update_data = {
                "qr_token": f"{restaurant.code}_{table.id}",
                "qr_code_data": {
                    "token": f"{restaurant.code}_{table.id}",
                    "url": qr_url,
                    "data": {
                        "restaurant_id": str(restaurant.id),
                        "restaurant_code": restaurant.code,
                        "table_id": str(table.id),
                        "table_number": table.table_number,
                        "generated_at": bulk_result.generated_at.isoformat(),
                        "format": qr_config.format.value,
                        "bulk_request_id": bulk_result.request_id,
                    }
                }
            }
            
            update_tasks.append(
                self._table_repo.update_table(table.id, update_data)
            )
        
        # Execute all updates concurrently
        if update_tasks:
            await asyncio.gather(*update_tasks, return_exceptions=True)
