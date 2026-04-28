#!/usr/bin/env python3
"""Debug script to test Supabase integration."""

import asyncio
import traceback

from app.common.supabase_client import get_supabase
from app.features.auth.domain.auth_vos import Email


async def test_supabase():
    """Test Supabase integration."""
    print("Testing Supabase integration...")

    try:
        # Get Supabase client
        client = get_supabase()
        print(f"✅ Supabase client created: {type(client)}")

        # Test email validation with different domains
        test_emails = [
            "test@gmail.com",
            "testuser@outlook.com",
            "demo@test.com",
            "test@example.com",
        ]

        for test_email in test_emails:
            print(f"\nTesting email: {test_email}")
            try:
                email = Email(test_email)
                print(f"✅ Email validation successful: {email.value}")

                # Test Supabase Auth signup
                print("Testing Supabase Auth signup...")
                auth_response = client.auth.sign_up(
                    {
                        "email": test_email,
                        "password": "TestPassword123!",
                        "options": {"data": {"name": "Test User", "role": "customer"}},
                    }
                )
                print(f"Auth response: {auth_response}")
                if hasattr(auth_response, "user") and auth_response.user:
                    print(f"✅ User created: {auth_response.user.id}")
                    break  # Success, exit loop
                else:
                    print(f"❌ No user in response: {auth_response}")
            except Exception as e:
                print(f"❌ Supabase Auth error for {test_email}: {str(e)}")
                # Continue to next email

    except Exception as e:
        print(f"❌ General error: {str(e)}")
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_supabase())
