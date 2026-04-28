"""QR generation FastAPI router.

This module contains the FastAPI router for QR code generation endpoints.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import StreamingResponse
from supabase import Client

from app.common.supabase_client import get_supabase
from app.security import get_current_user_restaurant_id

from ..application.use_cases.generate_qr_code import GenerateQRCodeUseCase
from ..application.use_cases.generate_bulk_qr import GenerateBulkQRUseCase
from ..application.use_cases.get_qr_management_data import GetQRManagementDataUseCase
from ..infrastructure.qr_generation_service import QRGenerationService
from ..infrastructure.qr_repos_impl import QRMetadataRepositoryImpl, QRStorageRepositoryImpl
from ...tables.infrastructure.table_repos_impl import TableRepositoryImpl
from ...restaurants.infrastructure.restaurant_repos_impl import RestaurantRepositoryImpl
from .qr_schemas import (
    BulkQRGenerateSchema,
    BulkQRResponseSchema,
    ErrorResponseSchema,
    GenerateQRSchema,
    QRManagementGridSchema,
    QRPreviewResponseSchema,
    QRPreviewSchema,
    QRResponseSchema,
    RegenerateQRSchema,
)

router = APIRouter(prefix="/qr", tags=["QR Codes"])


# Dependency injection functions
def get_qr_generation_service() -> QRGenerationService:
    """Get QR generation service instance."""
    return QRGenerationService()


def get_qr_storage_repo(supabase: Client = Depends(get_supabase)) -> QRStorageRepositoryImpl:
    """Get QR storage repository instance."""
    return QRStorageRepositoryImpl(supabase)


def get_qr_metadata_repo(supabase: Client = Depends(get_supabase)) -> QRMetadataRepositoryImpl:
    """Get QR metadata repository instance."""
    return QRMetadataRepositoryImpl(supabase)


def get_table_repository(supabase: Client = Depends(get_supabase)) -> TableRepositoryImpl:
    """Get table repository instance."""
    return TableRepositoryImpl(supabase)


def get_restaurant_repository(supabase: Client = Depends(get_supabase)) -> RestaurantRepositoryImpl:
    """Get restaurant repository instance."""
    return RestaurantRepositoryImpl(supabase)


def get_generate_qr_use_case(
    qr_generation_service: QRGenerationService = Depends(get_qr_generation_service),
    qr_storage_repo: QRStorageRepositoryImpl = Depends(get_qr_storage_repo),
    qr_metadata_repo: QRMetadataRepositoryImpl = Depends(get_qr_metadata_repo),
    table_repo: TableRepositoryImpl = Depends(get_table_repository),
    restaurant_repo: RestaurantRepositoryImpl = Depends(get_restaurant_repository),
) -> GenerateQRCodeUseCase:
    """Get generate QR code use case instance."""
    return GenerateQRCodeUseCase(
        qr_generation_service,
        qr_storage_repo,
        qr_metadata_repo,
        table_repo,
        restaurant_repo,
    )


def get_generate_bulk_qr_use_case(
    qr_generation_service: QRGenerationService = Depends(get_qr_generation_service),
    qr_storage_repo: QRStorageRepositoryImpl = Depends(get_qr_storage_repo),
    qr_metadata_repo: QRMetadataRepositoryImpl = Depends(get_qr_metadata_repo),
    table_repo: TableRepositoryImpl = Depends(get_table_repository),
    restaurant_repo: RestaurantRepositoryImpl = Depends(get_restaurant_repository),
) -> GenerateBulkQRUseCase:
    """Get generate bulk QR use case instance."""
    return GenerateBulkQRUseCase(
        qr_generation_service,
        qr_storage_repo,
        qr_metadata_repo,
        table_repo,
        restaurant_repo,
    )


def get_qr_management_use_case(
    qr_metadata_repo: QRMetadataRepositoryImpl = Depends(get_qr_metadata_repo),
    table_repo: TableRepositoryImpl = Depends(get_table_repository),
    restaurant_repo: RestaurantRepositoryImpl = Depends(get_restaurant_repository),
) -> GetQRManagementDataUseCase:
    """Get QR management data use case instance."""
    return GetQRManagementDataUseCase(
        qr_metadata_repo,
        table_repo,
        restaurant_repo,
    )


# QR Code Generation Endpoints

@router.post("/generate", response_model=QRResponseSchema, status_code=status.HTTP_201_CREATED)
async def generate_qr_code(
    request: GenerateQRSchema,
    restaurant_id: UUID = Depends(get_current_user_restaurant_id),
    use_case: GenerateQRCodeUseCase = Depends(get_generate_qr_use_case),
):
    """Generate a QR code for a single table.
    
    Args:
        request: QR generation request.
        restaurant_id: Current user's restaurant ID.
        use_case: Generate QR code use case.
        
    Returns:
        Generated QR code information.
        
    Raises:
        HTTPException: If QR generation fails.
    """
    try:
        from ..application.qr_dtos import GenerateQRRequestDTO, QRConfigDTO
        
        # Convert schema to DTO
        config_dto = QRConfigDTO(
            format=request.config.format,
            size=request.config.size,
            error_correction=request.config.error_correction,
            border=request.config.border,
            include_logo=request.config.include_logo,
            logo_size_ratio=request.config.logo_size_ratio,
            background_color=request.config.background_color,
            foreground_color=request.config.foreground_color,
        )
        
        request_dto = GenerateQRRequestDTO(
            table_id=request.table_id,
            config=config_dto,
        )
        
        result = await use_case.execute(restaurant_id, request_dto)
        
        return QRResponseSchema(
            table_id=result.table_id,
            table_number=result.table_number,
            url=result.url,
            filename=result.filename,
            file_size=result.file_size,
            format=result.format,
            generated_at=result.generated_at,
        )
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/generate/bulk", response_model=BulkQRResponseSchema, status_code=status.HTTP_201_CREATED)
async def generate_bulk_qr_codes(
    request: BulkQRGenerateSchema,
    restaurant_id: UUID = Depends(get_current_user_restaurant_id),
    use_case: GenerateBulkQRUseCase = Depends(get_generate_bulk_qr_use_case),
):
    """Generate QR codes for multiple tables.
    
    Args:
        request: Bulk QR generation request.
        restaurant_id: Current user's restaurant ID.
        use_case: Generate bulk QR use case.
        
    Returns:
        Bulk QR generation result.
        
    Raises:
        HTTPException: If bulk generation fails.
    """
    try:
        from ..application.qr_dtos import BulkQRRequestDTO, QRConfigDTO
        
        # Convert schema to DTO
        config_dto = QRConfigDTO(
            format=request.config.format,
            size=request.config.size,
            error_correction=request.config.error_correction,
            border=request.config.border,
            include_logo=request.config.include_logo,
            logo_size_ratio=request.config.logo_size_ratio,
            background_color=request.config.background_color,
            foreground_color=request.config.foreground_color,
        )
        
        request_dto = BulkQRRequestDTO(
            table_ids=request.table_ids,
            config=config_dto,
            include_zip=request.include_zip,
        )
        
        result = await use_case.execute(restaurant_id, request_dto)
        
        return BulkQRResponseSchema(
            request_id=result.request_id,
            total_requested=result.total_requested,
            total_generated=result.total_generated,
            failed_tables=result.failed_tables,
            success_rate=result.success_rate,
            generation_time_seconds=result.generation_time_seconds,
            zip_download_url=result.zip_download_url,
            generated_at=result.generated_at,
        )
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/preview", response_model=QRPreviewResponseSchema)
async def preview_qr_code(
    request: QRPreviewSchema,
    restaurant_id: UUID = Depends(get_current_user_restaurant_id),
    qr_generation_service: QRGenerationService = Depends(get_qr_generation_service),
    table_repo: TableRepositoryImpl = Depends(get_table_repository),
    restaurant_repo: RestaurantRepositoryImpl = Depends(get_restaurant_repository),
):
    """Generate a preview of a QR code.
    
    Args:
        request: QR preview request.
        restaurant_id: Current user's restaurant ID.
        qr_generation_service: QR generation service.
        table_repo: Table repository.
        restaurant_repo: Restaurant repository.
        
    Returns:
        QR code preview data.
        
    Raises:
        HTTPException: If preview generation fails.
    """
    try:
        # Get table and restaurant information
        table = await table_repo.get_table_by_id(request.table_id)
        if not table or table.restaurant_id != restaurant_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")
        
        restaurant = await restaurant_repo.get_restaurant_by_id(restaurant_id)
        if not restaurant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")
        
        # Create QR data for preview
        from ..domain.qr_entities import QRCodeConfig, QRCodeData
        
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
        
        qr_url = f"https://app.zergoqrf.com/menu/{restaurant.code}/{table.id}"
        
        qr_data = QRCodeData(
            url=qr_url,
            table_id=table.id,
            restaurant_id=restaurant_id,
            restaurant_code=restaurant.code,
            table_number=table.table_number,
            config=qr_config,
        )
        
        # Generate preview
        preview = await qr_generation_service.generate_qr_preview(qr_data)
        
        return QRPreviewResponseSchema(
            table_id=table.id,
            table_number=table.table_number,
            url=qr_url,
            preview_data_url=preview.preview_url,
            config=request.config,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/management", response_model=QRManagementGridSchema)
async def get_qr_management_data(
    restaurant_id: UUID = Depends(get_current_user_restaurant_id),
    use_case: GetQRManagementDataUseCase = Depends(get_qr_management_use_case),
):
    """Get QR code management dashboard data.
    
    Args:
        restaurant_id: Current user's restaurant ID.
        use_case: QR management data use case.
        
    Returns:
        QR management grid data.
        
    Raises:
        HTTPException: If data retrieval fails.
    """
    try:
        result = await use_case.execute(restaurant_id)
        
        return QRManagementGridSchema(
            restaurant_id=result.restaurant_id,
            restaurant_name=result.restaurant_name,
            restaurant_code=result.restaurant_code,
            tables=[
                {
                    "table_id": table.table_id,
                    "table_number": table.table_number,
                    "has_qr_code": table.has_qr_code,
                    "qr_url": table.qr_url,
                    "last_generated": table.last_generated,
                    "formats_available": table.formats_available,
                }
                for table in result.tables
            ],
            stats={
                "total_tables": result.stats.total_tables,
                "tables_with_qr": result.stats.tables_with_qr,
                "tables_without_qr": result.stats.tables_without_qr,
                "qr_coverage_percentage": result.stats.qr_coverage_percentage,
                "last_generation_date": result.stats.last_generation_date,
                "total_generations": result.stats.total_generations,
            },
        )
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
