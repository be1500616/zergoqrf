"""Security tests for JWT token validation.

This module contains tests to verify that JWT tokens are properly validated
and that security vulnerabilities like signature bypass are prevented.
"""

import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException

from app.features.auth.presentation.dependencies import (
    get_current_user,
    decode_jwt_claims,
)


class TestJWTSecurity:
    """Test cases for JWT security validation."""

    @pytest.mark.asyncio
    async def test_get_current_user_with_invalid_token(self):
        """Test that invalid tokens are rejected."""
        # Arrange
        mock_token = Mock()
        mock_token.credentials = "invalid.jwt.token"
        
        mock_supabase = Mock()
        mock_supabase.auth.get_user.side_effect = Exception("Invalid token")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(mock_token, mock_supabase)
        
        assert exc_info.value.status_code == 401
        assert "Invalid token" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_current_user_with_none_user_response(self):
        """Test that tokens returning None user are rejected."""
        # Arrange
        mock_token = Mock()
        mock_token.credentials = "valid.format.token"
        
        mock_supabase = Mock()
        mock_user_response = Mock()
        mock_user_response.user = None
        mock_supabase.auth.get_user.return_value = mock_user_response

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(mock_token, mock_supabase)
        
        assert exc_info.value.status_code == 401
        assert "Invalid token" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_current_user_with_valid_token(self):
        """Test that valid tokens are accepted."""
        # Arrange
        mock_token = Mock()
        mock_token.credentials = "valid.jwt.token"
        
        mock_user = Mock()
        mock_user.id = "user-123"
        mock_user.email = "test@example.com"
        
        mock_supabase = Mock()
        mock_user_response = Mock()
        mock_user_response.user = mock_user
        mock_supabase.auth.get_user.return_value = mock_user_response

        # Act
        result = get_current_user(mock_token, mock_supabase)

        # Assert
        assert result == mock_user
        mock_supabase.auth.get_user.assert_called_once_with("valid.jwt.token")

    def test_decode_jwt_claims_with_invalid_token(self):
        """Test that decode_jwt_claims handles invalid tokens securely."""
        # Arrange
        invalid_token = "invalid.jwt.token"
        
        with patch('app.features.auth.presentation.dependencies.get_supabase') as mock_get_supabase:
            mock_supabase = Mock()
            mock_supabase.auth.get_user.side_effect = Exception("Invalid token")
            mock_get_supabase.return_value = iter([mock_supabase])

            # Act
            result = decode_jwt_claims(invalid_token)

            # Assert
            assert result == {}

    def test_decode_jwt_claims_with_valid_token(self):
        """Test that decode_jwt_claims extracts claims from valid tokens."""
        # Arrange
        valid_token = "valid.jwt.token"
        
        mock_user = Mock()
        mock_user.id = "user-123"
        mock_user.email = "test@example.com"
        mock_user.user_metadata = {
            "role": "customer",
            "restaurant_id": "rest-456",
            "permissions": {"read": True}
        }
        
        with patch('app.features.auth.presentation.dependencies.get_supabase') as mock_get_supabase:
            mock_supabase = Mock()
            mock_user_response = Mock()
            mock_user_response.user = mock_user
            mock_supabase.auth.get_user.return_value = mock_user_response
            mock_get_supabase.return_value = iter([mock_supabase])

            # Act
            result = decode_jwt_claims(valid_token)

            # Assert
            expected = {
                "sub": "user-123",
                "email": "test@example.com",
                "role": "customer",
                "restaurant_id": "rest-456",
                "permissions": {"read": True}
            }
            assert result == expected

    def test_decode_jwt_claims_with_missing_metadata(self):
        """Test that decode_jwt_claims handles missing user metadata."""
        # Arrange
        valid_token = "valid.jwt.token"
        
        mock_user = Mock()
        mock_user.id = "user-123"
        mock_user.email = "test@example.com"
        mock_user.user_metadata = None
        
        with patch('app.features.auth.presentation.dependencies.get_supabase') as mock_get_supabase:
            mock_supabase = Mock()
            mock_user_response = Mock()
            mock_user_response.user = mock_user
            mock_supabase.auth.get_user.return_value = mock_user_response
            mock_get_supabase.return_value = iter([mock_supabase])

            # Act
            result = decode_jwt_claims(valid_token)

            # Assert
            expected = {
                "sub": "user-123",
                "email": "test@example.com",
                "role": "customer",  # Default value
                "restaurant_id": None,
                "permissions": {}
            }
            assert result == expected

    def test_jwt_signature_verification_is_enforced(self):
        """Test that JWT signature verification cannot be bypassed."""
        # This test verifies that we're using Supabase's secure validation
        # instead of manual JWT decode with verify_signature=False
        
        # Arrange
        tampered_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhZG1pbiIsInJvbGUiOiJhZG1pbiJ9.TAMPERED_SIGNATURE"
        
        with patch('app.features.auth.presentation.dependencies.get_supabase') as mock_get_supabase:
            mock_supabase = Mock()
            # Supabase should reject tampered tokens
            mock_supabase.auth.get_user.side_effect = Exception("Invalid JWT signature")
            mock_get_supabase.return_value = iter([mock_supabase])

            # Act
            result = decode_jwt_claims(tampered_token)

            # Assert
            assert result == {}  # Should return empty dict for invalid tokens
            mock_supabase.auth.get_user.assert_called_once_with(tampered_token)
