#!/usr/bin/env python3
"""
Test script to verify restaurant registration works after schema migration.
Run this after applying the database migration.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the backend directory to Python path (from scripts/dev/ to apps/backend)
backend_dir = Path(__file__).parent.parent.parent / "apps" / "backend"
sys.path.insert(0, str(backend_dir))

import httpx
from app.common.supabase_client import get_supabase


async def test_schema_verification():
    """Test that the schema migration was applied successfully."""
    print("🔍 Testing schema verification...")

    try:
        client = get_supabase()

        # Try to query with all expected columns
        result = (
            client.table("restaurants")
            .select(
                "id,name,code,address,description,phone,email,website,"
                "cuisine_type,dining_style,is_active,business_hours,settings,"
                "created_at,updated_at"
            )
            .limit(1)
            .execute()
        )

        print("✅ Schema verification successful!")
        print(
            f"   Available columns: {len(result.data[0].keys()) if result.data else 'All columns accessible'}"
        )
        return True

    except Exception as e:
        print(f"❌ Schema verification failed: {e}")
        print("   Please apply the migration first!")
        return False


async def test_restaurant_registration():
    """Test the restaurant registration endpoint."""
    print("\n🧪 Testing restaurant registration endpoint...")

    try:
        # Test data with all fields including the previously missing ones
        registration_data = {
            "name": "Test Restaurant After Migration",
            "description": "A test restaurant to verify schema fix",
            "address": "123 Migration Test Street, Schema City, SC 12345",
            "phone": "+1-555-SCHEMA",
            "email": "test@migration-fix.com",
            "website": "https://migration-test.com",
            "cuisine_type": "International",
            "dining_style": "Casual Dining",
            "owner_email": "owner@migration-test.com",
            "owner_password": "SecurePassword123!",
            "owner_name": "Migration Test Owner",
        }

        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            response = await client.post(
                "/restaurants/register", json=registration_data
            )

            print(f"   Response status: {response.status_code}")

            if response.status_code == 201:
                data = response.json()
                print("✅ Registration successful!")
                print(f"   Restaurant ID: {data['restaurant']['id']}")
                print(f"   Restaurant Code: {data['restaurant']['code']}")
                print(f"   Address: {data['restaurant']['address']}")
                print(f"   Description: {data['restaurant']['description']}")
                print(f"   Phone: {data['restaurant']['phone']}")
                print(f"   Email: {data['restaurant']['email']}")
                print(f"   Website: {data['restaurant']['website']}")
                print(f"   Cuisine Type: {data['restaurant']['cuisine_type']}")
                print(f"   Dining Style: {data['restaurant']['dining_style']}")
                print(f"   Is Active: {data['restaurant']['is_active']}")

                # Test public access by restaurant code
                code = data["restaurant"]["code"]
                public_response = await client.get(f"/restaurants/{code}")

                if public_response.status_code == 200:
                    print("✅ Public restaurant access working!")
                else:
                    print(f"❌ Public access failed: {public_response.status_code}")

                return True

            else:
                print(f"❌ Registration failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return False

    except Exception as e:
        print(f"❌ Registration test failed: {e}")
        return False


async def test_backend_server():
    """Test if the backend server is running."""
    print("🔌 Testing backend server connection...")

    try:
        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            response = await client.get("/healthz")

            if response.status_code == 200:
                print("✅ Backend server is running!")
                return True
            else:
                print(f"❌ Backend server health check failed: {response.status_code}")
                return False

    except Exception as e:
        print(f"❌ Cannot connect to backend server: {e}")
        print("   Please start the backend server first:")
        print(
            "   cd apps/backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
        )
        return False


async def main():
    """Main test function."""
    print("🚀 Restaurant Registration Test Suite")
    print("=====================================")

    # Test 1: Backend server
    if not await test_backend_server():
        return False

    # Test 2: Schema verification
    if not await test_schema_verification():
        print("\n📋 MIGRATION REQUIRED:")
        print("Please apply the migration SQL in your Supabase dashboard:")
        print(
            "1. Go to https://supabase.com/dashboard/project/kpsyzsmgzuweadpnffwy/sql"
        )
        print(
            "2. Copy the SQL from: infra/supabase/migrations/20250924000003_add_restaurant_profile_fields.sql"
        )
        print("3. Execute it")
        print("4. Run this script again")
        return False

    # Test 3: Restaurant registration
    if not await test_restaurant_registration():
        return False

    print("\n🎉 ALL TESTS PASSED!")
    print("The restaurant registration system is working correctly!")
    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
