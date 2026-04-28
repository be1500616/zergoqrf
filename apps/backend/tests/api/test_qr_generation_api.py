#!/usr/bin/env python3
"""
Comprehensive test script for QR generation API endpoints.
Tests all QR generation functionality including single generation, bulk operations, and management features.
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


class QRGenerationAPITester:
    """Comprehensive tester for QR generation API."""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        """Initialize the tester.
        
        Args:
            base_url: Base URL of the API server.
        """
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=60.0)  # Longer timeout for QR generation
        self.auth_token: Optional[str] = None
        self.restaurant_id: Optional[str] = None
        self.test_data: Dict[str, Any] = {}
    
    async def setup_test_environment(self):
        """Set up test environment with authentication and test data."""
        print("🔧 Setting up QR generation test environment...")
        
        # For testing, we'll use mock credentials
        # In a real scenario, you'd authenticate and get these values
        self.restaurant_id = "test-restaurant-id"
        self.auth_token = "test-auth-token"
        
        # Set up headers for authenticated requests
        self.headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        print("✅ QR generation test environment setup complete")
    
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
    
    async def test_create_test_table(self) -> bool:
        """Create a test table for QR generation testing.
        
        Returns:
            True if test table creation succeeds, False otherwise.
        """
        print("🪑 Creating test table for QR generation...")
        
        table_data = {
            "table_number": "QR-TEST-001",
            "capacity": 4,
            "shape": "round",
            "category": "regular",
            "position": {"x": 100, "y": 100},
            "dimensions": {"width": 80, "height": 80},
            "notes": "Test table for QR generation"
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
                self.test_data["table_number"] = table["table_number"]
                print(f"✅ Test table created: {table['table_number']} (ID: {table['id']})")
                return True
            else:
                print(f"❌ Test table creation failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Test table creation failed: {str(e)}")
            return False
    
    async def test_generate_single_qr_code(self) -> bool:
        """Test single QR code generation.
        
        Returns:
            True if test passes, False otherwise.
        """
        print("🔲 Testing single QR code generation...")
        
        if not self.test_data.get("table_id"):
            print("❌ No test table available for QR generation")
            return False
        
        qr_request = {
            "table_id": self.test_data["table_id"],
            "config": {
                "format": "png",
                "size": "medium",
                "error_correction": "medium",
                "border": 4,
                "include_logo": False,
                "background_color": "white",
                "foreground_color": "black"
            }
        }
        
        try:
            start_time = time.time()
            response = await self.client.post(
                f"{self.base_url}/api/v1/qr/generate",
                json=qr_request,
                headers=self.headers
            )
            generation_time = time.time() - start_time
            
            if response.status_code == 201:
                qr_data = response.json()
                self.test_data["qr_data"] = qr_data
                
                print(f"✅ QR code generated successfully:")
                print(f"   - Table: {qr_data['table_number']}")
                print(f"   - URL: {qr_data['url']}")
                print(f"   - File size: {qr_data['file_size']} bytes")
                print(f"   - Generation time: {generation_time:.2f}s")
                
                # Check performance requirement (< 2 seconds)
                if generation_time < 2.0:
                    print(f"✅ Performance requirement met: {generation_time:.2f}s < 2.0s")
                else:
                    print(f"⚠️ Performance requirement not met: {generation_time:.2f}s >= 2.0s")
                
                return True
            else:
                print(f"❌ QR code generation failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ QR code generation failed: {str(e)}")
            return False
    
    async def test_qr_code_preview(self) -> bool:
        """Test QR code preview generation.
        
        Returns:
            True if test passes, False otherwise.
        """
        print("👁️ Testing QR code preview...")
        
        if not self.test_data.get("table_id"):
            print("❌ No test table available for QR preview")
            return False
        
        preview_request = {
            "table_id": self.test_data["table_id"],
            "config": {
                "format": "png",
                "size": "small",
                "error_correction": "medium"
            }
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/qr/preview",
                json=preview_request,
                headers=self.headers
            )
            
            if response.status_code == 200:
                preview_data = response.json()
                print(f"✅ QR code preview generated:")
                print(f"   - Table: {preview_data['table_number']}")
                print(f"   - URL: {preview_data['url']}")
                print(f"   - Preview available: {'preview_data_url' in preview_data}")
                return True
            else:
                print(f"❌ QR code preview failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ QR code preview failed: {str(e)}")
            return False
    
    async def test_bulk_qr_generation(self) -> bool:
        """Test bulk QR code generation.
        
        Returns:
            True if test passes, False otherwise.
        """
        print("📦 Testing bulk QR code generation...")
        
        # First, get all tables for the restaurant
        try:
            tables_response = await self.client.get(
                f"{self.base_url}/api/v1/tables/",
                headers=self.headers
            )
            
            if tables_response.status_code != 200:
                print(f"❌ Failed to get tables: {tables_response.status_code}")
                return False
            
            tables = tables_response.json()
            if not tables:
                print("❌ No tables available for bulk QR generation")
                return False
            
            # Take first 3 tables for bulk generation test
            table_ids = [table["id"] for table in tables[:3]]
            
            bulk_request = {
                "table_ids": table_ids,
                "config": {
                    "format": "png",
                    "size": "medium",
                    "error_correction": "medium",
                    "include_logo": False
                },
                "include_zip": True
            }
            
            start_time = time.time()
            response = await self.client.post(
                f"{self.base_url}/api/v1/qr/generate/bulk",
                json=bulk_request,
                headers=self.headers
            )
            generation_time = time.time() - start_time
            
            if response.status_code == 201:
                bulk_data = response.json()
                
                print(f"✅ Bulk QR generation completed:")
                print(f"   - Requested: {bulk_data['total_requested']}")
                print(f"   - Generated: {bulk_data['total_generated']}")
                print(f"   - Success rate: {bulk_data['success_rate']:.1f}%")
                print(f"   - Generation time: {generation_time:.2f}s")
                print(f"   - ZIP available: {'zip_download_url' in bulk_data and bulk_data['zip_download_url'] is not None}")
                
                # Check performance requirement (< 30 seconds for bulk)
                if generation_time < 30.0:
                    print(f"✅ Bulk performance requirement met: {generation_time:.2f}s < 30.0s")
                else:
                    print(f"⚠️ Bulk performance requirement not met: {generation_time:.2f}s >= 30.0s")
                
                return True
            else:
                print(f"❌ Bulk QR generation failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Bulk QR generation failed: {str(e)}")
            return False
    
    async def test_qr_management_data(self) -> bool:
        """Test QR management dashboard data retrieval.
        
        Returns:
            True if test passes, False otherwise.
        """
        print("📊 Testing QR management data retrieval...")
        
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/qr/management",
                headers=self.headers
            )
            
            if response.status_code == 200:
                management_data = response.json()
                
                print(f"✅ QR management data retrieved:")
                print(f"   - Restaurant: {management_data['restaurant_name']}")
                print(f"   - Total tables: {management_data['stats']['total_tables']}")
                print(f"   - Tables with QR: {management_data['stats']['tables_with_qr']}")
                print(f"   - QR coverage: {management_data['stats']['qr_coverage_percentage']:.1f}%")
                print(f"   - Tables in grid: {len(management_data['tables'])}")
                
                return True
            else:
                print(f"❌ QR management data retrieval failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ QR management data retrieval failed: {str(e)}")
            return False
    
    async def test_different_qr_formats(self) -> bool:
        """Test QR code generation in different formats.
        
        Returns:
            True if test passes, False otherwise.
        """
        print("🎨 Testing different QR code formats...")
        
        if not self.test_data.get("table_id"):
            print("❌ No test table available for format testing")
            return False
        
        formats = ["png", "svg", "pdf"]
        successful_formats = []
        
        for format_type in formats:
            try:
                qr_request = {
                    "table_id": self.test_data["table_id"],
                    "config": {
                        "format": format_type,
                        "size": "medium",
                        "error_correction": "medium"
                    }
                }
                
                response = await self.client.post(
                    f"{self.base_url}/api/v1/qr/generate",
                    json=qr_request,
                    headers=self.headers
                )
                
                if response.status_code == 201:
                    qr_data = response.json()
                    successful_formats.append(format_type)
                    print(f"   ✅ {format_type.upper()}: {qr_data['file_size']} bytes")
                else:
                    print(f"   ❌ {format_type.upper()}: Failed ({response.status_code})")
                    
            except Exception as e:
                print(f"   ❌ {format_type.upper()}: Exception - {str(e)}")
        
        success = len(successful_formats) == len(formats)
        if success:
            print(f"✅ All formats generated successfully: {', '.join(successful_formats)}")
        else:
            print(f"⚠️ Some formats failed. Successful: {', '.join(successful_formats)}")
        
        return success
    
    async def cleanup_test_data(self):
        """Clean up test data created during testing."""
        print("🧹 Cleaning up QR generation test data...")
        
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
    
    async def run_all_tests(self) -> bool:
        """Run all QR generation API tests.
        
        Returns:
            True if all tests pass, False otherwise.
        """
        print("🚀 Starting QR Generation API Tests")
        print("=" * 60)
        
        tests = [
            ("Server Health", self.test_server_health),
            ("Create Test Table", self.test_create_test_table),
            ("Generate Single QR Code", self.test_generate_single_qr_code),
            ("QR Code Preview", self.test_qr_code_preview),
            ("Different QR Formats", self.test_different_qr_formats),
            ("Bulk QR Generation", self.test_bulk_qr_generation),
            ("QR Management Data", self.test_qr_management_data),
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
        
        print("\n" + "=" * 60)
        print(f"📊 QR Generation Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All QR generation tests passed!")
            return True
        else:
            print(f"❌ {total - passed} QR generation tests failed")
            return False
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


async def main():
    """Main test function."""
    tester = QRGenerationAPITester()
    
    try:
        await tester.setup_test_environment()
        success = await tester.run_all_tests()
        return success
    finally:
        await tester.close()


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
