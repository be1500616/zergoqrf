#!/usr/bin/env python3
"""Test script to systematically test all authentication endpoints."""

import asyncio
import json

from app.main import create_app
from fastapi.testclient import TestClient
from httpx import AsyncClient


async def test_endpoints():
    """Test all authentication endpoints systematically."""
    app = create_app()

    print("=" * 60)
    print("TESTING AUTHENTICATION ENDPOINTS")
    print("=" * 60)

    # Use TestClient for synchronous testing
    client = TestClient(app)

    # Test 1: Signup endpoint
    print("\n1. Testing POST /auth/signup")
    print("-" * 40)
    try:
        response = client.post(
            "/auth/signup",
            json={
                "email": "testuser@outlook.com",
                "password": "TestPassword123!",
                "name": "Test User",
                "role": "customer",
            },
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        if response.status_code != 200:
            print(f"❌ FAILED: Expected 200, got {response.status_code}")
        else:
            print("✅ SUCCESS")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

    # Test 2: Signin endpoint
    print("\n2. Testing POST /auth/signin")
    print("-" * 40)
    try:
        response = client.post(
            "/auth/signin",
            json={"email": "testuser@outlook.com", "password": "TestPassword123!"},
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        if response.status_code != 200:
            print(f"❌ FAILED: Expected 200, got {response.status_code}")
        else:
            print("✅ SUCCESS")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

    # Test 3: Phone send-otp endpoint
    print("\n3. Testing POST /auth/phone/send-otp")
    print("-" * 40)
    try:
        response = client.post("/auth/phone/send-otp", json={"phone": "+1234567890"})
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        if response.status_code != 200:
            print(f"❌ FAILED: Expected 200, got {response.status_code}")
        else:
            print("✅ SUCCESS")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

    # Test 4: Phone verify-otp endpoint
    print("\n4. Testing POST /auth/phone/verify-otp")
    print("-" * 40)
    try:
        response = client.post(
            "/auth/phone/verify-otp",
            json={"phone": "+1234567890", "otp": "123456", "name": "Test User"},
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        if response.status_code != 200:
            print(f"❌ FAILED: Expected 200, got {response.status_code}")
        else:
            print("✅ SUCCESS")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

    # Test 5: Anonymous session endpoint
    print("\n5. Testing POST /auth/anonymous-session")
    print("-" * 40)
    try:
        response = client.post(
            "/auth/anonymous-session",
            json={
                "restaurant_id": "d9fdc55e-2ed1-4ec6-a21a-2a3e4e3ad1c2",
                "table_id": "ff1bd990-325d-420b-a723-feb4b872c2b2",
            },
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        if response.status_code != 200:
            print(f"❌ FAILED: Expected 200, got {response.status_code}")
        else:
            print("✅ SUCCESS")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

    # Test 6: Refresh token endpoint (will fail without valid token)
    print("\n6. Testing POST /auth/refresh")
    print("-" * 40)
    try:
        response = client.post("/auth/refresh", json={"refresh_token": "dummy_token"})
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        print("ℹ️  Expected to fail without valid token")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

    print("\n" + "=" * 60)
    print("ENDPOINT TESTING COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_endpoints())
