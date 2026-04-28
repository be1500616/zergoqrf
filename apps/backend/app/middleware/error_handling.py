"""
Comprehensive error handling and logging middleware for FastAPI.

This module provides centralized error handling, logging, and monitoring
for the ZERGO QR restaurant ordering system.
"""

import logging
import time
import traceback
from typing import Any, Dict, Optional
from uuid import uuid4

from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from supabase.lib.client_options import ClientOptions
from supabase import Client

logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for centralized error handling and logging.
    
    This middleware catches all exceptions, logs them appropriately,
    and returns consistent error responses to clients.
    """

    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        """
        Process the request and handle any errors.
        
        Args:
            request: The incoming HTTP request
            call_next: The next middleware or route handler
            
        Returns:
            Response: The HTTP response
        """
        # Generate request ID for tracing
        request_id = str(uuid4())
        request.state.request_id = request_id
        
        # Log request start
        start_time = time.time()
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "user_agent": request.headers.get("user-agent"),
                "client_ip": self._get_client_ip(request),
            }
        )

        try:
            response = await call_next(request)
            
            # Log successful request
            duration = time.time() - start_time
            logger.info(
                f"Request completed: {request.method} {request.url.path} - {response.status_code}",
                extra={
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "duration_ms": round(duration * 1000, 2),
                }
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response

        except HTTPException as e:
            # Handle FastAPI HTTP exceptions
            duration = time.time() - start_time
            
            logger.warning(
                f"HTTP exception: {request.method} {request.url.path} - {e.status_code}: {e.detail}",
                extra={
                    "request_id": request_id,
                    "status_code": e.status_code,
                    "error_detail": e.detail,
                    "duration_ms": round(duration * 1000, 2),
                }
            )
            
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "error": {
                        "code": e.status_code,
                        "message": e.detail,
                        "request_id": request_id,
                        "timestamp": time.time(),
                    }
                },
                headers={"X-Request-ID": request_id}
            )

        except Exception as e:
            # Handle unexpected exceptions
            duration = time.time() - start_time
            error_id = str(uuid4())
            
            logger.error(
                f"Unhandled exception: {request.method} {request.url.path} - {str(e)}",
                extra={
                    "request_id": request_id,
                    "error_id": error_id,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "duration_ms": round(duration * 1000, 2),
                    "traceback": traceback.format_exc(),
                }
            )
            
            # Return generic error response (don't expose internal details)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": {
                        "code": 500,
                        "message": "Internal server error",
                        "request_id": request_id,
                        "error_id": error_id,
                        "timestamp": time.time(),
                    }
                },
                headers={"X-Request-ID": request_id}
            )

    def _get_client_ip(self, request: Request) -> str:
        """
        Get the client IP address from the request.
        
        Args:
            request: The HTTP request
            
        Returns:
            str: The client IP address
        """
        # Check for forwarded headers (when behind a proxy)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct client IP
        return request.client.host if request.client else "unknown"


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """
    Middleware for performance monitoring and metrics collection.
    
    This middleware tracks request performance and can be extended
    to send metrics to monitoring systems.
    """

    def __init__(self, app):
        super().__init__(app)
        self.slow_request_threshold = 1.0  # seconds

    async def dispatch(self, request: Request, call_next):
        """
        Process the request and monitor performance.
        
        Args:
            request: The incoming HTTP request
            call_next: The next middleware or route handler
            
        Returns:
            Response: The HTTP response
        """
        start_time = time.time()
        
        response = await call_next(request)
        
        duration = time.time() - start_time
        
        # Log slow requests
        if duration > self.slow_request_threshold:
            request_id = getattr(request.state, "request_id", "unknown")
            logger.warning(
                f"Slow request detected: {request.method} {request.url.path}",
                extra={
                    "request_id": request_id,
                    "duration_ms": round(duration * 1000, 2),
                    "threshold_ms": self.slow_request_threshold * 1000,
                }
            )
        
        # Add performance headers
        response.headers["X-Response-Time"] = f"{round(duration * 1000, 2)}ms"
        
        return response


class DatabaseErrorHandler:
    """
    Utility class for handling database-specific errors.
    
    This class provides methods to handle and translate database
    errors into appropriate HTTP responses.
    """

    @staticmethod
    def handle_supabase_error(error: Exception) -> HTTPException:
        """
        Handle Supabase-specific errors.
        
        Args:
            error: The Supabase error
            
        Returns:
            HTTPException: The appropriate HTTP exception
        """
        error_message = str(error).lower()
        
        # Authentication errors
        if "invalid_grant" in error_message or "invalid_credentials" in error_message:
            return HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Authorization errors
        if "insufficient_scope" in error_message or "access_denied" in error_message:
            return HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Rate limiting errors
        if "rate_limit" in error_message or "too_many_requests" in error_message:
            return HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )
        
        # Validation errors
        if "invalid_request" in error_message or "bad_request" in error_message:
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid request"
            )
        
        # Not found errors
        if "not_found" in error_message or "does_not_exist" in error_message:
            return HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resource not found"
            )
        
        # Conflict errors (duplicate data, etc.)
        if "conflict" in error_message or "already_exists" in error_message:
            return HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Resource conflict"
            )
        
        # Default to internal server error
        logger.error(f"Unhandled Supabase error: {error}")
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed"
        )

    @staticmethod
    def handle_validation_error(error: Exception) -> HTTPException:
        """
        Handle validation errors from Pydantic models.
        
        Args:
            error: The validation error
            
        Returns:
            HTTPException: The appropriate HTTP exception
        """
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation error: {str(error)}"
        )


class SecurityErrorHandler:
    """
    Utility class for handling security-related errors.
    
    This class provides methods to handle authentication,
    authorization, and other security errors.
    """

    @staticmethod
    def handle_auth_error(error: Exception) -> HTTPException:
        """
        Handle authentication errors.
        
        Args:
            error: The authentication error
            
        Returns:
            HTTPException: The appropriate HTTP exception
        """
        error_message = str(error).lower()
        
        if "token" in error_message and ("expired" in error_message or "invalid" in error_message):
            return HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired or invalid",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if "permission" in error_message or "access" in error_message:
            return HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        # Default authentication error
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Utility functions for error handling
def create_error_response(
    status_code: int,
    message: str,
    request_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
) -> JSONResponse:
    """
    Create a standardized error response.
    
    Args:
        status_code: HTTP status code
        message: Error message
        request_id: Optional request ID
        details: Optional additional error details
        
    Returns:
        JSONResponse: The error response
    """
    content = {
        "error": {
            "code": status_code,
            "message": message,
            "timestamp": time.time(),
        }
    }
    
    if request_id:
        content["error"]["request_id"] = request_id
    
    if details:
        content["error"]["details"] = details
    
    headers = {}
    if request_id:
        headers["X-Request-ID"] = request_id
    
    return JSONResponse(
        status_code=status_code,
        content=content,
        headers=headers
    )


def log_security_event(
    event_type: str,
    request: Request,
    details: Optional[Dict[str, Any]] = None,
):
    """
    Log security-related events for monitoring and alerting.
    
    Args:
        event_type: Type of security event
        request: The HTTP request
        details: Optional additional details
    """
    request_id = getattr(request.state, "request_id", "unknown")
    
    logger.warning(
        f"Security event: {event_type}",
        extra={
            "event_type": event_type,
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "client_ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent"),
            "details": details or {},
        }
    )
