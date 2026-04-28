from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ...common.supabase_client import get_supabase

router = APIRouter()


class OrderItem(BaseModel):
    item_id: str
    qty: int


class CreateOrderRequest(BaseModel):
    restaurant_id: str
    table_id: str | None = None
    items: List[OrderItem]


@router.post("/")
async def create_order(payload: CreateOrderRequest):
    sb = get_supabase()
    # Simplified create
    ins = (
        sb.table("orders")
        .insert(
            {
                "restaurant_id": payload.restaurant_id,
                "table_id": payload.table_id,
                "status": "pending",
            }
        )
        .execute()
    )
    if not ins.data:
        raise HTTPException(status_code=400, detail="Failed to create order")
    order = ins.data[0]
    return {"order": order}
