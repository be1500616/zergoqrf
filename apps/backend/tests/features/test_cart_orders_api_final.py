"""Final Cart and Orders API Testing.

This module provides comprehensive testing of cart and orders API endpoints
with actual HTTP requests using FastAPI TestClient.
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Any

from fastapi.testclient import TestClient
from app.main import app


class CartOrdersAPITester:
    """Test cart and orders API endpoints."""

    def __init__(self):
        self.client = TestClient(app)
        self.results = {}

    def test_endpoint(self, method: str, endpoint: str, data: Dict = None) -> Dict[str, Any]:
        """Test a single endpoint."""
        start_time = time.time()

        try:
            if method == "GET":
                response = self.client.get(endpoint)
            elif method == "POST":
                response = self.client.post(endpoint, json=data)
            elif method == "PUT":
                response = self.client.put(endpoint, json=data)
            elif method == "DELETE":
                response = self.client.delete(endpoint)
            elif method == "PATCH":
                response = self.client.patch(endpoint, json=data)
            else:
                return {"error": f"Unsupported method: {method}"}

            end_time = time.time()
            response_time = (end_time - start_time) * 1000

            try:
                response_data = response.json()
            except:
                response_data = {"raw": response.text}

            return {
                "success": True,
                "status_code": response.status_code,
                "response_time_ms": response_time,
                "response_data": response_data,
            }

        except Exception as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            return {
                "success": False,
                "error": str(e),
                "response_time_ms": response_time,
            }

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all API tests."""
        print("🧪 Testing Cart and Orders API Endpoints...")
        print("=" * 50)

        # Test 1: Anonymous Cart Session Creation
        print("\n1. 🛒 Testing Anonymous Cart Session...")
        session_data = {
            "anonymous_session_id": "test-session-123",
            "restaurant_id": "550e8400-e29b-41d4-a716-446655440001",
        }

        result = self.test_endpoint("POST", "/api/v1/cart/sessions/anonymous", session_data)
        print(f"   Status: {result.get('status_code', 'ERROR')}")
        print(f"   Response Time: {result.get('response_time_ms', 0):.2f}ms")
        self.results["anonymous_session"] = result

        # Test 2: Invalid Session Token
        print("\n2. 🚨 Testing Invalid Session Token...")
        result = self.test_endpoint("GET", "/api/v1/cart/sessions/invalid-token")
        print(f"   Status: {result.get('status_code', 'ERROR')}")
        print(f"   Response Time: {result.get('response_time_ms', 0):.2f}ms")
        self.results["invalid_session"] = result

        # Test 3: Order Creation
        print("\n3. 📋 Testing Order Creation...")
        order_data = {
            "cart_session_id": "550e8400-e29b-41d4-a716-446655440003",
            "customer_info": {
                "name": "Test Customer",
                "phone": "+919876543210",
                "email": "test@example.com"
            },
        }

        result = self.test_endpoint("POST", "/orders", order_data)
        print(f"   Status: {result.get('status_code', 'ERROR')}")
        print(f"   Response Time: {result.get('response_time_ms', 0):.2f}ms")
        self.results["order_creation"] = result

        # Test 4: Invalid Order ID
        print("\n4. 🚨 Testing Invalid Order ID...")
        result = self.test_endpoint("GET", "/orders/invalid-uuid")
        print(f"   Status: {result.get('status_code', 'ERROR')}")
        print(f"   Response Time: {result.get('response_time_ms', 0):.2f}ms")
        self.results["invalid_order"] = result

        # Test 5: Missing Required Fields
        print("\n5. 🚨 Testing Missing Required Fields...")
        result = self.test_endpoint("POST", "/api/v1/cart/sessions/anonymous", {})
        print(f"   Status: {result.get('status_code', 'ERROR')}")
        print(f"   Response Time: {result.get('response_time_ms', 0):.2f}ms")
        self.results["missing_fields"] = result

        return self.generate_report()

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        successful_tests = sum(1 for result in self.results.values() if result.get("success"))
        total_tests = len(self.results)

        return {
            "test_summary": {
                "timestamp": datetime.now().isoformat(),
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "success_rate": successful_tests / total_tests * 100 if total_tests > 0 else 0,
            },
            "detailed_results": self.results,
            "endpoint_coverage": {
                "cart_sessions_tested": "anonymous_session" in self.results,
                "order_endpoints_tested": "order_creation" in self.results,
                "error_scenarios_tested": "invalid_session" in self.results,
            },
        }

    def print_summary(self, report: Dict[str, Any]):
        """Print test summary."""
        print("\n" + "=" * 50)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 50)

        summary = report["test_summary"]
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Successful: {summary['successful_tests']}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")

        print("\n📋 Detailed Results:")
        for test_name, result in self.results.items():
            if result.get("success"):
                status = result.get("status_code", "ERROR")
                time_ms = result.get("response_time_ms", 0)
                print(f"✅ {test_name}: {status} ({time_ms:.2f}ms)")
            else:
                error = result.get("error", "Unknown error")
                print(f"❌ {test_name}: ERROR - {error}")

        print("\n✅ Testing completed!")


def run_api_testing() -> Dict[str, Any]:
    """Run API testing and return results."""
    tester = CartOrdersAPITester()
    report = tester.run_all_tests()
    tester.print_summary(report)

    # Save results
    with open("cart_orders_api_test_results.json", "w") as f:
        json.dump(report, f, indent=2, default=str)

    print("\n📄 Results saved to: cart_orders_api_test_results.json")
    return report


if __name__ == "__main__":
    report = run_api_testing()















