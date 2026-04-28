#!/usr/bin/env python3
"""
Comprehensive test script for table management API endpoints.
Tests all table management functionality including CRUD operations, floor plans, and status management.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

import httpx
from app.common.supabase_client import get_supabase


class TableManagementAPITester:
    """Comprehensive tester for table management API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize the tester.
        
        Args:
            base_url: Base URL of the API server.
        """
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.auth_token: Optional[str] = None
        self.restaurant_id: Optional[str] = None
        self.test_data: Dict[str, Any] = {}
    
    async def setup_test_environment(self):
        """Set up test environment with authentication and test data."""
        print("🔧 Setting up test environment...")
        
        # For now, we'll use a mock restaurant ID and auth token
        # In a real scenario, you'd authenticate and get these values
        self.restaurant_id = "test-restaurant-id"
        self.auth_token = "test-auth-token"
        
        # Set up headers for authenticated requests
        self.headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        print("✅ Test environment setup complete")
    
    async def test_server_health(self) -> bool:
        """Test if the server is running and healthy.
        
        Returns:
            True if server is healthy, False otherwise.
        """
        print("🏥 Testing server health...")
        
        try:
            response = await self.client.get(f"{self.base_url}/healthz")
            if response.status_code == 200:
                print("✅ Server is healthy")
                return True
            else:
                print(f"❌ Server health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Server health check failed: {str(e)}")
            return False
    
    async def test_create_floor(self) -> bool:
        """Test floor creation endpoint.
        
        Returns:
            True if test passes, False otherwise.
        """
        print("🏢 Testing floor creation...")
        
        floor_data = {
            "name": "Ground Floor",
            "description": "Main dining area",
            "floor_number": 1,
            "layout_config": {
                "width": 800,
                "height": 600,
                "grid_size": 16
            }
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/tables/floors",
                json=floor_data,
                headers=self.headers
            )
            
            if response.status_code == 201:
                floor = response.json()
                self.test_data["floor_id"] = floor["id"]
                print(f"✅ Floor created successfully: {floor['name']} (ID: {floor['id']})")
                return True
            else:
                print(f"❌ Floor creation failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Floor creation failed: {str(e)}")
            return False
    
    async def test_get_floors(self) -> bool:
        """Test getting floors endpoint.
        
        Returns:
            True if test passes, False otherwise.
        """
        print("📋 Testing get floors...")
        
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/tables/floors",
                headers=self.headers
            )
            
            if response.status_code == 200:
                floors = response.json()
                print(f"✅ Retrieved {len(floors)} floors")
                return True
            else:
                print(f"❌ Get floors failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Get floors failed: {str(e)}")
            return False
    
    async def test_create_table(self) -> bool:
        """Test table creation endpoint.
        
        Returns:
            True if test passes, False otherwise.
        """
        print("🪑 Testing table creation...")
        
        table_data = {
            "floor_id": self.test_data.get("floor_id"),
            "table_number": "T001",
            "capacity": 4,
            "shape": "round",
            "category": "regular",
            "position": {"x": 100, "y": 100},
            "dimensions": {"width": 80, "height": 80},
            "rotation": 0.0,
            "special_requirements": [],
            "is_accessible": False,
            "has_power_outlet": False,
            "has_window_view": True,
            "min_party_size": 1,
            "max_party_size": 4,
            "notes": "Test table"
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/tables/",
                json=table_data,
                headers=self.headers
            )
            
            if response.status_code == 201:
                table = response.json()
                self.test_data["table_id"] = table["id"]
                print(f"✅ Table created successfully: {table['table_number']} (ID: {table['id']})")
                return True
            else:
                print(f"❌ Table creation failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Table creation failed: {str(e)}")
            return False
    
    async def test_get_tables(self) -> bool:
        """Test getting tables endpoint.
        
        Returns:
            True if test passes, False otherwise.
        """
        print("📋 Testing get tables...")
        
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/tables/",
                headers=self.headers
            )
            
            if response.status_code == 200:
                tables = response.json()
                print(f"✅ Retrieved {len(tables)} tables")
                return True
            else:
                print(f"❌ Get tables failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Get tables failed: {str(e)}")
            return False
    
    async def test_get_table_by_id(self) -> bool:
        """Test getting table by ID endpoint.
        
        Returns:
            True if test passes, False otherwise.
        """
        print("🔍 Testing get table by ID...")
        
        if not self.test_data.get("table_id"):
            print("❌ No table ID available for testing")
            return False
        
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/tables/{self.test_data['table_id']}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                table = response.json()
                print(f"✅ Retrieved table: {table['table_number']}")
                return True
            else:
                print(f"❌ Get table by ID failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Get table by ID failed: {str(e)}")
            return False
    
    async def test_update_table_status(self) -> bool:
        """Test updating table status endpoint.
        
        Returns:
            True if test passes, False otherwise.
        """
        print("🔄 Testing table status update...")
        
        if not self.test_data.get("table_id"):
            print("❌ No table ID available for testing")
            return False
        
        status_data = {"status": "occupied"}
        
        try:
            response = await self.client.patch(
                f"{self.base_url}/api/v1/tables/{self.test_data['table_id']}/status",
                json=status_data,
                headers=self.headers
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Table status updated: {result['message']}")
                return True
            else:
                print(f"❌ Table status update failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Table status update failed: {str(e)}")
            return False
    
    async def test_get_occupancy_stats(self) -> bool:
        """Test getting occupancy statistics endpoint.
        
        Returns:
            True if test passes, False otherwise.
        """
        print("📊 Testing occupancy statistics...")
        
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/tables/stats",
                headers=self.headers
            )
            
            if response.status_code == 200:
                stats = response.json()
                print(f"✅ Occupancy stats retrieved: {stats['occupancy_rate']}% occupancy")
                return True
            else:
                print(f"❌ Get occupancy stats failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Get occupancy stats failed: {str(e)}")
            return False
    
    async def test_get_floor_plan(self) -> bool:
        """Test getting floor plan endpoint.
        
        Returns:
            True if test passes, False otherwise.
        """
        print("🗺️ Testing floor plan retrieval...")
        
        if not self.test_data.get("floor_id"):
            print("❌ No floor ID available for testing")
            return False
        
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/tables/floors/{self.test_data['floor_id']}/plan",
                headers=self.headers
            )
            
            if response.status_code == 200:
                floor_plan = response.json()
                print(f"✅ Floor plan retrieved: {len(floor_plan['tables'])} tables on {floor_plan['floor']['name']}")
                return True
            else:
                print(f"❌ Get floor plan failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Get floor plan failed: {str(e)}")
            return False
    
    async def cleanup_test_data(self):
        """Clean up test data created during testing."""
        print("🧹 Cleaning up test data...")
        
        # Delete test table
        if self.test_data.get("table_id"):
            try:
                response = await self.client.delete(
                    f"{self.base_url}/api/v1/tables/{self.test_data['table_id']}",
                    headers=self.headers
                )
                if response.status_code == 204:
                    print("✅ Test table deleted")
                else:
                    print(f"⚠️ Failed to delete test table: {response.status_code}")
            except Exception as e:
                print(f"⚠️ Failed to delete test table: {str(e)}")
        
        # Delete test floor
        if self.test_data.get("floor_id"):
            try:
                response = await self.client.delete(
                    f"{self.base_url}/api/v1/tables/floors/{self.test_data['floor_id']}",
                    headers=self.headers
                )
                if response.status_code == 204:
                    print("✅ Test floor deleted")
                else:
                    print(f"⚠️ Failed to delete test floor: {response.status_code}")
            except Exception as e:
                print(f"⚠️ Failed to delete test floor: {str(e)}")
    
    async def run_all_tests(self) -> bool:
        """Run all table management API tests.
        
        Returns:
            True if all tests pass, False otherwise.
        """
        print("🚀 Starting Table Management API Tests")
        print("=" * 50)
        
        tests = [
            ("Server Health", self.test_server_health),
            ("Create Floor", self.test_create_floor),
            ("Get Floors", self.test_get_floors),
            ("Create Table", self.test_create_table),
            ("Get Tables", self.test_get_tables),
            ("Get Table by ID", self.test_get_table_by_id),
            ("Update Table Status", self.test_update_table_status),
            ("Get Occupancy Stats", self.test_get_occupancy_stats),
            ("Get Floor Plan", self.test_get_floor_plan),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n📝 Running: {test_name}")
            try:
                if await test_func():
                    passed += 1
                    print(f"✅ {test_name} PASSED")
                else:
                    print(f"❌ {test_name} FAILED")
            except Exception as e:
                print(f"❌ {test_name} FAILED with exception: {str(e)}")
        
        # Cleanup
        await self.cleanup_test_data()
        
        print("\n" + "=" * 50)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed!")
            return True
        else:
            print(f"❌ {total - passed} tests failed")
            return False
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


async def main():
    """Main test function."""
    tester = TableManagementAPITester()
    
    try:
        await tester.setup_test_environment()
        success = await tester.run_all_tests()
        return success
    finally:
        await tester.close()


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
