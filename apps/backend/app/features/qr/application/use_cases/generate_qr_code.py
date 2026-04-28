"""Generate QR code use case.

This module contains the use case for generating individual QR codes.
"""

import time
from uuid import UUID

from ...domain.qr_entities import QRCodeConfig, QRCodeData
from ...domain.qr_repos import IQRGenerationRepository, IQRMetadataRepository, IQRStorageRepository
from ..qr_dtos import GenerateQRRequestDTO, GenerateQRResponseDTO
from ....tables.domain.table_repos import ITableRepository
from ....restaurants.domain.restaurant_repos import IRestaurantRepository


class GenerateQRCodeUseCase:
    """Use case for generating individual QR codes."""
    
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
        self._qr_metadata_repo = qr_metadata_repo
        self._table_repo = table_repo
        self._restaurant_repo = restaurant_repo
    
    async def execute(self, restaurant_id: UUID, request: GenerateQRRequestDTO) -> GenerateQRResponseDTO:
        """Execute the generate QR code use case.
        
        Args:
            restaurant_id: Restaurant ID.
            request: QR generation request.
            
        Returns:
            Generated QR code response.
            
        Raises:
            ValueError: If table not found or doesn't belong to restaurant.
            Exception: If QR generation fails.
        """
        start_time = time.time()
        
        # Get table information
        table = await self._table_repo.get_table_by_id(request.table_id)
        if not table:
            raise ValueError(f"Table with ID {request.table_id} not found")
        
        if table.restaurant_id != restaurant_id:
            raise ValueError("Table does not belong to the specified restaurant")
        
        # Get restaurant information
        restaurant = await self._restaurant_repo.get_restaurant_by_id(restaurant_id)
        if not restaurant:
            raise ValueError(f"Restaurant with ID {restaurant_id} not found")
        
        # Create QR code data
        qr_url = f"https://app.zergoqrf.com/menu/{restaurant.code}/{table.id}"
        
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
        
        qr_data = QRCodeData(
            url=qr_url,
            table_id=table.id,
            restaurant_id=restaurant_id,
            restaurant_code=restaurant.code,
            table_number=table.table_number,
            config=qr_config,
        )
        
        # Generate QR code
        generated_qr = await self._qr_generation_repo.generate_qr_code(qr_data)
        
        # Store QR code
        storage_url = await self._qr_storage_repo.store_qr_code(generated_qr)
        
        # Save metadata
        await self._qr_metadata_repo.save_qr_metadata(qr_data, storage_url)
        
        # Update table with QR code data
        await self._table_repo.update_table(
            table.id,
            {
                "qr_token": f"{restaurant.code}_{table.id}",
                "qr_code_data": {
                    "token": f"{restaurant.code}_{table.id}",
                    "url": qr_url,
                    "data": {
                        "restaurant_id": str(restaurant_id),
                        "restaurant_code": restaurant.code,
                        "table_id": str(table.id),
                        "table_number": table.table_number,
                        "generated_at": generated_qr.generated_at.isoformat(),
                        "format": qr_config.format.value,
                        "storage_url": storage_url,
                    }
                }
            }
        )
        
        generation_time = time.time() - start_time
        
        return GenerateQRResponseDTO(
            table_id=table.id,
            table_number=table.table_number,
            url=qr_url,
            filename=qr_data.filename,
            file_size=generated_qr.file_size,
            format=qr_config.format,
            generated_at=generated_qr.generated_at,
        )
