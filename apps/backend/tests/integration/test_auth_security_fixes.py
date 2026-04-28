"""Integration tests for authentication security fixes.

This module contains comprehensive tests to verify that all security
fixes are working correctly and authentication flows are secure.
"""

import pytest
from httpx import AsyncClient
from unittest.mock import patch, Mock
from fastapi import status

from app.main import create_app
from app.core.config import settings


class TestAuthSecurityFixes:
    """Test cases for authentication security fixes."""

    @pytest.fixture
    async def client(self):
        """Create test client."""
        app = create_app()
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac

    @pytest.mark.asyncio
    async def test_hardcoded_credentials_removed(self, client: AsyncClient):
        """Test that hardcoded test credentials are no longer in config."""
        # Verify that test credentials are not hardcoded
        assert settings.test_phone_number is None or settings.test_phone_number == ""
        assert settings.test_otp_code is None or settings.test_otp_code == ""
        assert settings.enable_test_phone is False

    @pytest.mark.asyncio
    async def test_security_headers_present(self, client: AsyncClient):
        """Test that security headers are added to responses."""
        response = await client.get("/healthz")
        
        # Check for security headers
        assert "Strict-Transport-Security" in response.headers
        assert "X-Content-Type-Options" in response.headers
        assert "X-Frame-Options" in response.headers
        assert "X-XSS-Protection" in response.headers
        assert "Content-Security-Policy" in response.headers
        assert "Referrer-Policy" in response.headers
        assert "Permissions-Policy" in response.headers
        
        # Verify header values
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Frame-Options"] == "DENY"
        assert response.headers["X-XSS-Protection"] == "1; mode=block"

    @pytest.mark.asyncio
    async def test_openapi_has_bearer_auth(self, client: AsyncClient):
        """Test that OpenAPI schema includes Bearer authentication."""
        response = await client.get("/openapi.json")
        assert response.status_code == 200
        
        openapi_schema = response.json()
        
        # Check for security schemes
        assert "components" in openapi_schema
        assert "securitySchemes" in openapi_schema["components"]
        assert "BearerAuth" in openapi_schema["components"]["securitySchemes"]
        
        bearer_auth = openapi_schema["components"]["securitySchemes"]["BearerAuth"]
        assert bearer_auth["type"] == "http"
        assert bearer_auth["scheme"] == "bearer"
        assert bearer_auth["bearerFormat"] == "JWT"

    @pytest.mark.asyncio
    async def test_jwt_verification_secure(self, client: AsyncClient):
        """Test that JWT verification is secure and cannot be bypassed."""
        # Test with invalid token
        invalid_token = "invalid.jwt.token"
        
        response = await client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {invalid_token}"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_tampered_jwt_rejected(self, client: AsyncClient):
        """Test that tampered JWT tokens are rejected."""
        # Create a tampered token (this would be a real JWT with modified signature)
        tampered_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhZG1pbiIsInJvbGUiOiJhZG1pbiJ9.TAMPERED_SIGNATURE"
        
        response = await client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {tampered_token}"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_phone_auth_without_test_credentials(self, client: AsyncClient):
        """Test that phone authentication works without hardcoded test credentials."""
        # Mock the OTP service to avoid sending real SMS
        with patch('app.features.auth.infrastructure.otp_service_impl.OTPServiceImpl.send_otp') as mock_send_otp:
            mock_send_otp.return_value = True
            
            # Test phone auth request
            response = await client.post(
                "/auth/phone/request-otp",
                json={"phone": "+1234567890"}
            )
            
            # Should work even without test credentials
            # The actual response depends on your implementation
            # This test ensures the endpoint doesn't crash due to missing test credentials
            assert response.status_code in [200, 400, 422]  # Valid response codes

    @pytest.mark.asyncio
    async def test_password_validation_enforced(self, client: AsyncClient):
        """Test that password validation is properly enforced."""
        # Test with weak password
        weak_password_data = {
            "email": "test@example.com",
            "password": "weak",  # Too short, no numbers
            "name": "Test User"
        }
        
        response = await client.post("/auth/signup", json=weak_password_data)
        
        # Should reject weak password
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_cors_headers_present(self, client: AsyncClient):
        """Test that CORS headers are properly configured."""
        # Make an OPTIONS request to check CORS
        response = await client.options("/auth/signin")
        
        # CORS headers should be present
        assert "Access-Control-Allow-Origin" in response.headers
        assert "Access-Control-Allow-Methods" in response.headers
        assert "Access-Control-Allow-Headers" in response.headers

    @pytest.mark.asyncio
    async def test_no_server_header_exposed(self, client: AsyncClient):
        """Test that server information is not exposed in headers."""
        response = await client.get("/healthz")
        
        # Server header should be removed by security middleware
        assert "Server" not in response.headers

    @pytest.mark.asyncio
    async def test_health_check_works(self, client: AsyncClient):
        """Test that health check endpoint works correctly."""
        response = await client.get("/healthz")
        
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    @pytest.mark.asyncio
    async def test_swagger_ui_accessible(self, client: AsyncClient):
        """Test that Swagger UI is accessible and includes authentication."""
        response = await client.get("/docs")
        
        assert response.status_code == 200
        # Should contain HTML for Swagger UI
        assert "swagger" in response.text.lower() or "openapi" in response.text.lower()

    @pytest.mark.asyncio
    async def test_redoc_accessible(self, client: AsyncClient):
        """Test that ReDoc is accessible."""
        response = await client.get("/redoc")
        
        assert response.status_code == 200
        # Should contain HTML for ReDoc
        assert "redoc" in response.text.lower()

    @pytest.mark.asyncio
    async def test_environment_variables_used(self):
        """Test that configuration uses environment variables instead of hardcoded values."""
        # Test that sensitive configuration is not hardcoded
        assert not hasattr(settings, 'hardcoded_password') or settings.hardcoded_password is None
        
        # Test that database URL comes from environment
        assert settings.database_url is not None
        assert settings.supabase_url is not None
        assert settings.supabase_anon_key is not None

    @pytest.mark.asyncio
    async def test_production_security_config(self):
        """Test that production security configuration is properly set."""
        # In production, certain security features should be enabled
        if settings.env == "production":
            # Rate limiting should be enabled
            assert hasattr(settings, 'enable_rate_limiting')
            
            # HTTPS should be enforced
            assert settings.allowed_origins != ["*"]  # Should not allow all origins in production
