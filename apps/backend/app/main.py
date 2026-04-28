from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .common.exceptions import AppError, app_error_handler
from .core.config import settings
from .core.logging import setup_logging
from .features.admin.presentation.router import router as admin_router
from .features.auth.presentation.auth_router import router as auth_router
from .features.menu.presentation.router import router as menu_router
from .features.orders.presentation.router import router as orders_router
from .features.public_menu.presentation.public_menu_router import (
    router as public_menu_router,
)
from .security import verify_supabase_jwt

setup_logging(settings.log_level)


def create_app() -> FastAPI:
    app = FastAPI(
        title="ZERGO QR API",
        description="The backend API for ZERGO QR Ordering System",
        version="0.1.0",
        openapi_tags=[
            {
                "name": "Public Menu",
                "description": "Endpoints for public guest menu access (no auth req)",
            },
            {"name": "Orders", "description": "Customer and Kitchen order management"},
            {"name": "Auth", "description": "Authentication and session management"},
            {
                "name": "Menu Management",
                "description": "Administrative menu and catalog management",
            },
            {"name": "Admin", "description": "Internal administrative controls"},
        ],
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers grouped by feature area
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
    app.include_router(menu_router, prefix="/api/v1/menu", tags=["Menu Management"])
    app.include_router(orders_router, prefix="/api/v1/orders", tags=["Orders"])
    app.include_router(public_menu_router, prefix="/api/v1", tags=["Public Menu"])
    app.include_router(
        admin_router,
        prefix="/api/v1/admin",
        tags=["Admin"],
        dependencies=[Depends(verify_supabase_jwt)],
    )

    app.add_exception_handler(AppError, app_error_handler)

    @app.get("/healthz")
    async def healthz():
        return {"status": "ok"}

    @app.get("/protected-test", dependencies=[Depends(verify_supabase_jwt)])
    async def protected_test():
        return {"message": "You have access to protected data!"}

    return app


app = create_app()
