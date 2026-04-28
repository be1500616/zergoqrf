"""Security middleware for FastAPI application.

This module provides security middleware to add security headers
and implement security best practices for production deployment.
"""

import logging
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from ..core.config import settings

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to all responses.

    This middleware adds essential security headers to protect against
    common web vulnerabilities like XSS, clickjacking, and MIME sniffing.
    """

    def __init__(self, app: ASGIApp):
        """Initialize the security headers middleware.

        Args:
            app: The ASGI application instance
        """
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and add security headers to response.

        Args:
            request: The incoming HTTP request
            call_next: The next middleware or route handler

        Returns:
            Response with security headers added
        """
        # Process the request
        response = await call_next(request)

        # Add security headers
        self._add_security_headers(response)

        return response

    def _add_security_headers(self, response: Response) -> None:
        """Add security headers to the response.

        Args:
            response: The HTTP response to add headers to
        """
        # Strict Transport Security - Force HTTPS
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains; preload"
        )

        # Content Type Options - Prevent MIME sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Frame Options - Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # XSS Protection - Enable XSS filtering
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Content Security Policy - Prevent XSS and injection attacks
        csp_policy = self._build_csp_policy()
        response.headers["Content-Security-Policy"] = csp_policy

        # Log CSP policy in development for debugging
        if settings.env == "development":
            logger.debug(f"Applied CSP policy: {csp_policy}")

        # Referrer Policy - Control referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions Policy - Control browser features
        permissions_policy = self._build_permissions_policy()
        response.headers["Permissions-Policy"] = permissions_policy

        # Remove server information
        if "Server" in response.headers:
            del response.headers["Server"]

    def _build_csp_policy(self) -> str:
        """Build Content Security Policy header value.

        Returns:
            CSP policy string
        """
        # Build connect-src directive based on environment
        connect_src = "'self' https://*.supabase.co wss://*.supabase.co"
        if settings.env == "development":
            # Allow connections to local development servers
            connect_src += " http://localhost:* ws://localhost:*"

        # Configure script-src based on environment
        if settings.env == "development":
            # Development: Allow Swagger UI requirements
            script_src = (
                "'self' 'unsafe-inline' 'unsafe-eval' "
                "https://cdn.jsdelivr.net https://unpkg.com"
            )
        else:
            # Production: More restrictive policy
            script_src = "'self' https://cdn.jsdelivr.net"

        # Configure font-src based on environment
        if settings.env == "development":
            # Development: Allow external fonts for Swagger UI
            font_src = (
                "'self' data: https://fonts.gstatic.com "
                "https://cdn.jsdelivr.net https://unpkg.com"
            )
        else:
            # Production: More restrictive
            font_src = "'self' data:"

        # Base CSP policy for API server
        csp_directives = [
            "default-src 'self'",
            f"script-src {script_src}",
            # Allow Swagger UI styles from trusted CDN and inline styles
            (
                "style-src 'self' 'unsafe-inline' "
                "https://cdn.jsdelivr.net https://unpkg.com"
            ),
            "img-src 'self' data: https:",
            f"font-src {font_src}",
            f"connect-src {connect_src}",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'",
        ]

        csp_policy = "; ".join(csp_directives)

        # Log CSP configuration in development
        if settings.env == "development":
            logger.debug(f"Building CSP policy for {settings.env} environment")
            logger.debug(f"Script sources: {script_src}")
            logger.debug(f"Font sources: {font_src}")

        return csp_policy

    def _build_permissions_policy(self) -> str:
        """Build Permissions Policy header value.

        Returns:
            Permissions policy string
        """
        # Disable potentially dangerous browser features
        permissions = [
            "camera=()",
            "microphone=()",
            "geolocation=()",
            "payment=()",
            "usb=()",
            "magnetometer=()",
            "gyroscope=()",
            "accelerometer=()",
        ]

        return ", ".join(permissions)


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """Basic rate limiting middleware.

    This provides simple in-memory rate limiting. For production,
    consider using Redis-based rate limiting.
    """

    def __init__(self, app: ASGIApp, requests_per_minute: int = 1000):
        """Initialize rate limiting middleware.

        Args:
            app: The ASGI application instance
            requests_per_minute: Maximum requests per minute per IP
        """
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_counts = {}  # In production, use Redis

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with rate limiting.

        Args:
            request: The incoming HTTP request
            call_next: The next middleware or route handler

        Returns:
            Response or rate limit error
        """
        # Get client IP
        client_ip = self._get_client_ip(request)

        # Check rate limit (simplified implementation)
        if self._is_rate_limited(client_ip):
            return Response(
                content="Rate limit exceeded",
                status_code=429,
                headers={"Retry-After": "60"},
            )

        # Process request
        response = await call_next(request)
        return response

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address from request.

        Args:
            request: The HTTP request

        Returns:
            Client IP address
        """
        # Check for forwarded headers (when behind proxy)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fallback to direct connection IP
        return request.client.host if request.client else "unknown"

    def _is_rate_limited(self, client_ip: str) -> bool:
        """Check if client IP is rate limited.

        Args:
            client_ip: Client IP address

        Returns:
            True if rate limited, False otherwise
        """
        # Simplified rate limiting logic
        # In production, use Redis with sliding window
        import time

        current_time = int(time.time() / 60)  # Current minute
        key = f"{client_ip}:{current_time}"

        if key not in self.request_counts:
            self.request_counts[key] = 0

        self.request_counts[key] += 1

        # Clean up old entries (keep only current minute)
        keys_to_remove = [
            k for k in self.request_counts.keys() if int(k.split(":")[1]) < current_time
        ]
        for k in keys_to_remove:
            del self.request_counts[k]

        return self.request_counts[key] > self.requests_per_minute
