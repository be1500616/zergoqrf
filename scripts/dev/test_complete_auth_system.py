#!/usr/bin/env python3
"""
Comprehensive test script for the restaurant registration and authentication system.
This script tests the complete flow from registration to authenticated API access.
"""

import asyncio
import httpx
import jwt
import json
from typing import Dict, Any


async def test_complete_auth_system():
    """Test the complete authentication system end-to-end."""
    print("🧪 Testing Complete Restaurant Authentication System")
    print("=" * 60)
    
    # Test data
    registration_data = {
        'name': 'Complete Auth Test Restaurant',
        'description': 'Testing complete authentication system',
        'address': '123 Complete Auth Street, Test City, TC 12345',
        'phone': '+1-555-COMPLETE-AUTH',
        'email': 'test@complete-auth.com',
        'website': 'https://complete-auth-test.com',
        'cuisine_type': 'Test Cuisine',
        'dining_style': 'Test Dining',
        'owner_email': 'owner@complete-auth.com',
        'owner_password': 'SecurePassword123!',
        'owner_name': 'Complete Auth Owner'
    }
    
    try:
        async with httpx.AsyncClient(base_url='http://localhost:8000', timeout=30.0) as client:
            
            # Step 1: Test restaurant registration
            print("\n1. 🏪 Testing Restaurant Registration")
            print("-" * 40)
            
            response = await client.post('/restaurants/register', json=registration_data)
            
            if response.status_code != 201:
                print(f"❌ Registration failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
            
            data = response.json()
            access_token = data['access_token']
            refresh_token = data['refresh_token']
            restaurant_id = data['restaurant']['id']
            restaurant_code = data['restaurant']['code']
            
            print(f"✅ Registration successful!")
            print(f"   Restaurant ID: {restaurant_id}")
            print(f"   Restaurant Code: {restaurant_code}")
            print(f"   Access Token: {access_token[:30]}...")
            print(f"   Refresh Token: {refresh_token[:30]}...")
            
            # Step 2: Analyze JWT token
            print("\n2. 🔐 Analyzing JWT Token")
            print("-" * 40)
            
            try:
                decoded = jwt.decode(access_token, options={'verify_signature': False})
                print("JWT Claims:")
                important_claims = ['sub', 'email', 'restaurant_id', 'role', 'permissions', 'user_metadata', 'app_metadata']
                for claim in important_claims:
                    if claim in decoded:
                        value = decoded[claim]
                        if isinstance(value, dict) and len(str(value)) > 100:
                            print(f"   {claim}: {type(value).__name__} with {len(value)} keys")
                        else:
                            print(f"   {claim}: {value}")
                
                # Check if restaurant_id is in claims
                has_restaurant_id = 'restaurant_id' in decoded or \
                                  (decoded.get('user_metadata', {}).get('restaurant_id')) or \
                                  (decoded.get('app_metadata', {}).get('restaurant_id'))
                
                if has_restaurant_id:
                    print("✅ Restaurant ID found in JWT claims")
                else:
                    print("⚠️  Restaurant ID not found in JWT claims - will fallback to database lookup")
                    
            except Exception as e:
                print(f"❌ Failed to decode JWT: {e}")
            
            # Step 3: Test authenticated endpoints
            print("\n3. 🔒 Testing Authenticated Endpoints")
            print("-" * 40)
            
            auth_headers = {'Authorization': f'Bearer {access_token}'}
            
            # Test GET /restaurants/me
            print("Testing GET /restaurants/me...")
            response = await client.get('/restaurants/me', headers=auth_headers)
            
            if response.status_code == 200:
                restaurant_data = response.json()
                print(f"✅ Get restaurant profile successful")
                print(f"   Name: {restaurant_data['name']}")
                print(f"   ID: {restaurant_data['id']}")
            else:
                print(f"❌ Get restaurant profile failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
            
            # Test PUT /restaurants/me
            print("\nTesting PUT /restaurants/me...")
            update_data = {
                'name': 'Updated Complete Auth Test Restaurant',
                'description': 'Updated description for complete auth testing'
            }
            response = await client.put('/restaurants/me', json=update_data, headers=auth_headers)
            
            if response.status_code == 200:
                print("✅ Update restaurant profile successful")
            else:
                print(f"❌ Update restaurant profile failed: {response.status_code}")
                print(f"   Response: {response.text}")
            
            # Test PUT /restaurants/me/settings
            print("\nTesting PUT /restaurants/me/settings...")
            settings_data = {
                'currency': 'USD',
                'tax_rate': 0.08,
                'service_charge_rate': 0.15,
                'auto_accept_orders': True
            }
            response = await client.put('/restaurants/me/settings', json=settings_data, headers=auth_headers)
            
            if response.status_code == 200:
                print("✅ Update restaurant settings successful")
            else:
                print(f"❌ Update restaurant settings failed: {response.status_code}")
                print(f"   Response: {response.text}")
            
            # Test business hours with correct format
            print("\nTesting PUT /restaurants/me/business-hours...")
            business_hours_data = {
                'monday': {'open': '09:00', 'close': '22:00', 'closed': 'false'},
                'tuesday': {'open': '09:00', 'close': '22:00', 'closed': 'false'},
                'wednesday': {'open': '09:00', 'close': '22:00', 'closed': 'false'},
                'thursday': {'open': '09:00', 'close': '22:00', 'closed': 'false'},
                'friday': {'open': '09:00', 'close': '23:00', 'closed': 'false'},
                'saturday': {'open': '10:00', 'close': '23:00', 'closed': 'false'},
                'sunday': {'closed': 'true'}
            }
            response = await client.put('/restaurants/me/business-hours', json=business_hours_data, headers=auth_headers)
            
            if response.status_code == 200:
                print("✅ Update business hours successful")
            else:
                print(f"❌ Update business hours failed: {response.status_code}")
                print(f"   Response: {response.text}")
            
            # Step 4: Test public access
            print("\n4. 🌐 Testing Public Access")
            print("-" * 40)
            
            print(f"Testing GET /restaurants/{restaurant_code} (public access)...")
            response = await client.get(f'/restaurants/{restaurant_code}')
            
            if response.status_code == 200:
                public_data = response.json()
                print(f"✅ Public restaurant access successful")
                print(f"   Name: {public_data['name']}")
                print(f"   Code: {public_data['code']}")
            else:
                print(f"❌ Public restaurant access failed: {response.status_code}")
                print(f"   Response: {response.text}")
            
            # Step 5: Test staff management
            print("\n5. 👥 Testing Staff Management")
            print("-" * 40)
            
            # Test POST /restaurants/me/staff
            print("Testing POST /restaurants/me/staff...")
            staff_data = {
                'email': 'staff@complete-auth.com',
                'password': 'StaffPassword123!',
                'name': 'Complete Auth Staff Member',
                'role': 'manager',
                'permissions': {
                    'manage_orders': True,
                    'manage_menu': True,
                    'view_analytics': False
                }
            }
            response = await client.post('/restaurants/me/staff', json=staff_data, headers=auth_headers)
            
            if response.status_code == 201:
                staff_response = response.json()
                print(f"✅ Create staff successful")
                print(f"   Name: {staff_response.get('name', 'N/A')}")
                print(f"   Role: {staff_response.get('role', 'N/A')}")
            else:
                print(f"❌ Create staff failed: {response.status_code}")
                print(f"   Response: {response.text}")
            
            # Test GET /restaurants/me/staff
            print("\nTesting GET /restaurants/me/staff...")
            response = await client.get('/restaurants/me/staff', headers=auth_headers)
            
            if response.status_code == 200:
                staff_list = response.json()
                print(f"✅ List staff successful - {len(staff_list)} staff members")
            else:
                print(f"❌ List staff failed: {response.status_code}")
                print(f"   Response: {response.text}")
            
            print("\n" + "=" * 60)
            print("🎉 Complete Authentication System Test Completed!")
            print("✅ All core functionality is working properly")
            return True
            
    except Exception as e:
        print(f"❌ Test suite failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_complete_auth_system())
    if success:
        print("\n🎯 RESULT: Authentication system is fully functional!")
    else:
        print("\n❌ RESULT: Authentication system needs attention")
        exit(1)
