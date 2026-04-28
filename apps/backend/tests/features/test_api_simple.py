"""Simple API Testing Script."""

import requests
import time
import json

def test_endpoint(method, url, data=None):
    """Test a single endpoint."""
    start_time = time.time()

    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        elif method == "PUT":
            response = requests.put(url, json=data, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, timeout=10)
        elif method == "PATCH":
            response = requests.patch(url, json=data, timeout=10)
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

def run_tests():
    """Run all API tests."""
    base_url = "http://localhost:8000"
    print("🧪 Testing Cart and Orders API Endpoints...")
    print(f"📍 Base URL: {base_url}")

    results = {}

    # Test 1: Anonymous Cart Session
    print("\n1. Testing Anonymous Cart Session...")
    data = {
        "anonymous_session_id": "test-session-123",
        "restaurant_id": "550e8400-e29b-41d4-a716-446655440001",
    }
    result = test_endpoint("POST", f"{base_url}/api/v1/cart/sessions/anonymous", data)
    print(f"   Status: {result.get('status_code', 'ERROR')}")
    print(f"   Response Time: {result.get('response_time_ms', 0):.2f}ms")
    results["anonymous_session"] = result

    # Test 2: Invalid Session Token
    print("\n2. Testing Invalid Session Token...")
    result = test_endpoint("GET", f"{base_url}/api/v1/cart/sessions/invalid-token")
    print(f"   Status: {result.get('status_code', 'ERROR')}")
    print(f"   Response Time: {result.get('response_time_ms', 0):.2f}ms")
    results["invalid_session"] = result

    # Test 3: Order Creation
    print("\n3. Testing Order Creation...")
    order_data = {
        "cart_session_id": "550e8400-e29b-41d4-a716-446655440003",
        "customer_info": {
            "name": "Test Customer",
            "phone": "+919876543210",
            "email": "test@example.com"
        },
    }
    result = test_endpoint("POST", f"{base_url}/orders", order_data)
    print(f"   Status: {result.get('status_code', 'ERROR')}")
    print(f"   Response Time: {result.get('response_time_ms', 0):.2f}ms")
    results["order_creation"] = result

    # Test 4: Invalid Order ID
    print("\n4. Testing Invalid Order ID...")
    result = test_endpoint("GET", f"{base_url}/orders/invalid-uuid")
    print(f"   Status: {result.get('status_code', 'ERROR')}")
    print(f"   Response Time: {result.get('response_time_ms', 0):.2f}ms")
    results["invalid_order"] = result

    # Test 5: Missing Required Fields
    print("\n5. Testing Missing Required Fields...")
    result = test_endpoint("POST", f"{base_url}/api/v1/cart/sessions/anonymous", {})
    print(f"   Status: {result.get('status_code', 'ERROR')}")
    print(f"   Response Time: {result.get('response_time_ms', 0):.2f}ms")
    results["missing_fields"] = result

    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)

    successful_tests = 0
    total_tests = len(results)

    for test_name, result in results.items():
        if result.get("success"):
            successful_tests += 1
            status = result.get("status_code", "ERROR")
            time_ms = result.get("response_time_ms", 0)
            print(f"✅ {test_name}: {status} ({time_ms:.2f}ms)")
        else:
            error = result.get("error", "Unknown error")
            print(f"❌ {test_name}: ERROR - {error}")

    print(f"\n📈 Success Rate: {successful_tests}/{total_tests} ({successful_tests/total_tests*100:.1f}%)")

    # Save results
    with open("api_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)

    print("\n📄 Results saved to: api_test_results.json")

if __name__ == "__main__":
    run_tests()















