#!/usr/bin/env python3
"""Script to check if the user was created in the customers table."""

import asyncio

from app.common.supabase_client import get_supabase


async def check_created_user():
    """Check if the user was created in customers table."""
    print("=" * 60)
    print("CHECKING CREATED USER IN CUSTOMERS TABLE")
    print("=" * 60)

    try:
        client = get_supabase()
        print(f"✅ Connected to Supabase")

        # Check if user exists in customers table
        email = "test.user.new@gmail.com"
        print(f"\n🔍 Looking for user with email: {email}")

        result = client.table("customers").select("*").eq("email", email).execute()

        if result.data:
            print(f"✅ User found in customers table:")
            for user in result.data:
                print(f"   ID: {user['id']}")
                print(f"   Email: {user['email']}")
                print(f"   Phone: {user['phone']}")
                print(f"   Name: {user['name']}")
                print(f"   Created: {user['created_at']}")
        else:
            print(f"❌ No user found in customers table with email {email}")

        # Also check all users in customers table
        print(f"\n📊 All users in customers table:")
        all_result = client.table("customers").select("*").execute()

        if all_result.data:
            for i, user in enumerate(all_result.data):
                print(f"   User {i+1}: {user['email']} (ID: {user['id']})")
        else:
            print("   No users found in customers table")

        # Check Supabase Auth users
        print(f"\n🔍 Checking Supabase Auth users...")
        try:
            auth_user = client.auth.get_user()
            if auth_user.user:
                print(
                    f"✅ Current auth user: {auth_user.user.email} (ID: {auth_user.user.id})"
                )
            else:
                print("❌ No current auth user")
        except Exception as e:
            print(f"❌ Error getting auth user: {str(e)}")

    except Exception as e:
        print(f"❌ Failed to check user: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(check_created_user())
