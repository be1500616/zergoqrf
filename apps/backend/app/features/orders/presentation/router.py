"""Orders presentation router.

POST /orders — converts a cart session into an order by calling the
Supabase RPC `create_order_from_cart`. That RPC is the source of truth
for atomic cart→order conversion (validates cart, computes GST, inserts
order + items, generates order_number and payment_reference).
"""

import logging
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field, EmailStr

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Orders"])


# ── Request ──────────────────────────────────────────────────────────────────

class CreateOrderRequest(BaseModel):
    """POST /orders payload — cart-driven order creation."""

    cart_session_id: UUID = Field(..., description="Active cart session to convert")
    customer_name: str = Field(..., min_length=2, max_length=255)
    customer_phone: str = Field(..., pattern=r"^\+91[6-9]\d{9}$")
    customer_email: EmailStr | None = None
    special_instructions: str | None = Field(None, max_length=500)


# ── Response ─────────────────────────────────────────────────────────────────

class OrderCreateResponse(BaseModel):
    order_id: UUID
    order_number: str
    payment_reference: str
    total_amount: float
    customer_name: str
    customer_phone: str
    order_status: str = "placed"
    payment_status: str = "payment_pending"


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/", response_model=OrderCreateResponse)
async def create_order(payload: CreateOrderRequest, request: Request):
    """Create an order from a cart session via the create_order_from_cart RPC."""
    sb = request.app.state.supabase_service
    try:
        params = {
            "p_cart_session_id": str(payload.cart_session_id),
            "p_customer_name": payload.customer_name,
            "p_customer_phone": payload.customer_phone,
        }
        if payload.customer_email:
            params["p_customer_email"] = str(payload.customer_email)
        if payload.special_instructions:
            params["p_special_instructions"] = payload.special_instructions

        resp = await sb.rpc("create_order_from_cart", params).execute()
    except Exception as exc:  # pragma: no cover — network/RLS path
        logger.exception("create_order_from_cart RPC failed")
        raise HTTPException(status_code=502, detail=f"order creation failed: {exc}") from exc

    if not resp.data:
        raise HTTPException(status_code=502, detail="RPC returned no data")

    row = resp.data[0] if isinstance(resp.data, list) else resp.data
    return OrderCreateResponse(
        order_id=UUID(str(row["order_id"])),
        order_number=str(row["order_number"]),
        payment_reference=str(row["payment_reference"]),
        total_amount=float(row["total_amount"]),
        customer_name=payload.customer_name,
        customer_phone=payload.customer_phone,
    )
