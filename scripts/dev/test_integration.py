#!/usr/bin/env python3
"""Integration test script for ZERGO QR Restaurant Setup.

This script tests the complete Story 1.1 implementation including:
- Backend API endpoints
- Database operations
- Authentication flow
- Restaurant registration and management

Run this script to verify the end-to-end functionality.
"""

import asyncio
import json
import sys
import time
from typing import Dict, Any

import httpx


class IntegrationTester:
    """Integration tester for restaurant setup functionality."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize the tester.
        
        Args:
            base_url: Base URL of the FastAPI backend.
        """
        self.base_url = base_url
        self.session_data: Dict[str, Any] = {}

    async def run_tests(self) -> bool:
        """Run all integration tests.
        
        Returns:
            True if all tests pass, False otherwise.
        """
        print("🚀 Starting ZERGO QR Integration Tests")
        print("=" * 50)
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Test 1: Health check
                await self._test_health_check(client)
                
                # Test 2: Restaurant registration
                await self._test_restaurant_registration(client)
                
                # Test 3: Restaurant data retrieval
                await self._test_restaurant_data_access(client)
                
                # Test 4: Restaurant settings management
                await self._test_restaurant_settings(client)
                
                # Test 5: Business hours management
                await self._test_business_hours(client)
                
                # Test 6: Staff management
                await self._test_staff_management(client)
                
                # Test 7: Public restaurant access (QR code simulation)
                await self._test_public_restaurant_access(client)
                
                print("\n" + "=" * 50)
                print("✅ ALL INTEGRATION TESTS PASSED!")
                print("🎉 Story 1.1 (Restaurant Setup) is working correctly!")
                return True
                
        except Exception as e:
            print(f"\n❌ INTEGRATION TEST FAILED: {e}")
            return False

    async def _test_health_check(self, client: httpx.AsyncClient):
        """Test API health check."""
        print("\n📋 Test 1: API Health Check")
        
        response = await client.get(f"{self.base_url}/health")
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        
        print("✅ API is healthy and responding")

    async def _test_restaurant_registration(self, client: httpx.AsyncClient):
        """Test restaurant registration flow."""
        print("\n🏪 Test 2: Restaurant Registration")
        
        # Generate unique email for this test run
        timestamp = int(time.time())
        registration_data = {
            "name": "ZERGO Test Restaurant",
            "description": "A test restaurant for integration testing",
            "address": "123 Integration Test Street, Test City, TC 12345",
            "phone": "+91 9876543210",
            "email": "restaurant@zergotest.com",
            "website": "https://zergotest.com",
            "cuisine_type": "Multi-Cuisine",
            "dining_style": "Casual Dining",
            "owner_email": f"owner{timestamp}@zergotest.com",
            "owner_password": "SecurePassword123!",
            "owner_name": "Test Restaurant Owner",
        }
        
        response = await client.post(
            f"{self.base_url}/restaurants/register",
            json=registration_data
        )
        
        assert response.status_code == 201, f"Registration failed: {response.status_code} - {response.text}"
        
        data = response.json()
        
        # Verify response structure
        required_fields = ["restaurant", "owner", "access_token", "refresh_token"]
        for field in required_fields:
            assert field in data, f"Missing field in response: {field}"
        
        # Store session data for subsequent tests
        self.session_data = {
            "restaurant": data["restaurant"],
            "owner": data["owner"],
            "access_token": data["access_token"],
            "refresh_token": data["refresh_token"],
        }
        
        restaurant = data["restaurant"]
        
        # Verify restaurant data
        assert restaurant["name"] == registration_data["name"]
        assert restaurant["description"] == registration_data["description"]
        assert restaurant["is_active"] is True
        assert len(restaurant["code"]) == 6
        
        print(f"✅ Restaurant registered successfully!")
        print(f"   - Name: {restaurant['name']}")
        print(f"   - Code: {restaurant['code']}")
        print(f"   - Owner: {data['owner']['role']}")

    async def _test_restaurant_data_access(self, client: httpx.AsyncClient):
        """Test authenticated restaurant data access."""
        print("\n🔐 Test 3: Restaurant Data Access")
        
        headers = {"Authorization": f"Bearer {self.session_data['access_token']}"}
        
        # Get restaurant data
        response = await client.get(f"{self.base_url}/restaurants/me", headers=headers)
        assert response.status_code == 200, f"Failed to get restaurant data: {response.status_code}"
        
        restaurant_data = response.json()
        assert restaurant_data["id"] == self.session_data["restaurant"]["id"]
        
        print("✅ Authenticated restaurant data access working")

    async def _test_restaurant_settings(self, client: httpx.AsyncClient):
        """Test restaurant settings management."""
        print("\n⚙️ Test 4: Restaurant Settings Management")
        
        headers = {"Authorization": f"Bearer {self.session_data['access_token']}"}
        
        # Update restaurant settings
        settings_update = {
            "currency": "USD",
            "tax_rate": 0.15,
            "service_charge_rate": 0.10,
            "service_model": "self_service",
            "auto_accept_orders": True,
            "estimated_prep_time": 25,
            "email_notifications": True,
        }
        
        response = await client.put(
            f"{self.base_url}/restaurants/me/settings",
            json=settings_update,
            headers=headers
        )
        
        assert response.status_code == 200, f"Settings update failed: {response.status_code}"
        
        updated_restaurant = response.json()
        settings = updated_restaurant["settings"]
        
        assert settings["currency"] == "USD"
        assert settings["tax_rate"] == 0.15
        assert settings["auto_accept_orders"] is True
        
        print("✅ Restaurant settings management working")

    async def _test_business_hours(self, client: httpx.AsyncClient):
        """Test business hours management."""
        print("\n🕒 Test 5: Business Hours Management")
        
        headers = {"Authorization": f"Bearer {self.session_data['access_token']}"}
        
        # Update business hours
        business_hours = {
            "monday": {"open": "09:00", "close": "22:00", "closed": False},
            "tuesday": {"open": "09:00", "close": "22:00", "closed": False},
            "wednesday": {"open": "09:00", "close": "22:00", "closed": False},
            "thursday": {"open": "09:00", "close": "22:00", "closed": False},
            "friday": {"open": "09:00", "close": "23:00", "closed": False},
            "saturday": {"open": "10:00", "close": "23:00", "closed": False},
            "sunday": {"closed": True},
        }
        
        response = await client.put(
            f"{self.base_url}/restaurants/me/business-hours",
            json=business_hours,
            headers=headers
        )
        
        assert response.status_code == 200, f"Business hours update failed: {response.status_code}"
        
        updated_restaurant = response.json()
        hours = updated_restaurant["business_hours"]
        
        assert hours["monday"]["open"] == "09:00"
        assert hours["sunday"]["closed"] is True
        
        print("✅ Business hours management working")

    async def _test_staff_management(self, client: httpx.AsyncClient):
        """Test staff management functionality."""
        print("\n👥 Test 6: Staff Management")
        
        headers = {"Authorization": f"Bearer {self.session_data['access_token']}"}
        
        # Add a staff member
        timestamp = int(time.time())
        staff_data = {
            "email": f"staff{timestamp}@zergotest.com",
            "password": "StaffPassword123!",
            "name": "Test Staff Member",
            "role": "manager",
            "permissions": {
                "manage_menu": True,
                "manage_orders": True,
                "view_analytics": True,
            },
        }
        
        response = await client.post(
            f"{self.base_url}/restaurants/me/staff",
            json=staff_data,
            headers=headers
        )
        
        assert response.status_code == 201, f"Staff creation failed: {response.status_code}"
        
        staff_member = response.json()
        assert staff_member["role"] == "manager"
        assert staff_member["permissions"]["manage_menu"] is True
        
        # Get staff list
        response = await client.get(f"{self.base_url}/restaurants/me/staff", headers=headers)
        assert response.status_code == 200, f"Staff list retrieval failed: {response.status_code}"
        
        staff_list = response.json()
        assert staff_list["total"] >= 2  # Owner + newly added staff
        
        print(f"✅ Staff management working (Total staff: {staff_list['total']})")

    async def _test_public_restaurant_access(self, client: httpx.AsyncClient):
        """Test public restaurant access via QR code."""
        print("\n📱 Test 7: Public Restaurant Access (QR Code Simulation)")
        
        restaurant_code = self.session_data["restaurant"]["code"]
        
        # Access restaurant by code (simulating QR code scan)
        response = await client.get(f"{self.base_url}/restaurants/{restaurant_code}")
        assert response.status_code == 200, f"Public access failed: {response.status_code}"
        
        public_restaurant = response.json()
        assert public_restaurant["code"] == restaurant_code
        assert public_restaurant["is_active"] is True
        
        print(f"✅ Public restaurant access working (Code: {restaurant_code})")


async def main():
    """Main function to run integration tests."""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:8000"
    
    print(f"Testing against: {base_url}")
    
    tester = IntegrationTester(base_url)
    success = await tester.run_tests()
    
    if success:
        print("\n🎯 Integration test summary:")
        print("   ✅ Restaurant registration flow")
        print("   ✅ Authentication and authorization")
        print("   ✅ Restaurant settings management")
        print("   ✅ Business hours configuration")
        print("   ✅ Staff management system")
        print("   ✅ Public QR code access")
        print("\n🚀 Story 1.1 (Restaurant Setup) is COMPLETE and WORKING!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the backend server and database.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
