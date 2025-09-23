from fastapi import APIRouter
from pydantic import BaseModel

from ...common.supabase_client import get_supabase

router = APIRouter()


class Restaurant(BaseModel):
    id: str
    name: str


@router.post("/restaurants")
async def create_restaurant(payload: Restaurant):
    sb = get_supabase()
    res = sb.table("restaurants").insert(payload.model_dump()).execute()
    return res.data[0] if res.data else {}
