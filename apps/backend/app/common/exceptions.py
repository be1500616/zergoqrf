import structlog
from fastapi import Request
from fastapi.responses import JSONResponse

logger = structlog.get_logger()


class AppError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


async def app_error_handler(request: Request, exc: AppError):
    logger.error(
        "app_error",
        path=str(request.url),
        status=exc.status_code,
        msg=exc.message,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )
