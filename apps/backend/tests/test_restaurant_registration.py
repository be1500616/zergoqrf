"""Test restaurant registration end-to-end workflow.

This module contains tests for the complete restaurant registration process.
"""

import pytest
import asyncio
from httpx import AsyncClient
from app.main import app


class TestRestaurantRegistration:
    """Test class for restaurant registration workflow."""

    @pytest.mark.asyncio
    async def test_restaurant_registration_flow(self):
        """Test the complete restaurant registration flow."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Test data
            registration_data = {
                "name": "Test Restaurant",
                "description": "A test restaurant for automated testing",
                "address": "123 Test Street, Test City",
                "phone": "+91 9876543210",
                "email": "test@restaurant.com",
                "website": "https://testrestaurant.com",
                "cuisine_type": "Multi-Cuisine",
                "dining_style": "Casual Dining",
                "owner_email": f"owner{asyncio.current_task().get_name()}@test.com",
                "owner_password": "testpassword123",
                "owner_name": "Test Owner",
            }

            # 1. Register restaurant
            response = await client.post("/restaurants/register", json=registration_data)
            
            assert response.status_code == 201
            data = response.json()
            
            # Verify response structure
            assert "restaurant" in data
            assert "owner" in data
            assert "access_token" in data
            assert "refresh_token" in data
            
            restaurant = data["restaurant"]
            owner = data["owner"]
            access_token = data["access_token"]
            
            # Verify restaurant data
            assert restaurant["name"] == registration_data["name"]
            assert restaurant["description"] == registration_data["description"]
            assert restaurant["address"] == registration_data["address"]
            assert restaurant["phone"] == registration_data["phone"]
            assert restaurant["email"] == registration_data["email"]
            assert restaurant["website"] == registration_data["website"]
            assert restaurant["cuisine_type"] == registration_data["cuisine_type"]
            assert restaurant["dining_style"] == registration_data["dining_style"]
            assert restaurant["is_active"] is True
            assert len(restaurant["code"]) == 6  # Restaurant code should be 6 characters
            
            # Verify owner data
            assert owner["role"] == "owner"
            assert owner["is_active"] is True
            
            # 2. Test authenticated access to restaurant data
            headers = {"Authorization": f"Bearer {access_token}"}
            
            # Get restaurant by authenticated user
            response = await client.get("/restaurants/me", headers=headers)
            assert response.status_code == 200
            
            my_restaurant = response.json()
            assert my_restaurant["id"] == restaurant["id"]
            assert my_restaurant["name"] == restaurant["name"]
            
            # 3. Test public access by restaurant code
            restaurant_code = restaurant["code"]
            response = await client.get(f"/restaurants/{restaurant_code}")
            assert response.status_code == 200
            
            public_restaurant = response.json()
            assert public_restaurant["id"] == restaurant["id"]
            assert public_restaurant["name"] == restaurant["name"]
            assert public_restaurant["code"] == restaurant_code
            
            # 4. Test restaurant settings update
            settings_update = {
                "currency": "USD",
                "tax_rate": 0.10,
                "service_charge_rate": 0.05,
                "auto_accept_orders": False,
            }
            
            response = await client.put(
                "/restaurants/me/settings",
                json=settings_update,
                headers=headers
            )
            assert response.status_code == 200
            
            updated_restaurant = response.json()
            assert updated_restaurant["settings"]["currency"] == "USD"
            assert updated_restaurant["settings"]["tax_rate"] == 0.10
            assert updated_restaurant["settings"]["auto_accept_orders"] is False
            
            # 5. Test business hours update
            business_hours = {
                "monday": {"open": "09:00", "close": "22:00", "closed": False},
                "tuesday": {"open": "09:00", "close": "22:00", "closed": False},
                "wednesday": {"open": "09:00", "close": "22:00", "closed": False},
                "thursday": {"open": "09:00", "close": "22:00", "closed": False},
                "friday": {"open": "09:00", "close": "23:00", "closed": False},
                "saturday": {"open": "09:00", "close": "23:00", "closed": False},
                "sunday": {"closed": True},
            }
            
            response = await client.put(
                "/restaurants/me/business-hours",
                json=business_hours,
                headers=headers
            )
            assert response.status_code == 200
            
            updated_restaurant = response.json()
            assert updated_restaurant["business_hours"]["monday"]["open"] == "09:00"
            assert updated_restaurant["business_hours"]["sunday"]["closed"] is True
            
            # 6. Test staff management
            staff_data = {
                "email": f"staff{asyncio.current_task().get_name()}@test.com",
                "password": "staffpassword123",
                "name": "Test Staff Member",
                "role": "manager",
                "permissions": {
                    "manage_menu": True,
                    "manage_orders": True,
                    "view_analytics": True,
                },
            }
            
            response = await client.post(
                "/restaurants/me/staff",
                json=staff_data,
                headers=headers
            )
            assert response.status_code == 201
            
            staff_member = response.json()
            assert staff_member["role"] == "manager"
            assert staff_member["permissions"]["manage_menu"] is True
            
            # Get staff list
            response = await client.get("/restaurants/me/staff", headers=headers)
            assert response.status_code == 200
            
            staff_list = response.json()
            assert staff_list["total"] >= 2  # Owner + newly added staff
            
            # Update staff member
            staff_update = {
                "role": "kitchen",
                "permissions": {
                    "manage_orders": True,
                },
            }
            
            response = await client.put(
                f"/restaurants/me/staff/{staff_member['id']}",
                json=staff_update,
                headers=headers
            )
            assert response.status_code == 200
            
            updated_staff = response.json()
            assert updated_staff["role"] == "kitchen"
            
            print("✅ All restaurant registration and management tests passed!")

    @pytest.mark.asyncio
    async def test_restaurant_code_uniqueness(self):
        """Test that restaurant codes are unique."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Register multiple restaurants and verify unique codes
            codes = set()
            
            for i in range(5):
                registration_data = {
                    "name": f"Test Restaurant {i}",
                    "owner_email": f"owner{i}@uniquetest.com",
                    "owner_password": "testpassword123",
                }
                
                response = await client.post("/restaurants/register", json=registration_data)
                assert response.status_code == 201
                
                data = response.json()
                restaurant_code = data["restaurant"]["code"]
                
                # Verify code is unique
                assert restaurant_code not in codes
                codes.add(restaurant_code)
                
                # Verify code format (6 characters, alphanumeric, no confusing chars)
                assert len(restaurant_code) == 6
                assert restaurant_code.isalnum()
                assert '0' not in restaurant_code  # No confusing characters
                assert 'O' not in restaurant_code
                assert 'I' not in restaurant_code
                assert '1' not in restaurant_code
            
            print(f"✅ Generated {len(codes)} unique restaurant codes: {codes}")

    @pytest.mark.asyncio
    async def test_invalid_restaurant_registration(self):
        """Test restaurant registration with invalid data."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Test missing required fields
            invalid_data = {
                "description": "Missing name and owner info",
            }
            
            response = await client.post("/restaurants/register", json=invalid_data)
            assert response.status_code == 422  # Validation error
            
            # Test invalid email
            invalid_email_data = {
                "name": "Test Restaurant",
                "owner_email": "invalid-email",
                "owner_password": "testpassword123",
            }
            
            response = await client.post("/restaurants/register", json=invalid_email_data)
            assert response.status_code == 422
            
            # Test short password
            short_password_data = {
                "name": "Test Restaurant",
                "owner_email": "test@example.com",
                "owner_password": "123",
            }
            
            response = await client.post("/restaurants/register", json=short_password_data)
            assert response.status_code == 422
            
            print("✅ Invalid registration data properly rejected!")


if __name__ == "__main__":
    # Run tests directly
    import sys
    import os
    
    # Add the backend directory to Python path
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, backend_dir)
    
    # Run the tests
    pytest.main([__file__, "-v"])
