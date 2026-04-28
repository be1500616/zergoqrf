"""Public menu router registration.

This module registers the public menu router with the main application.
"""

from fastapi import APIRouter

from .presentation.public_menu_router import router as public_menu_router

# Create main public menu router
router = APIRouter()

# Include public menu routes
router.include_router(public_menu_router)
