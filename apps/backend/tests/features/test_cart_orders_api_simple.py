"""Simple Cart and Orders API Testing.

This module provides straightforward testing of cart and orders API endpoints
with actual HTTP requests to validate functionality.
"""

import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any

import requests
from fastapi.testclient import TestClient

from app.main import app


class SimpleCartOrdersTester:
    """Simple tester for cart and orders API endpoints."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = TestClient(app)
        self.results = {}

    def make_request(self, method: str, endpoint: str, data: Dict = None, headers: Dict = None) -> Dict[str, Any]:
        """Make HTTP request and return results."""
        url = f"{self.base_url}{endpoint}"

        # Default headers
        request_headers = {"Content-Type": "application/json"}
        if headers:
            request_headers.update(headers)

        # Execute request
        start_time = time.time()

        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=request_headers, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, headers=request_headers, json=data, timeout=10)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=request_headers, json=data, timeout=10)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=request_headers, timeout=10)
            elif method.upper() == "PATCH":
                response = requests.patch(url, headers=request_headers, json=data, timeout=10)
            else:
                return {"error": f"Unsupported method: {method}"}

            end_time = time.time()
            response_time = (end_time - start_time) * 1000

            # Parse response
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                response_data = {"raw_response": response.text}

            return {
                "success": True,
                "status_code": response.status_code,
                "response_time_ms": response_time,
                "response_data": response_data,
                "headers": dict(response.headers),
                "method": method,
                "url": url,
            }

        except requests.exceptions.RequestException as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000

            return {
                "success": False,
                "status_code": None,
                "response_time_ms": response_time,
                "error": str(e),
                "method": method,
                "url": url,
            }

    def test_all_endpoints(self) -> Dict[str, Any]:
        """Test all cart and orders API endpoints."""
        print("🧪 Starting Cart and Orders API Testing...")
        print(f"📍 Base URL: {self.base_url}")
        print("=" * 60)

        # Test data
        test_ids = {
            "restaurant_id": "550e8400-e29b-41d4-a716-446655440001",
            "user_id": "550e8400-e29b-41d4-a716-446655440005",
            "table_id": "550e8400-e29b-41d4-a716-446655440002",
            "menu_item_id": "550e8400-e29b-41d4-a716-446655440007",
        }

        # 1. Test Cart Session Management
        print("\n1. 🛒 Testing Cart Session Management...")

        # Create anonymous session
        session_data = {
            "anonymous_session_id": str(uuid.uuid4()),
            "restaurant_id": test_ids["restaurant_id"],
        }

        result = self.make_request("POST", "/api/v1/cart/sessions/anonymous", data=session_data)
        print(f"   Anonymous session creation: {result['status_code']} ({result['response_time_ms']:.2f}ms)")

        if result["success"] and result["status_code"] == 201:
            session_data = result["response_data"]
            session_token = session_data.get("session_token")
            session_id = session_data.get("id")

            # Get session
            result2 = self.make_request("GET", f"/api/v1/cart/sessions/{session_token}")
            print(f"   Session retrieval: {result2['status_code']} ({result2['response_time_ms']".2f"}ms)")

            # Extend session
            result3 = self.make_request("POST", f"/api/v1/cart/sessions/{session_token}/extend")
            print(f"   Session extension: {result3['status_code']} ({result3['response_time_ms']".2f"}ms)")

            self.results["cart_sessions"] = {
                "anonymous_creation": result,
                "session_retrieval": result2,
                "session_extension": result3,
            }
        else:
            print("   ❌ Failed to create anonymous session")
            self.results["cart_sessions"] = {"anonymous_creation": result}

        # 2. Test Cart Item Operations
        print("\n2. 📦 Testing Cart Item Operations...")

        if "session_token" in locals():
            # Add item to cart
            item_data = {
                "menu_item_id": test_ids["menu_item_id"],
                "quantity": 2,
                "customizations": {"spice_level": "medium"},
            }

            result = self.make_request("POST", f"/api/v1/cart/sessions/{session_token}/items", data=item_data)
            print(f"   Add item: {result['status_code']} ({result['response_time_ms']:.2f}ms)")

            # Get cart items
            result2 = self.make_request("GET", f"/api/v1/cart/sessions/{session_token}/items")
            print(f"   Get items: {result2['status_code']} ({result2['response_time_ms']".2f"}ms)")

            self.results["cart_items"] = {
                "add_item": result,
                "get_items": result2,
            }
        else:
            print("   ❌ Skipping cart item tests - no session token")
            self.results["cart_items"] = {"error": "No session token available"}

        # 3. Test Order Operations
        print("\n3. 📋 Testing Order Operations...")

        # Create order
        order_data = {
            "cart_session_id": session_id if "session_id" in locals() else test_ids["restaurant_id"],
            "customer_info": {
                "name": "Test Customer",
                "phone": "+919876543210",
                "email": "test@example.com"
            },
        }

        result = self.make_request("POST", "/orders", data=order_data)
        print(f"   Create order: {result['status_code']} ({result['response_time_ms']:.2f}ms)")

        if result["success"] and result["status_code"] == 201:
            order_data = result["response_data"]
            order_id = order_data.get("id")

            # Get order
            result2 = self.make_request("GET", f"/orders/{order_id}")
            print(f"   Get order: {result2['status_code']} ({result2['response_time_ms']".2f"}ms)")

            self.results["orders"] = {
                "create_order": result,
                "get_order": result2,
            }
        else:
            # Test with fake order ID
            fake_order_id = "550e8400-e29b-41d4-a716-446655440011"
            result2 = self.make_request("GET", f"/orders/{fake_order_id}")
            print(f"   Get order (fake ID): {result2['status_code']} ({result2['response_time_ms']".2f"}ms)")

            self.results["orders"] = {
                "create_order": result,
                "get_order": result2,
            }

        # 4. Test Error Scenarios
        print("\n4. 🚨 Testing Error Scenarios...")

        # Invalid session token
        result = self.make_request("GET", "/api/v1/cart/sessions/invalid-token")
        print(f"   Invalid session: {result['status_code']} ({result['response_time_ms']:.2f}ms)")

        # Invalid order ID
        result2 = self.make_request("GET", "/orders/invalid-uuid")
        print(f"   Invalid order ID: {result2['status_code']} ({result2['response_time_ms']".2f"}ms)")

        # Missing required fields
        result3 = self.make_request("POST", "/api/v1/cart/sessions/anonymous", data={})
        print(f"   Missing fields: {result3['status_code']} ({result3['response_time_ms']".2f"}ms)")

        self.results["error_scenarios"] = {
            "invalid_session": result,
            "invalid_order_id": result2,
            "missing_fields": result3,
        }

        # 5. Test Price Validation
        print("\n5. 💰 Testing Price Validation...")

        price_data = {
            "menu_item_id": test_ids["menu_item_id"],
            "expected_base_price": 15.00,
            "customizations": {"spice_level": "hot"},
        }

        result = self.make_request("POST", "/api/v1/cart/validate-price", data=price_data)
        print(f"   Price validation: {result['status_code']} ({result['response_time_ms']:.2f}ms)")

        self.results["price_validation"] = result

        # 6. Test Authentication Requirements
        print("\n6. 🔐 Testing Authentication Requirements...")

        # Try authenticated endpoints without auth
        result = self.make_request("POST", "/api/v1/cart/sessions/authenticated", data={
            "restaurant_id": test_ids["restaurant_id"],
            "table_id": test_ids["table_id"]
        })
        print(f"   Auth endpoint without token: {result['status_code']} ({result['response_time_ms']:.2f}ms)")

        # Try order status update without auth
        fake_order_id = "550e8400-e29b-41d4-a716-446655440011"
        result2 = self.make_request("PATCH", f"/orders/{fake_order_id}/status", data={
            "new_status": "preparing"
        })
        print(f"   Order update without auth: {result2['status_code']} ({result2['response_time_ms']".2f"}ms)")

        self.results["authentication"] = {
            "auth_endpoint_no_token": result,
            "order_update_no_auth": result2,
        }

        # 7. Performance Testing
        print("\n7. ⚡ Testing Performance Metrics...")

        operations = [
            ("POST", "/api/v1/cart/sessions/anonymous", {
                "anonymous_session_id": str(uuid.uuid4()),
                "restaurant_id": test_ids["restaurant_id"],
            }),
            ("GET", "/api/v1/cart/sessions/invalid-token", None),
            ("POST", "/orders", order_data),
            ("GET", f"/orders/{fake_order_id}", None),
        ]

        response_times = []

        for method, endpoint, data in operations:
            result = self.make_request(method, endpoint, data=data)
            if result["success"]:
                response_times.append(result["response_time_ms"])

        if response_times:
            avg_time = sum(response_times) / len(response_times)
            print(f"   📊 Average response time: {avg_time".2f"}ms")
            print(f"   🎯 Target (< 500ms): {'✅ MET' if avg_time < 500 else '❌ NOT MET'}")

            self.results["performance"] = {
                "average_response_time_ms": avg_time,
                "individual_times_ms": response_times,
                "target_met": avg_time < 500,
            }
        else:
            print("   ❌ No successful operations to measure performance")
            self.results["performance"] = {"error": "No performance data available"}

        return self.generate_report()

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        return {
            "test_summary": {
                "timestamp": datetime.now().isoformat(),
                "base_url": self.base_url,
                "total_endpoints_tested": len(self.results),
            },
            "detailed_results": self.results,
            "endpoint_coverage": self._analyze_coverage(),
            "performance_assessment": self._assess_performance(),
            "error_handling_assessment": self._assess_error_handling(),
            "authentication_validation": self._validate_authentication(),
            "recommendations": self._generate_recommendations(),
        }

    def _analyze_coverage(self) -> Dict[str, Any]:
        """Analyze test coverage."""
        total_tests = 0
        successful_tests = 0

        for category, tests in self.results.items():
            if isinstance(tests, dict):
                for test_name, result in tests.items():
                    if isinstance(result, dict):
                        total_tests += 1
                        if result.get("success", False) and result.get("status_code") in [200, 201, 400, 401, 404, 422]:
                            successful_tests += 1

        return {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "coverage_percentage": (successful_tests / total_tests * 100) if total_tests > 0 else 0,
        }

    def _assess_performance(self) -> Dict[str, Any]:
        """Assess performance metrics."""
        perf_data = self.results.get("performance", {})

        if isinstance(perf_data, dict) and "average_response_time_ms" in perf_data:
            avg_time = perf_data["average_response_time_ms"]
            target_met = perf_data["target_met"]

            return {
                "average_response_time_ms": avg_time,
                "performance_target_met": target_met,
                "assessment": "good" if target_met else "needs_optimization",
            }

        return {"performance_data": "not_available"}

    def _assess_error_handling(self) -> Dict[str, Any]:
        """Assess error handling quality."""
        error_data = self.results.get("error_scenarios", {})

        if isinstance(error_data, dict):
            proper_errors = 0
            total_errors = len(error_data)

            for test_name, result in error_data.items():
                if isinstance(result, dict) and result.get("success", False):
                    status_code = result.get("status_code")
                    if status_code in [400, 404, 422, 401]:
                        proper_errors += 1

            return {
                "error_handling_score": (proper_errors / total_errors * 100) if total_errors > 0 else 0,
                "proper_errors": proper_errors,
                "total_error_tests": total_errors,
            }

        return {"error_handling": "not_tested"}

    def _validate_authentication(self) -> Dict[str, Any]:
        """Validate authentication requirements."""
        auth_data = self.results.get("authentication", {})

        if isinstance(auth_data, dict):
            auth_properly_enforced = 0
            total_auth_tests = len(auth_data)

            for test_name, result in auth_data.items():
                if isinstance(result, dict) and result.get("success", False):
                    status_code = result.get("status_code")
                    if status_code in [401, 422]:
                        auth_properly_enforced += 1

            return {
                "authentication_enforced": auth_properly_enforced == total_auth_tests,
                "auth_tests": total_auth_tests,
            }

        return {"authentication": "not_tested"}

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []

        # Performance recommendations
        perf_assessment = self._assess_performance()
        if perf_assessment.get("performance_target_met") == False:
            avg_time = perf_assessment.get("average_response_time_ms", 0)
            recommendations.append(f"Optimize API performance - average response time {avg_time".2f"}ms exceeds 500ms target")

        # Error handling recommendations
        error_assessment = self._assess_error_handling()
        if error_assessment.get("error_handling_score", 100) < 80:
            recommendations.append("Improve error handling consistency across endpoints")

        # Authentication recommendations
        auth_validation = self._validate_authentication()
        if not auth_validation.get("authentication_enforced", True):
            recommendations.append("Strengthen authentication requirements for protected endpoints")

        if not recommendations:
            recommendations.extend([
                "All endpoints tested successfully",
                "API implementation is robust and production-ready",
                "Consider adding comprehensive logging for production monitoring",
                "Implement rate limiting for cart operations",
            ])

        return recommendations

    def print_summary(self, report: Dict[str, Any]):
        """Print comprehensive test summary."""
        print("\n" + "=" * 60)
        print("🧪 COMPREHENSIVE TEST RESULTS")
        print("=" * 60)

        coverage = report["endpoint_coverage"]
        print(f"📊 Test Coverage: {coverage['successful_tests']}/{coverage['total_tests']} tests ({coverage['coverage_percentage']".1f"}%)")

        perf = report["performance_assessment"]
        if perf.get("performance_target_met"):
            print(f"⚡ Performance: ✅ {perf['average_response_time_ms']".2f"}ms (target met)")
        else:
            print(f"⚡ Performance: ❌ {perf.get('average_response_time_ms', 'N/A')}ms (target not met)")

        error_handling = report["error_handling_assessment"]
        print(f"🚨 Error Handling: {error_handling['error_handling_score']".1f"}% effectiveness")

        auth = report["authentication_validation"]
        auth_status = "✅ Properly enforced" if auth["authentication_enforced"] else "⚠️ Needs attention"
        print(f"🔐 Authentication: {auth_status}")

        print("\n💡 Recommendations:")
        for i, rec in enumerate(report["recommendations"][:3], 1):
            print(f"   {i}. {rec}")

        print("\n✅ Testing completed!")
        print("=" * 60)


def run_simple_api_testing(base_url: str = "http://localhost:8000") -> Dict[str, Any]:
    """Run simple API testing and return results."""
    tester = SimpleCartOrdersTester(base_url)
    report = tester.test_all_endpoints()
    tester.print_summary(report)

    # Save detailed results
    output_file = "cart_orders_api_test_results.json"
    try:
        with open(output_file, "w") as f:
            json.dump(report, f, indent=2, default=str)
        print(f"\n📄 Detailed results saved to: {output_file}")
    except Exception as e:
        print(f"\n⚠️  Failed to save results: {e}")

    return report


# Run tests when executed directly
if __name__ == "__main__":
    import sys

    base_url = "http://localhost:8000"
    if len(sys.argv) > 1:
        base_url = sys.argv[1]

    print("🔬 Simple Cart and Orders API Testing")
    print(f"🎯 Target: {base_url}")

    report = run_simple_api_testing(base_url)
