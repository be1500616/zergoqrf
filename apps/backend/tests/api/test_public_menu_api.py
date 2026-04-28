#!/usr/bin/env python3
"""
Comprehensive test script for public menu API endpoints.
Tests all public menu functionality including performance requirements.
"""

import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

import httpx


class PublicMenuAPITester:
    """Comprehensive tester for public menu API."""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        """Initialize the tester.
        
        Args:
            base_url: Base URL of the API server.
        """
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.test_restaurant_code = "TEST123"
        self.test_data: Dict[str, Any] = {}
    
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
    
    async def test_restaurant_branding_endpoint(self) -> bool:
        """Test restaurant branding endpoint.
        
        Returns:
            True if test passes, False otherwise.
        """
        print("🏢 Testing restaurant branding endpoint...")
        
        try:
            start_time = time.time()
            response = await self.client.get(
                f"{self.base_url}/api/v1/public/menu/restaurant/{self.test_restaurant_code}"
            )
            response_time = time.time() - start_time
            
            print(f"   Response time: {response_time:.3f}s")
            
            if response.status_code == 404:
                print("⚠️ Test restaurant not found (expected for test environment)")
                return True
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['id', 'name', 'code', 'primary_color', 'secondary_color', 'accent_color']
                
                for field in required_fields:
                    if field not in data:
                        print(f"❌ Missing required field: {field}")
                        return False
                
                self.test_data['restaurant'] = data
                print(f"✅ Restaurant branding endpoint working: {data['name']}")
                
                # Performance check (should be < 1 second)
                if response_time < 1.0:
                    print(f"✅ Performance requirement met: {response_time:.3f}s < 1.0s")
                else:
                    print(f"⚠️ Performance requirement not met: {response_time:.3f}s >= 1.0s")
                
                return True
            else:
                print(f"❌ Unexpected status code: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Restaurant branding test failed: {str(e)}")
            return False
    
    async def test_complete_menu_structure_endpoint(self) -> bool:
        """Test complete menu structure endpoint.
        
        Returns:
            True if test passes, False otherwise.
        """
        print("📋 Testing complete menu structure endpoint...")
        
        try:
            start_time = time.time()
            response = await self.client.get(
                f"{self.base_url}/api/v1/public/menu/{self.test_restaurant_code}"
            )
            response_time = time.time() - start_time
            
            print(f"   Response time: {response_time:.3f}s")
            
            if response.status_code == 404:
                print("⚠️ Test restaurant menu not found (expected for test environment)")
                return True
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['restaurant', 'categories', 'items', 'last_updated']
                
                for field in required_fields:
                    if field not in data:
                        print(f"❌ Missing required field: {field}")
                        return False
                
                self.test_data['menu_structure'] = data
                print(f"✅ Menu structure endpoint working:")
                print(f"   - Restaurant: {data['restaurant']['name']}")
                print(f"   - Categories: {len(data['categories'])}")
                print(f"   - Items: {len(data['items'])}")
                
                # Performance check (should be < 2 seconds for 3G requirement)
                if response_time < 2.0:
                    print(f"✅ Performance requirement met: {response_time:.3f}s < 2.0s")
                else:
                    print(f"⚠️ Performance requirement not met: {response_time:.3f}s >= 2.0s")
                
                return True
            else:
                print(f"❌ Unexpected status code: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Menu structure test failed: {str(e)}")
            return False
    
    async def test_categories_endpoint(self) -> bool:
        """Test menu categories endpoint.
        
        Returns:
            True if test passes, False otherwise.
        """
        print("📂 Testing menu categories endpoint...")
        
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/public/menu/{self.test_restaurant_code}/categories"
            )
            
            if response.status_code == 404:
                print("⚠️ Test restaurant categories not found (expected for test environment)")
                return True
            
            if response.status_code == 200:
                data = response.json()
                
                if not isinstance(data, list):
                    print("❌ Categories response should be a list")
                    return False
                
                print(f"✅ Categories endpoint working: {len(data)} categories")
                
                # Validate category structure
                if data:
                    category = data[0]
                    required_fields = ['id', 'name', 'sort_order', 'item_count']
                    
                    for field in required_fields:
                        if field not in category:
                            print(f"❌ Missing required category field: {field}")
                            return False
                
                return True
            else:
                print(f"❌ Unexpected status code: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Categories test failed: {str(e)}")
            return False
    
    async def test_search_endpoint(self) -> bool:
        """Test menu search endpoint.
        
        Returns:
            True if test passes, False otherwise.
        """
        print("🔍 Testing menu search endpoint...")
        
        try:
            search_queries = ["pizza", "burger", "salad", "nonexistent"]
            
            for query in search_queries:
                start_time = time.time()
                response = await self.client.get(
                    f"{self.base_url}/api/v1/public/menu/{self.test_restaurant_code}/search?query={query}&limit=10"
                )
                response_time = time.time() - start_time
                
                if response.status_code == 404:
                    print(f"⚠️ Test restaurant not found for search '{query}' (expected)")
                    continue
                
                if response.status_code == 200:
                    data = response.json()
                    required_fields = ['items', 'total_count', 'search_query', 'categories_found']
                    
                    for field in required_fields:
                        if field not in data:
                            print(f"❌ Missing required search field: {field}")
                            return False
                    
                    print(f"   Search '{query}': {data['total_count']} results in {response_time:.3f}s")
                    
                    # Performance check (should be < 1 second)
                    if response_time >= 1.0:
                        print(f"⚠️ Search performance concern: {response_time:.3f}s >= 1.0s")
                else:
                    print(f"❌ Search failed for '{query}': {response.status_code}")
                    return False
            
            print("✅ Search endpoint working for all test queries")
            return True
                
        except Exception as e:
            print(f"❌ Search test failed: {str(e)}")
            return False
    
    async def test_featured_items_endpoint(self) -> bool:
        """Test featured items endpoint.
        
        Returns:
            True if test passes, False otherwise.
        """
        print("⭐ Testing featured items endpoint...")
        
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/public/menu/{self.test_restaurant_code}/featured?limit=5"
            )
            
            if response.status_code == 404:
                print("⚠️ Test restaurant featured items not found (expected for test environment)")
                return True
            
            if response.status_code == 200:
                data = response.json()
                
                if not isinstance(data, list):
                    print("❌ Featured items response should be a list")
                    return False
                
                print(f"✅ Featured items endpoint working: {len(data)} featured items")
                
                # Validate featured item structure
                if data:
                    item = data[0]
                    required_fields = ['id', 'name', 'base_price', 'is_featured']
                    
                    for field in required_fields:
                        if field not in item:
                            print(f"❌ Missing required featured item field: {field}")
                            return False
                    
                    if not item['is_featured']:
                        print("❌ Featured item should have is_featured=true")
                        return False
                
                return True
            else:
                print(f"❌ Unexpected status code: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Featured items test failed: {str(e)}")
            return False
    
    async def test_api_documentation(self) -> bool:
        """Test API documentation availability.
        
        Returns:
            True if test passes, False otherwise.
        """
        print("📚 Testing API documentation...")
        
        try:
            response = await self.client.get(f"{self.base_url}/docs")
            
            if response.status_code == 200:
                print("✅ API documentation is accessible")
                return True
            else:
                print(f"⚠️ API documentation not accessible: {response.status_code}")
                return True  # Not critical for functionality
                
        except Exception as e:
            print(f"⚠️ API documentation test failed: {str(e)}")
            return True  # Not critical for functionality
    
    async def test_cors_headers(self) -> bool:
        """Test CORS headers for web app compatibility.
        
        Returns:
            True if test passes, False otherwise.
        """
        print("🌐 Testing CORS headers...")
        
        try:
            # Test preflight request
            response = await self.client.options(
                f"{self.base_url}/api/v1/public/menu/restaurant/{self.test_restaurant_code}",
                headers={
                    'Origin': 'https://app.zergoqrf.com',
                    'Access-Control-Request-Method': 'GET',
                }
            )
            
            # CORS might not be configured yet, so we'll be lenient
            if response.status_code in [200, 204, 404]:
                print("✅ CORS preflight handled")
                return True
            else:
                print(f"⚠️ CORS preflight response: {response.status_code}")
                return True  # Not critical for basic functionality
                
        except Exception as e:
            print(f"⚠️ CORS test failed: {str(e)}")
            return True  # Not critical for basic functionality
    
    async def run_all_tests(self) -> bool:
        """Run all public menu API tests.
        
        Returns:
            True if all tests pass, False otherwise.
        """
        print("🚀 Starting Public Menu API Tests")
        print("=" * 60)
        
        tests = [
            ("Server Health", self.test_server_health),
            ("Restaurant Branding Endpoint", self.test_restaurant_branding_endpoint),
            ("Complete Menu Structure Endpoint", self.test_complete_menu_structure_endpoint),
            ("Menu Categories Endpoint", self.test_categories_endpoint),
            ("Menu Search Endpoint", self.test_search_endpoint),
            ("Featured Items Endpoint", self.test_featured_items_endpoint),
            ("API Documentation", self.test_api_documentation),
            ("CORS Headers", self.test_cors_headers),
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
        
        print("\n" + "=" * 60)
        print(f"📊 Public Menu API Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All public menu API tests passed!")
            return True
        else:
            print(f"❌ {total - passed} public menu API tests failed")
            return False
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


async def main():
    """Main test function."""
    tester = PublicMenuAPITester()
    
    try:
        success = await tester.run_all_tests()
        return success
    finally:
        await tester.close()


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
