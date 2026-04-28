"""Cart and Orders API Execution Testing.

This module executes actual HTTP requests to test all cart and orders API endpoints
and provides comprehensive execution results with curl commands, request/response data,
status codes, and explanations.
"""

import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any

import requests


class CartOrdersAPIExecutionTester:
    """Execute comprehensive testing of cart and orders API endpoints."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.execution_results = {}

    def execute_request(self, method: str, endpoint: str, data: Dict = None, headers: Dict = None) -> Dict[str, Any]:
        """Execute HTTP request and return comprehensive results."""
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
                return {"error": f"Unsupported HTTP method: {method}"}

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
                "request_data": data,
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
                "request_data": data,
            }

    def test_cart_session_management(self) -> Dict[str, Any]:
        """Test cart session management endpoints."""
        print("\n🛒 Testing Cart Session Management Endpoints...")

        results = {}

        # 1. Create Anonymous Cart Session
        print("   1. Creating anonymous cart session...")
        session_data = {
            "anonymous_session_id": str(uuid.uuid4()),
            "restaurant_id": "550e8400-e29b-41d4-a716-446655440001",
        }

        result = self.execute_request("POST", "/api/v1/cart/sessions/anonymous", data=session_data)
        results["anonymous_session_creation"] = result

        print(f"      Status: {result['status_code']}")
        print(f"      Response Time: {result['response_time_ms']:.2f}ms")
        if result["success"] and result["status_code"] == 201:
            session_info = result["response_data"]
            session_token = session_info.get("session_token")
            print(f"      Session Token: {session_token[:20]}...")
            print("      ✅ Anonymous cart session created successfully")
        else:
            print(f"      ❌ Failed to create session: {result.get('error', 'Unknown error')}")

        # 2. Get Cart Session
        if result["success"] and result["status_code"] == 201:
            session_token = result["response_data"].get("session_token")

            print("   2. Retrieving cart session...")
            result2 = self.execute_request("GET", f"/api/v1/cart/sessions/{session_token}")
            results["session_retrieval"] = result2

            print(f"      Status: {result2['status_code']}")
            print(f"      Response Time: {result2['response_time_ms']:.2f}ms")
            if result2["success"] and result2["status_code"] == 200:
                print("      ✅ Cart session retrieved successfully"
            else:
                print(f"      ❌ Failed to retrieve session: {result2.get('error', 'Unknown error')}")

        return results

    def test_order_operations(self) -> Dict[str, Any]:
        """Test order management endpoints."""
        print("\n📋 Testing Order Management Endpoints...")

        results = {}

        # 1. Create Order (test with fake cart session)
        print("   1. Creating order from cart...")
        order_data = {
            "cart_session_id": "550e8400-e29b-41d4-a716-446655440003",
            "customer_info": {
                "name": "Test Customer",
                "phone": "+919876543210",
                "email": "test@example.com"
            },
        }

        result = self.execute_request("POST", "/orders", data=order_data)
        results["order_creation"] = result

        print(f"      Status: {result['status_code']}")
        print(f"      Response Time: {result['response_time_ms']:.2f}ms")
        if result["success"]:
            if result["status_code"] == 201:
                order_info = result["response_data"]
                order_id = order_info.get("id")
                print(f"      Order ID: {order_id}")
                print("      ✅ Order created successfully"
            elif result["status_code"] in [400, 422]:
                print("      ⚠️  Order creation failed (expected - invalid cart session)"
            else:
                print(f"      ❌ Unexpected status code: {result['status_code']}")
        else:
            print(f"      ❌ Request failed: {result.get('error', 'Unknown error')}")

        # 2. Get Order by ID
        test_order_id = "550e8400-e29b-41d4-a716-446655440011"
        print("   2. Retrieving order by ID...")
        result2 = self.execute_request("GET", f"/orders/{test_order_id}")
        results["order_retrieval"] = result2

        print(f"      Status: {result2['status_code']}")
        print(f"      Response Time: {result2['response_time_ms']:.2f}ms")
        if result2["success"] and result2["status_code"] == 404:
            print("      ✅ Properly returned 404 for non-existent order"
        elif result2["success"] and result2["status_code"] == 200:
            print("      ✅ Order retrieved successfully"
        else:
            print(f"      ❌ Unexpected response: {result2.get('status_code', 'Unknown error')}")

        return results

    def test_error_scenarios(self) -> Dict[str, Any]:
        """Test error handling and edge cases."""
        print("\n🚨 Testing Error Scenarios...")

        results = {}

        # 1. Invalid Session Token
        print("   1. Testing invalid session token...")
        result = self.execute_request("GET", "/api/v1/cart/sessions/invalid-token")
        results["invalid_session"] = result

        print(f"      Status: {result['status_code']}")
        print(f"      Response Time: {result['response_time_ms']:.2f}ms")
        if result["success"] and result["status_code"] in [404, 401]:
            print("      ✅ Properly handled invalid session token"
        else:
            print(f"      ❌ Unexpected response: {result.get('status_code', 'Unknown error')}")

        # 2. Invalid Order ID
        print("   2. Testing invalid order ID...")
        result2 = self.execute_request("GET", "/orders/invalid-uuid")
        results["invalid_order_id"] = result2

        print(f"      Status: {result2['status_code']}")
        print(f"      Response Time: {result2['response_time_ms']:.2f}ms")
        if result2["success"] and result2["status_code"] == 404:
            print("      ✅ Properly handled invalid order ID"
        else:
            print(f"      ❌ Unexpected response: {result2.get('status_code', 'Unknown error')}")

        # 3. Missing Required Fields
        print("   3. Testing missing required fields...")
        result3 = self.execute_request("POST", "/api/v1/cart/sessions/anonymous", data={})
        results["missing_fields"] = result3

        print(f"      Status: {result3['status_code']}")
        print(f"      Response Time: {result3['response_time_ms']:.2f}ms")
        if result3["success"] and result3["status_code"] == 422:
            print("      ✅ Properly validated required fields"
        else:
            print(f"      ❌ Unexpected response: {result3.get('status_code', 'Unknown error')}")

        return results

    def run_comprehensive_testing(self) -> Dict[str, Any]:
        """Run comprehensive testing of all endpoints."""
        print("🚀 Starting Comprehensive Cart and Orders API Execution Testing...")
        print(f"📍 Target URL: {self.base_url}")
        print("=" * 80)

        # Execute all test categories
        self.execution_results["cart_sessions"] = self.test_cart_session_management()
        self.execution_results["orders"] = self.test_order_operations()
        self.execution_results["error_scenarios"] = self.test_error_scenarios()

        # Generate comprehensive report
        report = self.generate_execution_report()

        # Print summary
        self.print_execution_summary(report)

        return report

    def generate_execution_report(self) -> Dict[str, Any]:
        """Generate comprehensive execution report."""
        return {
            "execution_summary": {
                "timestamp": datetime.now().isoformat(),
                "base_url": self.base_url,
                "total_endpoints_tested": len(self.execution_results),
                "execution_status": "completed",
            },
            "detailed_results": self.execution_results,
            "endpoint_coverage": self._analyze_endpoint_coverage(),
            "performance_summary": self._generate_performance_summary(),
            "error_handling_assessment": self._assess_error_handling(),
            "execution_insights": self._generate_execution_insights(),
        }

    def _analyze_endpoint_coverage(self) -> Dict[str, Any]:
        """Analyze which endpoints were successfully tested."""
        total_requests = 0
        successful_requests = 0

        for category, tests in self.execution_results.items():
            if isinstance(tests, dict):
                for test_name, result in tests.items():
                    if isinstance(result, dict):
                        total_requests += 1
                        if result.get("success", False):
                            successful_requests += 1

        return {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "coverage_percentage": (successful_requests / total_requests * 100) if total_requests > 0 else 0,
        }

    def _generate_performance_summary(self) -> Dict[str, Any]:
        """Generate performance metrics summary."""
        response_times = []

        for category, tests in self.execution_results.items():
            if isinstance(tests, dict):
                for test_name, result in tests.items():
                    if isinstance(result, dict) and result.get("success", False):
                        response_times.append(result.get("response_time_ms", 0))

        if response_times:
            avg_time = sum(response_times) / len(response_times)
            return {
                "average_response_time_ms": avg_time,
                "fastest_response_ms": min(response_times),
                "slowest_response_ms": max(response_times),
                "total_requests_measured": len(response_times),
                "performance_target_met": avg_time < 500,
            }

        return {"performance_data": "not_available"}

    def _assess_error_handling(self) -> Dict[str, Any]:
        """Assess error handling quality."""
        error_scenarios = self.execution_results.get("error_scenarios", {})
        proper_errors = 0
        total_errors = len(error_scenarios)

        for test_name, result in error_scenarios.items():
            if isinstance(result, dict) and result.get("success", False):
                status_code = result.get("status_code")
                if status_code in [400, 404, 422, 401]:
                    proper_errors += 1

        return {
            "error_handling_score": (proper_errors / total_errors * 100) if total_errors > 0 else 0,
            "proper_errors": proper_errors,
            "total_error_tests": total_errors,
        }

    def _generate_execution_insights(self) -> List[str]:
        """Generate insights from test execution."""
        insights = []

        # Analyze endpoint coverage
        coverage = self._analyze_endpoint_coverage()
        if coverage["coverage_percentage"] >= 80:
            insights.append("✅ High endpoint coverage achieved")
        elif coverage["coverage_percentage"] >= 60:
            insights.append("⚠️  Moderate endpoint coverage - consider expanding test scenarios")
        else:
            insights.append("❌ Low endpoint coverage - need more comprehensive testing")

        # Analyze performance
        perf = self._generate_performance_summary()
        if perf.get("performance_target_met"):
            insights.append("⚡ Performance targets met - API responds within acceptable time limits")
        else:
            avg_time = perf.get("average_response_time_ms", 0)
            insights.append(f"⚠️  Performance concerns - average response time {avg_time:.2f}ms exceeds 500ms target")

        # Analyze error handling
        error_assessment = self._assess_error_handling()
        if error_assessment["error_handling_score"] >= 80:
            insights.append("✅ Error handling is robust and consistent")
        else:
            insights.append("⚠️  Error handling needs improvement")

        return insights

    def print_execution_summary(self, report: Dict[str, Any]):
        """Print comprehensive execution summary."""
        print("\n" + "=" * 80)
        print("🧪 COMPREHENSIVE API EXECUTION RESULTS")
        print("=" * 80)

        # Coverage summary
        coverage = report["endpoint_coverage"]
        print(f"📊 Endpoint Coverage: {coverage['successful_requests']}/{coverage['total_requests']} requests ({coverage['coverage_percentage']:.1f}%)")

        # Performance summary
        perf = report["performance_summary"]
        if isinstance(perf, dict) and "average_response_time_ms" in perf:
            avg_time = perf["average_response_time_ms"]
            target_met = perf["performance_target_met"]
            print(f"⚡ Performance: {avg_time:.2f}ms average ({'✅ TARGET MET' if target_met else '❌ TARGET NOT MET'})")

        # Error handling summary
        error_assessment = report["error_handling_assessment"]
        print(f"🚨 Error Handling: {error_assessment['error_handling_score']:.1f}% effectiveness")

        print("\n🔍 Execution Insights:")
        for insight in report["execution_insights"]:
            print(f"   {insight}")

        print("\n📋 Detailed Test Results:")

        # Cart Sessions
        cart_sessions = self.execution_results.get("cart_sessions", {})
        if cart_sessions:
            print("\n   🛒 Cart Session Management:")
            for test_name, result in cart_sessions.items():
                if isinstance(result, dict):
                    status = result.get("status_code", "ERROR")
                    time_ms = result.get("response_time_ms", 0)
                    print(f"      {test_name}: {status} ({time_ms:.2f}ms)")

        # Orders
        orders = self.execution_results.get("orders", {})
        if orders:
            print("\n   📋 Order Management:")
            for test_name, result in orders.items():
                if isinstance(result, dict):
                    status = result.get("status_code", "ERROR")
                    time_ms = result.get("response_time_ms", 0)
                    print(f"      {test_name}: {status} ({time_ms:.2f}ms)")

        # Error Scenarios
        error_scenarios = self.execution_results.get("error_scenarios", {})
        if error_scenarios:
            print("\n   🚨 Error Scenarios:")
            for test_name, result in error_scenarios.items():
                if isinstance(result, dict):
                    status = result.get("status_code", "ERROR")
                    time_ms = result.get("response_time_ms", 0)
                    print(f"      {test_name}: {status} ({time_ms:.2f}ms)")

        print("\n✅ API execution testing completed!")
        print("=" * 80)


def run_cart_orders_api_execution_testing(base_url: str = "http://localhost:8000") -> Dict[str, Any]:
    """Run comprehensive API execution testing."""
    tester = CartOrdersAPIExecutionTester(base_url)
    report = tester.run_comprehensive_testing()

    # Save detailed results
    output_file = "cart_orders_api_execution_results.json"
    try:
        with open(output_file, "w") as f:
            json.dump(report, f, indent=2, default=str)
        print(f"\n📄 Detailed execution results saved to: {output_file}")
    except Exception as e:
        print(f"\n⚠️  Failed to save results: {e}")

    return report


# Run execution testing when module is executed directly
if __name__ == "__main__":
    import sys

    base_url = "http://localhost:8000"
    if len(sys.argv) > 1:
        base_url = sys.argv[1]

    print("🔬 Cart and Orders API Execution Testing")
    print(f"🎯 Target: {base_url}")

    report = run_cart_orders_api_execution_testing(base_url)
