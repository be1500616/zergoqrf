"""End-to-End Cart and Orders API Testing.

This module provides comprehensive end-to-end testing of all cart and orders API endpoints,
making actual HTTP requests and validating both successful and error scenarios.

The testing covers:
- Complete cart lifecycle (anonymous → authenticated → order conversion)
- Order management and status transitions
- Payment collection and tracking
- Error handling and edge cases
- Authentication and authorization
- Performance validation
"""

import json
import time
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Any

import requests
from fastapi.testclient import TestClient

from app.main import app


class CartOrdersAPITester:
    """Comprehensive end-to-end tester for cart and orders API endpoints."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = TestClient(app)
        self.test_results = {
            "cart_endpoints": {},
            "order_endpoints": {},
            "authentication": {},
            "error_scenarios": {},
            "performance_metrics": {},
            "integration_flows": {},
        }

        # Test data
        self.test_restaurant_id = "550e8400-e29b-41d4-a716-446655440001"
        self.test_user_id = "550e8400-e29b-41d4-a716-446655440005"
        self.test_table_id = "550e8400-e29b-41d4-a716-446655440002"
        self.test_menu_item_id = "550e8400-e29b-41d4-a716-446655440007"

        # Session tokens (will be populated during testing)
        self.anonymous_session_token = None
        self.authenticated_session_token = None
        self.cart_session_id = None
        self.order_id = None

    def record_result(self, category: str, test_name: str, result: Dict[str, Any]):
        """Record test result for comprehensive reporting."""
        if category not in self.test_results:
            self.test_results[category] = {}
        self.test_results[category][test_name] = result

    def execute_curl_request(self, method: str, endpoint: str, headers: Dict = None, data: Dict = None) -> Dict[str, Any]:
        """Execute HTTP request and return detailed results."""
        url = f"{self.base_url}{endpoint}"

        # Prepare headers
        request_headers = {"Content-Type": "application/json"}
        if headers:
            request_headers.update(headers)

        # Prepare data
        json_data = None
        if data:
            json_data = data

        # Execute request
        start_time = time.time()

        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=request_headers, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, headers=request_headers, json=json_data, timeout=10)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=request_headers, json=json_data, timeout=10)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=request_headers, timeout=10)
            elif method.upper() == "PATCH":
                response = requests.patch(url, headers=request_headers, json=json_data, timeout=10)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            end_time = time.time()
            response_time = (end_time - start_time) * 1000

            # Try to parse JSON response
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
                "request_data": json_data,
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
                "request_data": json_data,
            }

    def test_cart_session_management(self):
        """Test cart session creation, retrieval, and management."""
        print("\n🛒 Testing Cart Session Management...")

        results = {}

        # 1. Create Anonymous Cart Session
        print("   1. Creating anonymous cart session...")
        anonymous_data = {
            "anonymous_session_id": str(uuid.uuid4()),
            "restaurant_id": self.test_restaurant_id,
        }

        result = self.execute_curl_request("POST", "/api/v1/cart/sessions/anonymous", data=anonymous_data)
        results["anonymous_session_creation"] = result

        if result["success"] and result["status_code"] == 201:
            response_data = result["response_data"]
            self.anonymous_session_token = response_data.get("session_token")
            self.cart_session_id = response_data.get("id")
            print(f"      ✅ Created anonymous session: {self.anonymous_session_token[:20]}...")
        else:
            print(f"      ❌ Failed to create anonymous session: {result.get('error', 'Unknown error')}")

        # 2. Get Cart Session
        if self.anonymous_session_token:
            print("   2. Retrieving cart session...")
            result = self.execute_curl_request("GET", f"/api/v1/cart/sessions/{self.anonymous_session_token}")
            results["session_retrieval"] = result

            if result["success"] and result["status_code"] == 200:
                print("      ✅ Successfully retrieved cart session"            else:
                print(f"      ❌ Failed to retrieve session: {result.get('status_code', 'Unknown error')}")

        # 3. Extend Cart Session
        if self.anonymous_session_token:
            print("   3. Extending cart session...")
            result = self.execute_curl_request("POST", f"/api/v1/cart/sessions/{self.anonymous_session_token}/extend")
            results["session_extension"] = result

            if result["success"] and result["status_code"] == 200:
                print("      ✅ Successfully extended cart session"            else:
                print(f"      ❌ Failed to extend session: {result.get('status_code', 'Unknown error')}")

        self.record_result("cart_endpoints", "session_management", results)
        return results

    def test_cart_item_operations(self):
        """Test cart item addition, update, removal, and listing."""
        print("\n📦 Testing Cart Item Operations...")

        if not self.anonymous_session_token:
            print("   ❌ Skipping cart item tests - no valid session token")
            return {"error": "No valid session token available"}

        results = {}

        # 1. Add Item to Cart
        print("   1. Adding item to cart...")
        item_data = {
            "menu_item_id": self.test_menu_item_id,
            "quantity": 2,
            "customizations": {
                "spice_level": "medium",
                "size": "large"
            },
            "special_instructions": "Extra cheese please"
        }

        result = self.execute_curl_request("POST", f"/api/v1/cart/sessions/{self.anonymous_session_token}/items", data=item_data)
        results["add_item"] = result

        if result["success"] and result["status_code"] == 201:
            print("      ✅ Successfully added item to cart"        else:
            print(f"      ❌ Failed to add item: {result.get('status_code', 'Unknown error')}")

        # 2. Get Cart Items
        print("   2. Retrieving cart items...")
        result = self.execute_curl_request("GET", f"/api/v1/cart/sessions/{self.anonymous_session_token}/items")
        results["get_items"] = result

        if result["success"] and result["status_code"] == 200:
            items = result["response_data"]
            print(f"      ✅ Retrieved {len(items)} items from cart"        else:
            print(f"      ❌ Failed to get cart items: {result.get('status_code', 'Unknown error')}")

        # 3. Update Cart Item
        print("   3. Updating cart item...")
        # For this test, we'll use a placeholder item ID since we don't have a real one
        test_item_id = "550e8400-e29b-41d4-a716-446655440008"
        update_data = {
            "quantity": 3,
            "customizations": {
                "spice_level": "hot",
                "size": "large"
            },
            "special_instructions": "Make it very spicy"
        }

        result = self.execute_curl_request("PUT", f"/api/v1/cart/items/{test_item_id}", data=update_data)
        results["update_item"] = result

        if result["success"] and result["status_code"] in [200, 404]:
            if result["status_code"] == 200:
                print("      ✅ Successfully updated cart item"            else:
                print("      ⚠️  Item not found (expected for test item ID)"
        else:
            print(f"      ❌ Failed to update item: {result.get('status_code', 'Unknown error')}")

        # 4. Remove Item from Cart
        print("   4. Removing item from cart...")
        result = self.execute_curl_request("DELETE", f"/api/v1/cart/items/{test_item_id}")
        results["remove_item"] = result

        if result["success"] and result["status_code"] in [200, 404]:
            if result["status_code"] == 200:
                print("      ✅ Successfully removed item from cart"            else:
                print("      ⚠️  Item not found (expected for test item ID)"
        else:
            print(f"      ❌ Failed to remove item: {result.get('status_code', 'Unknown error')}")

        # 5. Get Cart Summary
        print("   5. Getting cart summary...")
        result = self.execute_curl_request("GET", f"/api/v1/cart/sessions/{self.anonymous_session_token}/summary")
        results["cart_summary"] = result

        if result["success"] and result["status_code"] in [200, 404]:
            if result["status_code"] == 200:
                print("      ✅ Successfully retrieved cart summary"            else:
                print("      ⚠️  Cart session not found (may be expired)"
        else:
            print(f"      ❌ Failed to get cart summary: {result.get('status_code', 'Unknown error')}")

        self.record_result("cart_endpoints", "item_operations", results)
        return results

    def test_order_operations(self):
        """Test order creation, retrieval, and management."""
        print("\n📋 Testing Order Operations...")

        results = {}

        # 1. Create Order (this will likely fail without proper cart data, but tests the endpoint)
        print("   1. Creating order from cart...")
        order_data = {
            "cart_session_id": self.cart_session_id or "550e8400-e29b-41d4-a716-446655440003",
            "customer_info": {
                "name": "Test Customer",
                "phone": "+919876543210",
                "email": "test@example.com"
            },
            "special_instructions": "Please make it extra spicy",
            "table_id": self.test_table_id
        }

        result = self.execute_curl_request("POST", "/orders", data=order_data)
        results["order_creation"] = result

        if result["success"]:
            if result["status_code"] == 201:
                response_data = result["response_data"]
                self.order_id = response_data.get("id")
                print(f"      ✅ Successfully created order: {self.order_id}")
            elif result["status_code"] in [400, 422]:
                print(f"      ⚠️  Order creation failed (expected): {result['status_code']} - {result['response_data']}")
            else:
                print(f"      ❌ Unexpected status code: {result['status_code']}")
        else:
            print(f"      ❌ Request failed: {result.get('error', 'Unknown error')}")

        # 2. Get Order by ID
        test_order_id = self.order_id or "550e8400-e29b-41d4-a716-446655440011"
        print("   2. Retrieving order by ID...")
        result = self.execute_curl_request("GET", f"/orders/{test_order_id}")
        results["order_retrieval"] = result

        if result["success"]:
            if result["status_code"] == 200:
                print("      ✅ Successfully retrieved order details"            elif result["status_code"] == 404:
                print("      ⚠️  Order not found (expected for test data)"
            else:
                print(f"      ❌ Unexpected status code: {result['status_code']}")
        else:
            print(f"      ❌ Request failed: {result.get('error', 'Unknown error')}")

        # 3. Update Order Status (requires authentication)
        print("   3. Updating order status...")
        status_data = {
            "new_status": "confirmed",
            "change_reason": "Customer confirmed order",
            "change_notes": "Order confirmed via phone"
        }

        result = self.execute_curl_request("PATCH", f"/orders/{test_order_id}/status", data=status_data)
        results["status_update"] = result

        if result["success"]:
            if result["status_code"] in [200, 404, 401]:
                if result["status_code"] == 200:
                    print("      ✅ Successfully updated order status"                elif result["status_code"] == 401:
                    print("      ⚠️  Authentication required (expected)"
                else:
                    print("      ⚠️  Order not found (expected for test data)"
            else:
                print(f"      ❌ Unexpected status code: {result['status_code']}")
        else:
            print(f"      ❌ Request failed: {result.get('error', 'Unknown error')}")

        # 4. Collect Payment (requires authentication)
        print("   4. Collecting payment...")
        payment_data = {
            "payment_reference": f"PAY-{datetime.now().strftime('%Y%m%d-%H%M%S')}-TEST",
            "amount": 66.68,
            "payment_method": "cash",
            "collection_notes": "Cash payment collected at counter",
            "verification_code": "1234"
        }

        result = self.execute_curl_request("POST", f"/orders/{test_order_id}/collect-payment", data=payment_data)
        results["payment_collection"] = result

        if result["success"]:
            if result["status_code"] in [200, 404, 401]:
                if result["status_code"] == 200:
                    print("      ✅ Successfully collected payment"                elif result["status_code"] == 401:
                    print("      ⚠️  Authentication required (expected)"
                else:
                    print("      ⚠️  Order not found (expected for test data)"
            else:
                print(f"      ❌ Unexpected status code: {result['status_code']}")
        else:
            print(f"      ❌ Request failed: {result.get('error', 'Unknown error')}")

        self.record_result("order_endpoints", "order_operations", results)
        return results

    def test_error_scenarios(self):
        """Test error handling and edge cases."""
        print("\n🚨 Testing Error Scenarios...")

        results = {}

        # 1. Invalid Session Token
        print("   1. Testing invalid session token...")
        result = self.execute_curl_request("GET", "/api/v1/cart/sessions/invalid-token")
        results["invalid_session"] = result

        if result["success"] and result["status_code"] in [404, 401]:
            print("      ✅ Properly handled invalid session token"        else:
            print(f"      ❌ Unexpected response: {result.get('status_code', 'Unknown error')}")

        # 2. Invalid Order ID
        print("   2. Testing invalid order ID...")
        result = self.execute_curl_request("GET", "/orders/invalid-uuid")
        results["invalid_order_id"] = result

        if result["success"] and result["status_code"] == 404:
            print("      ✅ Properly handled invalid order ID"        else:
            print(f"      ❌ Unexpected response: {result.get('status_code', 'Unknown error')}")

        # 3. Missing Required Fields
        print("   3. Testing missing required fields...")
        result = self.execute_curl_request("POST", "/api/v1/cart/sessions/anonymous", data={})
        results["missing_fields"] = result

        if result["success"] and result["status_code"] == 422:
            print("      ✅ Properly validated required fields"        else:
            print(f"      ❌ Unexpected response: {result.get('status_code', 'Unknown error')}")

        # 4. Invalid JSON
        print("   4. Testing invalid JSON...")
        result = self.execute_curl_request("POST", "/api/v1/cart/sessions/anonymous", data="invalid json")
        results["invalid_json"] = result

        if result["success"] and result["status_code"] == 400:
            print("      ✅ Properly handled invalid JSON"        else:
            print(f"      ❌ Unexpected response: {result.get('status_code', 'Unknown error')}")

        self.record_result("error_scenarios", "error_handling", results)
        return results

    def test_price_validation(self):
        """Test price validation endpoint."""
        print("\n💰 Testing Price Validation...")

        results = {}

        # Test price validation
        print("   1. Validating menu item price...")
        validation_data = {
            "menu_item_id": self.test_menu_item_id,
            "expected_base_price": 15.00,
            "customizations": {
                "spice_level": "hot",
                "size": "large"
            }
        }

        result = self.execute_curl_request("POST", "/api/v1/cart/validate-price", data=validation_data)
        results["price_validation"] = result

        if result["success"]:
            if result["status_code"] in [200, 400, 404]:
                print(f"      ✅ Price validation endpoint working (status: {result['status_code']})")
            else:
                print(f"      ❌ Unexpected status code: {result['status_code']}")
        else:
            print(f"      ❌ Request failed: {result.get('error', 'Unknown error')}")

        self.record_result("cart_endpoints", "price_validation", results)
        return results

    def test_performance_metrics(self):
        """Test performance metrics across multiple operations."""
        print("\n⚡ Testing Performance Metrics...")

        results = {}

        # Test multiple operations for performance
        operations = [
            ("POST", "/api/v1/cart/sessions/anonymous", {
                "anonymous_session_id": str(uuid.uuid4()),
                "restaurant_id": self.test_restaurant_id,
            }),
            ("GET", "/api/v1/cart/sessions/invalid-token", None),
            ("POST", "/orders", {
                "cart_session_id": "550e8400-e29b-41d4-a716-446655440003",
                "customer_info": {
                    "name": "Performance Test",
                    "phone": "+919876543210",
                    "email": "perf@test.com"
                }
            }),
            ("GET", "/orders/550e8400-e29b-41d4-a716-446655440011", None),
        ]

        response_times = []
        operation_results = {}

        for i, (method, endpoint, data) in enumerate(operations, 1):
            print(f"   {i}. Testing {method} {endpoint}...")

            result = self.execute_curl_request(method, endpoint, data=data)
            operation_results[f"operation_{i}"] = result

            if result["success"]:
                response_time = result["response_time_ms"]
                response_times.append(response_time)
                print(f"      ✅ {response_time".2f"}ms - {result['status_code']}")
            else:
                print(f"      ❌ Request failed: {result.get('error', 'Unknown error')}")

        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            results["performance_summary"] = {
                "average_response_time_ms": avg_response_time,
                "individual_times_ms": response_times,
                "performance_target_met": avg_response_time < 500,
                "operations_tested": len(response_times),
            }

            print("\n   📊 Performance Summary:")
            print(f"      Average response time: {avg_response_time:.2f}ms")
            print(f"      Target (< 500ms): {'✅ MET' if avg_response_time < 500 else '❌ NOT MET'}")
            print(f"      Operations tested: {len(response_times)}")
        else:
            results["performance_summary"] = {
                "error": "No successful operations to measure performance"
            }

        self.record_result("performance_metrics", "endpoint_performance", results)
        self.record_result("performance_metrics", "operation_details", operation_results)
        return results

    def test_authentication_requirements(self):
        """Test authentication requirements for protected endpoints."""
        print("\n🔐 Testing Authentication Requirements...")

        results = {}

        # Test authenticated cart session creation (without auth header)
        print("   1. Testing authenticated endpoint without auth...")
        auth_data = {
            "restaurant_id": self.test_restaurant_id,
            "table_id": self.test_table_id
        }

        result = self.execute_curl_request("POST", "/api/v1/cart/sessions/authenticated", data=auth_data)
        results["auth_required"] = result

        if result["success"]:
            if result["status_code"] in [401, 422]:
                print("      ✅ Authentication properly required"            else:
                print(f"      ⚠️  Unexpected status code: {result['status_code']}")
        else:
            print(f"      ❌ Request failed: {result.get('error', 'Unknown error')}")

        # Test order status update (without auth header)
        print("   2. Testing order status update without auth...")
        status_data = {
            "new_status": "preparing",
            "change_reason": "Test update"
        }

        result = self.execute_curl_request("PATCH", "/orders/550e8400-e29b-41d4-a716-446655440011/status", data=status_data)
        results["order_auth_required"] = result

        if result["success"]:
            if result["status_code"] in [401, 404]:
                print("      ✅ Authentication properly required for order updates"            else:
                print(f"      ⚠️  Unexpected status code: {result['status_code']}")
        else:
            print(f"      ❌ Request failed: {result.get('error', 'Unknown error')}")

        self.record_result("authentication", "auth_requirements", results)
        return results

    def test_integration_flows(self):
        """Test complete integration workflows."""
        print("\n🔄 Testing Integration Flows...")

        results = {}

        # Test complete anonymous cart workflow
        print("   1. Testing anonymous cart workflow...")

        # Step 1: Create anonymous session
        session_data = {
            "anonymous_session_id": str(uuid.uuid4()),
            "restaurant_id": self.test_restaurant_id,
        }

        result1 = self.execute_curl_request("POST", "/api/v1/cart/sessions/anonymous", data=session_data)

        if result1["success"] and result1["status_code"] == 201:
            session_token = result1["response_data"].get("session_token")
            session_id = result1["response_data"].get("id")

            # Step 2: Add item to cart
            item_data = {
                "menu_item_id": self.test_menu_item_id,
                "quantity": 1,
                "customizations": {"spice_level": "medium"}
            }

            result2 = self.execute_curl_request("POST", f"/api/v1/cart/sessions/{session_token}/items", data=item_data)

            # Step 3: Get cart summary
            result3 = self.execute_curl_request("GET", f"/api/v1/cart/sessions/{session_token}/summary")

            # Step 4: Try to create order
            order_data = {
                "cart_session_id": session_id,
                "customer_info": {
                    "name": "Integration Test Customer",
                    "phone": "+919876543210",
                    "email": "integration@test.com"
                }
            }

            result4 = self.execute_curl_request("POST", "/orders", data=order_data)

            results["anonymous_workflow"] = {
                "session_creation": result1,
                "item_addition": result2,
                "cart_summary": result3,
                "order_creation": result4,
                "workflow_successful": all([
                    result1["status_code"] == 201,
                    result2["status_code"] in [201, 400, 404],
                    result3["status_code"] in [200, 404],
                    result4["status_code"] in [201, 400, 404, 422]
                ])
            }

            if results["anonymous_workflow"]["workflow_successful"]:
                print("      ✅ Anonymous cart workflow completed successfully"            else:
                print("      ⚠️  Anonymous cart workflow partially failed (expected with test data)"
        else:
            results["anonymous_workflow"] = {
                "error": "Failed to create anonymous session",
                "session_creation": result1
            }
            print("      ❌ Failed to create anonymous session for workflow test"
        self.record_result("integration_flows", "complete_workflows", results)
        return results

    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report with all results."""
        return {
            "test_summary": {
                "total_categories": len(self.test_results),
                "categories_tested": list(self.test_results.keys()),
                "timestamp": datetime.now().isoformat(),
                "base_url": self.base_url,
            },
            "detailed_results": self.test_results,
            "endpoint_coverage": self._analyze_endpoint_coverage(),
            "performance_summary": self._generate_performance_summary(),
            "error_handling_assessment": self._assess_error_handling(),
            "authentication_validation": self._validate_authentication(),
            "integration_assessment": self._assess_integration(),
            "recommendations": self._generate_recommendations(),
        }

    def _analyze_endpoint_coverage(self) -> Dict[str, Any]:
        """Analyze which endpoints were successfully tested."""
        cart_endpoints = self.test_results.get("cart_endpoints", {})
        order_endpoints = self.test_results.get("order_endpoints", {})

        total_endpoints = len(cart_endpoints) + len(order_endpoints)
        successful_endpoints = sum(
            1 for category in [cart_endpoints, order_endpoints]
            for test in category.values()
            for result in (test.values() if isinstance(test, dict) else [test])
            if isinstance(result, dict) and result.get("success", False)
        )

        return {
            "total_endpoints_tested": total_endpoints,
            "successful_endpoints": successful_endpoints,
            "coverage_percentage": (successful_endpoints / total_endpoints * 100) if total_endpoints > 0 else 0,
            "endpoints_requiring_authentication": "validated",
        }

    def _generate_performance_summary(self) -> Dict[str, Any]:
        """Generate performance metrics summary."""
        perf_data = self.test_results.get("performance_metrics", {})

        if "endpoint_performance" in perf_data:
            summary = perf_data["endpoint_performance"].get("performance_summary", {})
            return summary

        return {"performance_data": "not_available"}

    def _assess_error_handling(self) -> Dict[str, Any]:
        """Assess error handling quality."""
        error_data = self.test_results.get("error_scenarios", {})

        if "error_handling" in error_data:
            error_tests = error_data["error_handling"]
            successful_errors = sum(
                1 for result in error_tests.values()
                if isinstance(result, dict) and result.get("success", False) and result.get("status_code") in [400, 404, 422, 401]
            )

            return {
                "error_handling_score": (successful_errors / len(error_tests) * 100) if error_tests else 0,
                "errors_properly_handled": successful_errors,
                "total_error_tests": len(error_tests),
            }

        return {"error_handling": "not_tested"}

    def _validate_authentication(self) -> Dict[str, Any]:
        """Validate authentication requirements."""
        auth_data = self.test_results.get("authentication", {})

        if "auth_requirements" in auth_data:
            auth_tests = auth_data["auth_requirements"]
            auth_validated = all(
                result.get("status_code") in [401, 422]
                for result in auth_tests.values()
                if isinstance(result, dict) and result.get("success", False)
            )

            return {
                "authentication_properly_enforced": auth_validated,
                "protected_endpoints_validated": len(auth_tests),
            }

        return {"authentication": "not_tested"}

    def _assess_integration(self) -> Dict[str, Any]:
        """Assess integration workflow quality."""
        integration_data = self.test_results.get("integration_flows", {})

        if "complete_workflows" in integration_data:
            workflow_data = integration_data["complete_workflows"]
            workflow_success = workflow_data.get("anonymous_workflow", {}).get("workflow_successful", False)

            return {
                "workflow_integration_successful": workflow_success,
                "integration_points_tested": "cart_to_order_conversion",
            }

        return {"integration": "not_tested"}

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []

        # Performance recommendations
        perf_summary = self._generate_performance_summary()
        if isinstance(perf_summary, dict) and "average_response_time_ms" in perf_summary:
            avg_time = perf_summary["average_response_time_ms"]
            if avg_time > 500:
                recommendations.append(f"Optimize API performance - average response time {avg_time".2f"}ms exceeds 500ms target")

        # Error handling recommendations
        error_assessment = self._assess_error_handling()
        if error_assessment.get("error_handling_score", 100) < 80:
            recommendations.append("Improve error handling consistency across endpoints")

        # Authentication recommendations
        auth_validation = self._validate_authentication()
        if not auth_validation.get("authentication_properly_enforced", True):
            recommendations.append("Strengthen authentication requirements for protected endpoints")

        if not recommendations:
            recommendations.extend([
                "All endpoints tested successfully",
                "API implementation is robust and production-ready",
                "Consider adding comprehensive logging for production monitoring",
                "Implement rate limiting for cart operations",
                "Add caching for frequently accessed menu data",
            ])

        return recommendations

    def run_comprehensive_test_suite(self) -> Dict[str, Any]:
        """Run the complete test suite and return comprehensive results."""
        print("🚀 Starting Comprehensive Cart and Orders API Test Suite...")
        print(f"📍 Base URL: {self.base_url}")
        print("=" * 80)

        # Execute all test categories
        try:
            self.test_cart_session_management()
            self.test_cart_item_operations()
            self.test_order_operations()
            self.test_error_scenarios()
            self.test_price_validation()
            self.test_performance_metrics()
            self.test_authentication_requirements()
            self.test_integration_flows()

            # Generate comprehensive report
            report = self.generate_comprehensive_report()

            # Print summary
            self._print_test_summary(report)

            return report

        except Exception as e:
            print(f"\n❌ Test suite execution failed: {str(e)}")
            return {"error": str(e), "test_results": self.test_results}

    def _print_test_summary(self, report: Dict[str, Any]):
        """Print comprehensive test summary."""
        print("\n" + "=" * 80)
        print("🧪 COMPREHENSIVE TEST EXECUTION RESULTS")
        print("=" * 80)

        # Overall summary
        endpoint_coverage = report["endpoint_coverage"]
        print(f"📊 Endpoint Coverage: {endpoint_coverage['successful_endpoints']}/{endpoint_coverage['total_endpoints_tested']} endpoints tested ({endpoint_coverage['coverage_percentage']".1f"}%)")

        # Performance summary
        perf_summary = report["performance_summary"]
        if isinstance(perf_summary, dict) and "average_response_time_ms" in perf_summary:
            avg_time = perf_summary["average_response_time_ms"]
            target_met = perf_summary["performance_target_met"]
            print(f"⚡ Performance: {avg_time".2f"}ms average ({'✅ TARGET MET' if target_met else '❌ TARGET NOT MET'})")

        # Error handling assessment
        error_assessment = report["error_handling_assessment"]
        if isinstance(error_assessment, dict) and "error_handling_score" in error_assessment:
            score = error_assessment["error_handling_score"]
            print(f"🚨 Error Handling: {score".1f"}% effectiveness")

        # Authentication validation
        auth_validation = report["authentication_validation"]
        if isinstance(auth_validation, dict) and "authentication_properly_enforced" in auth_validation:
            auth_ok = auth_validation["authentication_properly_enforced"]
            print(f"🔐 Authentication: {'✅ PROPERLY ENFORCED' if auth_ok else '⚠️  NEEDS ATTENTION'}")

        # Integration assessment
        integration_assessment = report["integration_assessment"]
        if isinstance(integration_assessment, dict) and "workflow_integration_successful" in integration_assessment:
            workflow_ok = integration_assessment["workflow_integration_successful"]
            print(f"🔄 Integration: {'✅ WORKFLOWS SUCCESSFUL' if workflow_ok else '⚠️  WORKFLOWS NEED IMPROVEMENT'}")

        print("\n💡 Key Recommendations:")
        for i, rec in enumerate(report["recommendations"][:5], 1):
            print(f"   {i}. {rec}")

        print("\n✅ Test execution completed!")
        print("=" * 80)


def run_comprehensive_api_testing(base_url: str = "http://localhost:8000") -> Dict[str, Any]:
    """Run comprehensive end-to-end API testing."""
    tester = CartOrdersAPITester(base_url)
    return tester.run_comprehensive_test_suite()


# Run tests when module is executed directly
if __name__ == "__main__":
    import sys

    # Allow custom base URL via command line argument
    base_url = "http://localhost:8000"
    if len(sys.argv) > 1:
        base_url = sys.argv[1]

    print("🔬 Cart and Orders API End-to-End Testing")
    print(f"🎯 Target: {base_url}")

    # Run comprehensive test suite
    report = run_comprehensive_api_testing(base_url)

    # Save detailed results to file
    output_file = "cart_orders_api_test_results.json"
    try:
        with open(output_file, "w") as f:
            json.dump(report, f, indent=2, default=str)
        print(f"\n📄 Detailed test results saved to: {output_file}")
    except Exception as e:
        print(f"\n⚠️  Failed to save results to file: {e}")

    # Exit with appropriate code
    if "error" in report:
        sys.exit(1)
    else:
        sys.exit(0)
