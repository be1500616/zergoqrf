"""Mock implementations for external services.

This package provides mock implementations for testing external
service integrations without actual network calls.
"""

from .external_services import (
    MockSupabaseAuth,
    MockSupabaseClient,
    MockSupabaseTable,
    create_mock_supabase_client,
)

__all__ = [
    "MockSupabaseClient",
    "MockSupabaseAuth",
    "MockSupabaseTable",
    "create_mock_supabase_client",
]
