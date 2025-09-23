from typing import List

from fastapi import APIRouter
from pydantic import BaseModel

from ...common.supabase_client import get_supabase

router = APIRouter()


class MenuItem(BaseModel):
    id: str
    name: str
    price_cents: int
    restaurant_id: str


@router.get("/items", response_model=List[MenuItem])
async def list_items(restaurant_id: str):
    sb = get_supabase()
    res = (
        sb.table("menu_items").select("*").eq("restaurant_id", restaurant_id).execute()
    )
    return res.data or []
