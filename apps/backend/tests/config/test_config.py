"""Centralized test configuration.

This module contains all test environment settings, URLs, and configurations
that need to be shared across different test modules.
"""

import os
from typing import Dict, Any, Optional
from enum import Enum

from app.core.config import settings


class TestEnvironment(str, Enum):
    """Test environment types."""
    UNIT = "unit"
    INTEGRATION = "integration"
    STAGING = "staging"
    PRODUCTION = "production"


class TestConfig:
    """Centralized test configuration class."""

    # Environment detection
    ENVIRONMENT = os.getenv("TEST_ENV", TestEnvironment.UNIT)

    # Test database configuration
    DATABASE_URL = os.getenv(
        "TEST_DATABASE_URL",
        "sqlite+aiosqlite:///./test.db"
    )

    # Supabase configuration for integration tests
    SUPABASE_URL = settings.supabase_url
    SUPABASE_ANON_KEY = settings.supabase_anon_key
    SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    # Test API configuration
    API_BASE_URL = "http://test"
    API_TIMEOUT = 30

    # Authentication test settings
    AUTH_TOKEN_EXPIRY_SECONDS = 3600
    REFRESH_TOKEN_EXPIRY_SECONDS = 86400 * 7  # 7 days

    # Rate limiting test settings
    RATE_LIMIT_REQUESTS_PER_MINUTE = 60
    RATE_LIMIT_BURST_SIZE = 10

    # Test data cleanup settings
    AUTO_CLEANUP_ENABLED = os.getenv("TEST_AUTO_CLEANUP", "true").lower() == "true"
    CLEANUP_BATCH_SIZE = 100

    # Performance test settings
    LOAD_TEST_CONCURRENT_USERS = 10
    LOAD_TEST_DURATION_SECONDS = 60

    # Security test settings
    TEST_JWT_ALGORITHM = "HS256"
    TEST_JWT_SECRET = os.getenv("TEST_JWT_SECRET", "test-secret-key")

    # Email test settings
    TEST_EMAIL_DOMAIN = "example.com"
    TEST_EMAIL_PASSWORD = "TestPassword123!"

    # Phone test settings
    TEST_PHONE_PREFIX = "+123456789"
    TEST_OTP_CODE = "123456"

    # Logging configuration
    LOG_LEVEL = os.getenv("TEST_LOG_LEVEL", "WARNING")
    ENABLE_SQL_LOGGING = os.getenv("TEST_ENABLE_SQL_LOGGING", "false").lower() == "true"

    # Mock configuration
    USE_MOCK_SERVICES = ENVIRONMENT == TestEnvironment.UNIT
    MOCK_EXTERNAL_APIS = os.getenv("TEST_MOCK_APIS", "true").lower() == "true"

    # Test markers
    MARKERS = {
        "unit": "Unit tests (no external dependencies)",
        "integration": "Integration tests (with external services)",
        "e2e": "End-to-end tests (full workflow)",
        "slow": "Slow running tests",
        "auth": "Authentication related tests",
        "database": "Database related tests",
        "api": "API endpoint tests",
        "security": "Security related tests",
        "performance": "Performance tests"
    }

    # Test data configuration
    UNIQUE_ID_LENGTH = 8
    MAX_TEST_USERS_PER_RUN = 50
    MAX_TEST_RESTAURANTS_PER_RUN = 20

    # Session configuration
    SESSION_TIMEOUT_SECONDS = 3600
    ANONYMOUS_SESSION_TIMEOUT_SECONDS = 7200

    # Restaurant configuration
    MAX_TABLES_PER_RESTAURANT = 50
    MAX_MENU_ITEMS_PER_RESTAURANT = 200

    # Order configuration
    MAX_ITEMS_PER_ORDER = 20
    MAX_ORDER_AMOUNT = 10000.00

    @classmethod
    def is_integration_test(cls) -> bool:
        """Check if running integration tests."""
        return cls.ENVIRONMENT in [TestEnvironment.INTEGRATION, TestEnvironment.STAGING]

    @classmethod
    def is_production_test(cls) -> bool:
        """Check if running against production."""
        return cls.ENVIRONMENT == TestEnvironment.PRODUCTION

    @classmethod
    def get_supabase_config(cls) -> Dict[str, Optional[str]]:
        """Get Supabase configuration for tests."""
        return {
            "url": cls.SUPABASE_URL,
            "anon_key": cls.SUPABASE_ANON_KEY,
            "service_key": cls.SUPABASE_SERVICE_KEY
        }

    @classmethod
    def get_auth_test_config(cls) -> Dict[str, Any]:
        """Get authentication test configuration."""
        return {
            "token_expiry": cls.AUTH_TOKEN_EXPIRY_SECONDS,
            "refresh_expiry": cls.REFRESH_TOKEN_EXPIRY_SECONDS,
            "test_email": cls.TEST_EMAIL_DOMAIN,
            "test_password": cls.TEST_EMAIL_PASSWORD,
            "test_phone": cls.TEST_PHONE_PREFIX,
            "test_otp": cls.TEST_OTP_CODE
        }

    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        """Validate test configuration and return status."""
        validation_result = {
            "valid": True,
            "warnings": [],
            "errors": []
        }

        # Check essential configurations
        if cls.is_integration_test():
            if not cls.SUPABASE_URL:
                validation_result["errors"].append("SUPABASE_URL not configured for integration tests")
                validation_result["valid"] = False

            if not cls.SUPABASE_ANON_KEY:
                validation_result["errors"].append("SUPABASE_ANON_KEY not configured for integration tests")
                validation_result["valid"] = False

        # Check optional configurations
        if not cls.DATABASE_URL:
            validation_result["warnings"].append("TEST_DATABASE_URL not configured, using default SQLite")

        if cls.is_production_test() and not cls.SUPABASE_SERVICE_KEY:
            validation_result["warnings"].append("SUPABASE_SERVICE_KEY not configured for production tests")

        return validation_result


# Global test configuration instance
TEST_CONFIG = TestConfig()

# Validate configuration on import
CONFIG_VALIDATION = TEST_CONFIG.validate_config()
if not CONFIG_VALIDATION["valid"]:
    raise ValueError(f"Invalid test configuration: {CONFIG_VALIDATION['errors']}")
elif CONFIG_VALIDATION["warnings"]:
    print(f"Test configuration warnings: {CONFIG_VALIDATION['warnings']}")