#!/usr/bin/env python3
"""
Comprehensive Restaurant API Endpoint Testing Script
Tests all restaurant-related endpoints systematically
"""

import asyncio
import json
import time
from typing import Dict, Any, List
import httpx
import uuid

# Test configuration
BASE_URL = "http://127.0.0.1:8001"
TEST_RESTAURANT_ID = "550e8400-e29b-41d4-a716-446655440000"
TEST_RESTAURANT_CODE = "TEST001"

class RestaurantAPITester:``
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.test_results = []
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def log_test(self, endpoint: str, method: str, status_code: int, 
                 response_time: float, success: bool, error: str = None):
        """Log test result"""
        result = {
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "response_time_ms": round(response_time * 1000, 2),
            "success": success,
            "error": error,
            "timestamp": time.time()
        }
        self.test_results.append(result)
        
        status_emoji = "✅" if success else "❌"
        print(f"{status_emoji} {method} {endpoint} - {status_code} ({result['response_time_ms']}ms)")
        if error:
            print(f"   Error: {error}")
    
    async def test_endpoint(self, method: str, endpoint: str, 
                          data: Dict[Any, Any] = None, 
                          expected_status: int = 200) -> Dict[str, Any]:
        """Test a single endpoint"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            if method == "GET":
                response = await self.client.get(url)
            elif method == "POST":
                response = await self.client.post(url, json=data)
            elif method == "PUT":
                response = await self.client.put(url, json=data)
            elif method == "DELETE":
                response = await self.client.delete(url)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response_time = time.time() - start_time
            success = response.status_code == expected_status
            
            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text}
            
            self.log_test(endpoint, method, response.status_code, 
                         response_time, success, 
                         None if success else f"Expected {expected_status}, got {response.status_code}")
            
            return {
                "status_code": response.status_code,
                "data": response_data,
                "response_time": response_time,
                "success": success
            }
            
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test(endpoint, method, 0, response_time, False, str(e))
            return {
                "status_code": 0,
                "data": {"error": str(e)},
                "response_time": response_time,
                "success": False
            }
    
    async def test_health_check(self):
        """Test health check endpoint"""
        print("\n🏥 Testing Health Check...")
        return await self.test_endpoint("GET", "/healthz")
    
    async def test_restaurant_by_code(self):
        """Test getting restaurant by code"""
        print("\n🏪 Testing Restaurant Retrieval by Code...")
        return await self.test_endpoint("GET", f"/restaurants/{TEST_RESTAURANT_CODE}")
    
    async def test_restaurant_registration(self):
        """Test restaurant registration"""
        print("\n📝 Testing Restaurant Registration...")
        
        # Generate unique test data
        unique_id = str(uuid.uuid4())[:8]
        test_data = {
            "name": f"Test Restaurant {unique_id}",
            "code": f"TEST{unique_id}",
            "owner_email": f"owner{unique_id}@test.com",
            "owner_password": "TestPassword123!",
            "business_hours": {
                "monday": {"open": "09:00", "close": "22:00"},
                "tuesday": {"open": "09:00", "close": "22:00"}
            },
            "settings": {
                "currency": "INR",
                "timezone": "Asia/Kolkata"
            }
        }
        
        return await self.test_endpoint("POST", "/restaurants/register", 
                                      data=test_data, expected_status=201)
    
    async def test_menu_endpoints(self):
        """Test menu-related endpoints"""
        print("\n🍽️ Testing Menu Endpoints...")
        
        results = []
        
        # Test get menu categories
        results.append(await self.test_endpoint("GET", f"/menu/{TEST_RESTAURANT_ID}/categories"))
        
        # Test get menu items
        results.append(await self.test_endpoint("GET", f"/menu/{TEST_RESTAURANT_ID}/items"))
        
        # Test create menu item
        test_item = {
            "name": f"Test Item {uuid.uuid4().hex[:8]}",
            "description": "Test menu item description",
            "price": 199.99,
            "category": "Test Category",
            "is_available": True
        }
        results.append(await self.test_endpoint("POST", f"/menu/{TEST_RESTAURANT_ID}/items", 
                                              data=test_item, expected_status=201))
        
        return results
    
    async def test_table_endpoints(self):
        """Test table management endpoints"""
        print("\n🪑 Testing Table Management Endpoints...")
        
        results = []
        
        # Test get tables
        results.append(await self.test_endpoint("GET", f"/api/v1/restaurants/{TEST_RESTAURANT_ID}/tables"))
        
        # Test create table
        test_table = {
            "table_number": f"T{uuid.uuid4().hex[:4]}",
            "capacity": 4,
            "position": {"x": 100, "y": 200}
        }
        results.append(await self.test_endpoint("POST", f"/api/v1/restaurants/{TEST_RESTAURANT_ID}/tables", 
                                              data=test_table, expected_status=201))
        
        return results
    
    async def test_qr_endpoints(self):
        """Test QR code generation endpoints"""
        print("\n🔲 Testing QR Code Endpoints...")
        
        results = []
        
        # Test QR code generation for table
        results.append(await self.test_endpoint("GET", f"/api/v1/qr/table/{TEST_RESTAURANT_ID}/T001"))
        
        # Test QR code generation for restaurant
        results.append(await self.test_endpoint("GET", f"/api/v1/qr/restaurant/{TEST_RESTAURANT_CODE}"))
        
        return results
    
    async def test_public_menu_endpoints(self):
        """Test public menu endpoints"""
        print("\n🌐 Testing Public Menu Endpoints...")
        
        results = []
        
        # Test public restaurant menu
        results.append(await self.test_endpoint("GET", f"/api/v1/public/menu/{TEST_RESTAURANT_CODE}"))
        
        # Test public menu categories
        results.append(await self.test_endpoint("GET", f"/api/v1/public/menu/{TEST_RESTAURANT_CODE}/categories"))
        
        return results
    
    async def run_all_tests(self):
        """Run all endpoint tests"""
        print("🚀 Starting Comprehensive Restaurant API Testing")
        print("=" * 60)
        
        # Test health check first
        await self.test_health_check()
        
        # Test restaurant endpoints
        await self.test_restaurant_by_code()
        await self.test_restaurant_registration()
        
        # Test menu endpoints
        await self.test_menu_endpoints()
        
        # Test table endpoints
        await self.test_table_endpoints()
        
        # Test QR endpoints
        await self.test_qr_endpoints()
        
        # Test public menu endpoints
        await self.test_public_menu_endpoints()
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - successful_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(successful_tests/total_tests)*100:.1f}%")
        
        # Performance analysis
        response_times = [result["response_time_ms"] for result in self.test_results if result["success"]]
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            print(f"Average Response Time: {avg_response_time:.2f}ms")
            print(f"Max Response Time: {max_response_time:.2f}ms")
        
        # Failed tests details
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['method']} {result['endpoint']}: {result['error']}")
        
        # Save detailed results
        with open("restaurant_api_test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: restaurant_api_test_results.json")

async def main():
    """Main test function"""
    async with RestaurantAPITester() as tester:
        await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
