"""Table management FastAPI router.

This module contains the FastAPI router for table management endpoints.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from supabase import Client

from app.common.supabase_client import get_supabase
from app.security import get_current_user_restaurant_id

from ..application.use_cases.create_table import CreateTableUseCase
from ..application.use_cases.get_tables import GetTablesUseCase
from ..application.use_cases.manage_floor_plan import ManageFloorPlanUseCase
from ..application.use_cases.update_table import UpdateTableUseCase
from ..application.use_cases.update_table_status import UpdateTableStatusUseCase
from ..domain.table_entities import TableStatus
from ..infrastructure.table_repos_impl import (
    FloorRepositoryImpl,
    TableRepositoryImpl,
)
from .table_schemas import (
    CreateFloorSchema,
    CreateTableSchema,
    FloorPlanResponseSchema,
    FloorResponseSchema,
    TableOccupancyStatsSchema,
    TableResponseSchema,
    UpdateFloorSchema,
    UpdateTableSchema,
    UpdateTableStatusSchema,
)

router = APIRouter(prefix="/tables", tags=["Tables"])


# Dependency injection functions
def get_floor_repository(supabase: Client = Depends(get_supabase)) -> FloorRepositoryImpl:
    """Get floor repository instance."""
    return FloorRepositoryImpl(supabase)


def get_table_repository(supabase: Client = Depends(get_supabase)) -> TableRepositoryImpl:
    """Get table repository instance."""
    return TableRepositoryImpl(supabase)


def get_create_table_use_case(
    table_repo: TableRepositoryImpl = Depends(get_table_repository)
) -> CreateTableUseCase:
    """Get create table use case instance."""
    return CreateTableUseCase(table_repo)


def get_get_tables_use_case(
    table_repo: TableRepositoryImpl = Depends(get_table_repository)
) -> GetTablesUseCase:
    """Get tables use case instance."""
    return GetTablesUseCase(table_repo)


def get_update_table_use_case(
    table_repo: TableRepositoryImpl = Depends(get_table_repository)
) -> UpdateTableUseCase:
    """Get update table use case instance."""
    return UpdateTableUseCase(table_repo)


def get_update_table_status_use_case(
    table_repo: TableRepositoryImpl = Depends(get_table_repository)
) -> UpdateTableStatusUseCase:
    """Get update table status use case instance."""
    return UpdateTableStatusUseCase(table_repo)


def get_manage_floor_plan_use_case(
    floor_repo: FloorRepositoryImpl = Depends(get_floor_repository),
    table_repo: TableRepositoryImpl = Depends(get_table_repository)
) -> ManageFloorPlanUseCase:
    """Get manage floor plan use case instance."""
    return ManageFloorPlanUseCase(floor_repo, table_repo)


# Floor management endpoints
@router.post("/floors", response_model=FloorResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_floor(
    floor_data: CreateFloorSchema,
    restaurant_id: UUID = Depends(get_current_user_restaurant_id),
    use_case: ManageFloorPlanUseCase = Depends(get_manage_floor_plan_use_case)
):
    """Create a new floor.
    
    Args:
        floor_data: Floor creation data.
        restaurant_id: Current user's restaurant ID.
        use_case: Floor management use case.
        
    Returns:
        Created floor information.
        
    Raises:
        HTTPException: If floor creation fails.
    """
    try:
        floor_dto = await use_case.create_floor(restaurant_id, floor_data)
        return FloorResponseSchema(**floor_dto.dict())
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/floors", response_model=List[FloorResponseSchema])
async def get_floors(
    restaurant_id: UUID = Depends(get_current_user_restaurant_id),
    use_case: ManageFloorPlanUseCase = Depends(get_manage_floor_plan_use_case)
):
    """Get all floors for the restaurant.
    
    Args:
        restaurant_id: Current user's restaurant ID.
        use_case: Floor management use case.
        
    Returns:
        List of floors.
    """
    floor_dtos = await use_case.get_floors_by_restaurant(restaurant_id)
    return [FloorResponseSchema(**floor_dto.dict()) for floor_dto in floor_dtos]


@router.get("/floors/{floor_id}", response_model=FloorResponseSchema)
async def get_floor(
    floor_id: UUID,
    restaurant_id: UUID = Depends(get_current_user_restaurant_id),
    use_case: ManageFloorPlanUseCase = Depends(get_manage_floor_plan_use_case)
):
    """Get floor by ID.
    
    Args:
        floor_id: Floor ID.
        restaurant_id: Current user's restaurant ID.
        use_case: Floor management use case.
        
    Returns:
        Floor information.
        
    Raises:
        HTTPException: If floor not found.
    """
    floor_dto = await use_case.get_floor_by_id(floor_id)
    if not floor_dto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Floor not found")
    
    # Verify floor belongs to restaurant
    if floor_dto.restaurant_id != restaurant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    return FloorResponseSchema(**floor_dto.dict())


@router.get("/floors/{floor_id}/plan", response_model=FloorPlanResponseSchema)
async def get_floor_plan(
    floor_id: UUID,
    restaurant_id: UUID = Depends(get_current_user_restaurant_id),
    use_case: ManageFloorPlanUseCase = Depends(get_manage_floor_plan_use_case)
):
    """Get complete floor plan with tables and occupancy stats.
    
    Args:
        floor_id: Floor ID.
        restaurant_id: Current user's restaurant ID.
        use_case: Floor management use case.
        
    Returns:
        Complete floor plan information.
        
    Raises:
        HTTPException: If floor not found.
    """
    floor_plan_dto = await use_case.get_floor_plan(floor_id)
    if not floor_plan_dto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Floor not found")
    
    # Verify floor belongs to restaurant
    if floor_plan_dto.floor.restaurant_id != restaurant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    return FloorPlanResponseSchema(**floor_plan_dto.dict())


@router.put("/floors/{floor_id}", response_model=FloorResponseSchema)
async def update_floor(
    floor_id: UUID,
    floor_data: UpdateFloorSchema,
    restaurant_id: UUID = Depends(get_current_user_restaurant_id),
    use_case: ManageFloorPlanUseCase = Depends(get_manage_floor_plan_use_case)
):
    """Update floor information.
    
    Args:
        floor_id: Floor ID.
        floor_data: Floor update data.
        restaurant_id: Current user's restaurant ID.
        use_case: Floor management use case.
        
    Returns:
        Updated floor information.
        
    Raises:
        HTTPException: If floor not found or update fails.
    """
    # Verify floor exists and belongs to restaurant
    existing_floor = await use_case.get_floor_by_id(floor_id)
    if not existing_floor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Floor not found")
    
    if existing_floor.restaurant_id != restaurant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    try:
        updated_floor_dto = await use_case.update_floor(floor_id, floor_data)
        if not updated_floor_dto:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Floor not found")
        
        return FloorResponseSchema(**updated_floor_dto.dict())
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/floors/{floor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_floor(
    floor_id: UUID,
    restaurant_id: UUID = Depends(get_current_user_restaurant_id),
    use_case: ManageFloorPlanUseCase = Depends(get_manage_floor_plan_use_case)
):
    """Delete a floor.
    
    Args:
        floor_id: Floor ID.
        restaurant_id: Current user's restaurant ID.
        use_case: Floor management use case.
        
    Raises:
        HTTPException: If floor not found or deletion fails.
    """
    # Verify floor exists and belongs to restaurant
    existing_floor = await use_case.get_floor_by_id(floor_id)
    if not existing_floor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Floor not found")
    
    if existing_floor.restaurant_id != restaurant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    try:
        success = await use_case.delete_floor(floor_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Floor not found")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# Table management endpoints
@router.post("/", response_model=TableResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_table(
    table_data: CreateTableSchema,
    restaurant_id: UUID = Depends(get_current_user_restaurant_id),
    use_case: CreateTableUseCase = Depends(get_create_table_use_case)
):
    """Create a new table.
    
    Args:
        table_data: Table creation data.
        restaurant_id: Current user's restaurant ID.
        use_case: Create table use case.
        
    Returns:
        Created table information.
        
    Raises:
        HTTPException: If table creation fails.
    """
    try:
        table_dto = await use_case.execute(restaurant_id, table_data)
        return TableResponseSchema(**table_dto.dict())
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/", response_model=List[TableResponseSchema])
async def get_tables(
    floor_id: Optional[UUID] = Query(None, description="Filter by floor ID"),
    status_filter: Optional[TableStatus] = Query(None, alias="status", description="Filter by table status"),
    party_size: Optional[int] = Query(None, description="Filter available tables for party size"),
    restaurant_id: UUID = Depends(get_current_user_restaurant_id),
    use_case: GetTablesUseCase = Depends(get_get_tables_use_case)
):
    """Get tables for the restaurant.

    Args:
        floor_id: Optional floor ID filter.
        status_filter: Optional status filter.
        party_size: Optional party size filter (only available tables).
        restaurant_id: Current user's restaurant ID.
        use_case: Get tables use case.

    Returns:
        List of tables.
    """
    if party_size:
        table_dtos = await use_case.get_available_tables(restaurant_id, party_size)
    elif floor_id:
        table_dtos = await use_case.get_tables_by_floor(floor_id)
        # Filter by restaurant to ensure security
        table_dtos = [t for t in table_dtos if t.restaurant_id == restaurant_id]
    elif status_filter:
        table_dtos = await use_case.get_tables_by_status(restaurant_id, status_filter)
    else:
        table_dtos = await use_case.get_tables_by_restaurant(restaurant_id)

    return [TableResponseSchema(**table_dto.dict()) for table_dto in table_dtos]


@router.get("/stats", response_model=TableOccupancyStatsSchema)
async def get_occupancy_stats(
    restaurant_id: UUID = Depends(get_current_user_restaurant_id),
    use_case: GetTablesUseCase = Depends(get_get_tables_use_case)
):
    """Get table occupancy statistics.

    Args:
        restaurant_id: Current user's restaurant ID.
        use_case: Get tables use case.

    Returns:
        Table occupancy statistics.
    """
    stats_dto = await use_case.get_occupancy_stats(restaurant_id)
    return TableOccupancyStatsSchema(**stats_dto.dict())


@router.get("/{table_id}", response_model=TableResponseSchema)
async def get_table(
    table_id: UUID,
    restaurant_id: UUID = Depends(get_current_user_restaurant_id),
    use_case: GetTablesUseCase = Depends(get_get_tables_use_case)
):
    """Get table by ID.

    Args:
        table_id: Table ID.
        restaurant_id: Current user's restaurant ID.
        use_case: Get tables use case.

    Returns:
        Table information.

    Raises:
        HTTPException: If table not found.
    """
    table_dto = await use_case.get_table_by_id(table_id)
    if not table_dto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")

    # Verify table belongs to restaurant
    if table_dto.restaurant_id != restaurant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return TableResponseSchema(**table_dto.dict())


@router.put("/{table_id}", response_model=TableResponseSchema)
async def update_table(
    table_id: UUID,
    table_data: UpdateTableSchema,
    restaurant_id: UUID = Depends(get_current_user_restaurant_id),
    use_case: UpdateTableUseCase = Depends(get_update_table_use_case)
):
    """Update table information.

    Args:
        table_id: Table ID.
        table_data: Table update data.
        restaurant_id: Current user's restaurant ID.
        use_case: Update table use case.

    Returns:
        Updated table information.

    Raises:
        HTTPException: If table not found or update fails.
    """
    # Verify table exists and belongs to restaurant
    get_use_case = GetTablesUseCase(use_case._table_repository)
    existing_table = await get_use_case.get_table_by_id(table_id)
    if not existing_table:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")

    if existing_table.restaurant_id != restaurant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    try:
        updated_table_dto = await use_case.execute(table_id, table_data)
        if not updated_table_dto:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")

        return TableResponseSchema(**updated_table_dto.dict())
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/{table_id}/status", response_model=dict)
async def update_table_status(
    table_id: UUID,
    status_data: UpdateTableStatusSchema,
    restaurant_id: UUID = Depends(get_current_user_restaurant_id),
    use_case: UpdateTableStatusUseCase = Depends(get_update_table_status_use_case)
):
    """Update table status.

    Args:
        table_id: Table ID.
        status_data: Status update data.
        restaurant_id: Current user's restaurant ID.
        use_case: Update table status use case.

    Returns:
        Success message.

    Raises:
        HTTPException: If table not found or update fails.
    """
    # Verify table exists and belongs to restaurant
    get_use_case = GetTablesUseCase(use_case._table_repository)
    existing_table = await get_use_case.get_table_by_id(table_id)
    if not existing_table:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")

    if existing_table.restaurant_id != restaurant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    success = await use_case.execute(table_id, status_data.status)
    if not success:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update table status")

    return {"message": "Table status updated successfully"}


@router.delete("/{table_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_table(
    table_id: UUID,
    restaurant_id: UUID = Depends(get_current_user_restaurant_id),
    table_repo: TableRepositoryImpl = Depends(get_table_repository)
):
    """Delete a table.

    Args:
        table_id: Table ID.
        restaurant_id: Current user's restaurant ID.
        table_repo: Table repository.

    Raises:
        HTTPException: If table not found or deletion fails.
    """
    # Verify table exists and belongs to restaurant
    existing_table = await table_repo.get_table_by_id(table_id)
    if not existing_table:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")

    if existing_table.restaurant_id != restaurant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    success = await table_repo.delete_table(table_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete table")
