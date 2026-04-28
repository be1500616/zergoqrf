"""QR generation router registration.

This module registers the QR generation router with the main application.
"""

from fastapi import APIRouter

from .presentation.qr_router import router as qr_router

# Create main QR router
router = APIRouter()

# Include QR generation routes
router.include_router(qr_router)
