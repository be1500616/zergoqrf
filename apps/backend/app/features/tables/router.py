"""Table management router registration.

This module registers the table management router with the main application.
"""

from fastapi import APIRouter

from .presentation.table_router import router as table_router

# Create main tables router
router = APIRouter()

# Include table management routes
router.include_router(table_router)
