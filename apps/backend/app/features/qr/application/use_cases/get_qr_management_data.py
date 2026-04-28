"""Get QR management data use case.

This module contains the use case for retrieving QR management dashboard data.
"""

from typing import List
from uuid import UUID

from ...domain.qr_repos import IQRMetadataRepository
from ..qr_dtos import QRManagementGridDTO, QRStatsDTO, TableQRStatusDTO
from ....tables.domain.table_repos import ITableRepository
from ....restaurants.domain.restaurant_repos import IRestaurantRepository


class GetQRManagementDataUseCase:
    """Use case for retrieving QR management dashboard data."""
    
    def __init__(
        self,
        qr_metadata_repo: IQRMetadataRepository,
        table_repo: ITableRepository,
        restaurant_repo: IRestaurantRepository,
    ):
        """Initialize the use case.
        
        Args:
            qr_metadata_repo: QR metadata repository.
            table_repo: Table repository.
            restaurant_repo: Restaurant repository.
        """
        self._qr_metadata_repo = qr_metadata_repo
        self._table_repo = table_repo
        self._restaurant_repo = restaurant_repo
    
    async def execute(self, restaurant_id: UUID) -> QRManagementGridDTO:
        """Execute the get QR management data use case.
        
        Args:
            restaurant_id: Restaurant ID.
            
        Returns:
            QR management grid data.
            
        Raises:
            ValueError: If restaurant not found.
        """
        # Get restaurant information
        restaurant = await self._restaurant_repo.get_restaurant_by_id(restaurant_id)
        if not restaurant:
            raise ValueError(f"Restaurant with ID {restaurant_id} not found")
        
        # Get all tables for the restaurant
        tables = await self._table_repo.get_tables_by_restaurant(restaurant_id)
        
        # Get QR statistics
        qr_stats = await self._qr_metadata_repo.get_restaurant_qr_stats(restaurant_id)
        
        # Build table QR status list
        table_statuses: List[TableQRStatusDTO] = []
        
        for table in tables:
            has_qr_code = table.qr_code_data is not None
            qr_url = None
            last_generated = None
            formats_available = []
            
            if has_qr_code and table.qr_code_data:
                qr_url = table.qr_code_data.url
                if table.qr_code_data.data and "generated_at" in table.qr_code_data.data:
                    try:
                        from datetime import datetime
                        last_generated = datetime.fromisoformat(
                            table.qr_code_data.data["generated_at"].replace("Z", "+00:00")
                        )
                    except (ValueError, KeyError):
                        pass
                
                if table.qr_code_data.data and "format" in table.qr_code_data.data:
                    from ...domain.qr_entities import QRFormat
                    try:
                        format_value = table.qr_code_data.data["format"]
                        formats_available = [QRFormat(format_value)]
                    except (ValueError, KeyError):
                        pass
            
            table_status = TableQRStatusDTO(
                table_id=table.id,
                table_number=table.table_number,
                has_qr_code=has_qr_code,
                qr_url=qr_url,
                last_generated=last_generated,
                formats_available=formats_available,
            )
            table_statuses.append(table_status)
        
        # Convert QR stats to DTO
        stats_dto = QRStatsDTO(
            total_tables=qr_stats.total_tables,
            tables_with_qr=qr_stats.tables_with_qr,
            tables_without_qr=qr_stats.tables_without_qr,
            qr_coverage_percentage=qr_stats.qr_coverage_percentage,
            last_generation_date=qr_stats.last_generation_date,
            total_generations=qr_stats.total_generations,
        )
        
        return QRManagementGridDTO(
            restaurant_id=restaurant_id,
            restaurant_name=restaurant.name,
            restaurant_code=restaurant.code,
            tables=table_statuses,
            stats=stats_dto,
        )
