"""Cart presentation layer package.

This package contains the presentation layer for cart management,
including FastAPI routers and Pydantic schemas.
"""

from . import cart_router

__all__ = ["cart_router"]
