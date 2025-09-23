from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .common.exceptions import AppError, app_error_handler
from .core.config import settings
from .core.logging import setup_logging
from .features.admin.presentation.router import router as admin_router
from .features.auth.presentation.router import router as auth_router
from .features.menu.presentation.router import router as menu_router
from .features.orders.presentation.router import router as orders_router

setup_logging(settings.log_level)

app = FastAPI(title="ZERGO QR API", version="0.1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers included below

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(menu_router, prefix="/menu", tags=["menu"])
app.include_router(orders_router, prefix="/orders", tags=["orders"])
app.include_router(admin_router, prefix="/admin", tags=["admin"])

app.add_exception_handler(AppError, app_error_handler)


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}
