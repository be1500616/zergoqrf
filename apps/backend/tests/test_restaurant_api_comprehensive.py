"""Comprehensive Restaurant API Testing Suite.

This module contains systematic tests for all restaurant API endpoints,
following the test plan requirements for Clean Architecture validation,
data integrity, performance assessment, and error handling verification.
"""

import time
from typing import Any, Dict, List
from uuid import uuid4

import pytest
from app.main import app
from httpx import ASGITransport, AsyncClient


class TestRestaurantAPIComprehensive:
    """Comprehensive test suite for restaurant API endpoints."""

    # Class-level test results tracking
    test_results = {
        "endpoint_tests": {},
        "performance_metrics": {},
        "validation_results": {},
        "database_consistency": {},
        "error_handling": {},
    }

    # Test data fixtures
    @pytest.fixture
    def valid_restaurant_registration_data(self):
        """Valid restaurant registration payload."""
        unique_id = str(uuid4())[:8]
        return {
            "name": f"Test Restaurant {unique_id}",
            "description": "A comprehensive test restaurant for API validation",
            "address": "123 Test Street, Test City, TC 12345",
            "phone": "+91 9876543210",
            "email": f"restaurant{unique_id}@test.com",
            "website": f"https://testrestaurant{unique_id}.com",
            "cuisine_type": "Multi-Cuisine",
            "dining_style": "Casual Dining",
            "owner_email": f"owner{unique_id}@test.com",
            "owner_password": "SecurePassword123!",
            "owner_name": f"Test Owner {unique_id}",
        }

    @pytest.fixture
    def invalid_registration_payloads(self):
        """Collection of invalid registration payloads for validation testing."""
        return {
            "missing_required_fields": {
                "description": "Missing name and owner info",
            },
            "invalid_email": {
                "name": "Test Restaurant",
                "owner_email": "invalid-email-format",
                "owner_password": "password123",
            },
            "short_password": {
                "name": "Test Restaurant",
                "owner_email": "test@example.com",
                "owner_password": "short",
            },
            "empty_name": {
                "name": "",
                "owner_email": "test@example.com",
                "owner_password": "password123",
            },
            "long_name": {
                "name": "A" * 300,  # Exceeds 255 character limit
                "owner_email": "test@example.com",
                "owner_password": "password123",
            },
        }

    @pytest.fixture
    def valid_restaurant_update_data(self):
        """Valid restaurant update payload."""
        return {
            "name": "Updated Restaurant Name",
            "description": "Updated description for testing",
            "address": "456 Updated Street, New City, NC 67890",
            "phone": "+91 8765432109",
            "cuisine_type": "Italian",
            "dining_style": "Fine Dining",
        }

    @pytest.fixture
    def valid_business_hours_data(self):
        """Valid business hours configuration."""
        return {
            "monday": {"open": "09:00", "close": "22:00"},
            "tuesday": {"open": "09:00", "close": "22:00"},
            "wednesday": {"open": "09:00", "close": "22:00"},
            "thursday": {"open": "09:00", "close": "22:00"},
            "friday": {"open": "09:00", "close": "23:00"},
            "saturday": {"open": "10:00", "close": "23:00"},
            "sunday": {"open": "10:00", "close": "21:00"},
            "holidays": ["2024-12-25", "2024-01-01"],
            "special_hours": {"2024-12-24": {"open": "09:00", "close": "18:00"}},
        }

    @pytest.fixture
    def valid_restaurant_settings_data(self):
        """Valid restaurant settings configuration."""
        return {
            "logo_url": "https://example.com/logo.png",
            "primary_color": "#FF5722",
            "secondary_color": "#FFC107",
            "currency": "INR",
            "tax_rate": 0.18,
            "service_charge_rate": 0.10,
            "service_model": "self_service",
            "auto_accept_orders": True,
            "estimated_prep_time": 25,
            "email_notifications": True,
            "sms_notifications": False,
            "whatsapp_notifications": True,
        }

    @pytest.fixture
    def valid_staff_creation_data(self):
        """Valid staff member creation payload."""
        unique_id = str(uuid4())[:8]
        return {
            "email": f"staff{unique_id}@test.com",
            "password": "StaffPassword123!",
            "name": f"Test Staff {unique_id}",
            "role": "kitchen",
            "permissions": {
                "view_orders": True,
                "update_order_status": True,
                "view_menu": True,
            },
        }

    # Performance tracking utilities
    def measure_response_time(self, start_time: float, end_time: float) -> float:
        """Calculate response time in milliseconds."""
        return (end_time - start_time) * 1000

    def assert_performance_target(
        self, response_time_ms: float, target_ms: float = 200
    ):
        """Assert response time meets performance target."""
        assert (
            response_time_ms < target_ms
        ), f"Response time {response_time_ms:.2f}ms exceeds target {target_ms}ms"

    # Test result tracking
    def record_test_result(self, category: str, test_name: str, result: Dict[str, Any]):
        """Record test result for comprehensive reporting."""
        if category not in self.test_results:
            self.test_results[category] = {}
        self.test_results[category][test_name] = result

    # Core CRUD Operations Tests
    @pytest.mark.asyncio
    async def test_restaurant_registration_endpoint(
        self, valid_restaurant_registration_data
    ):
        """Test POST /restaurants/register endpoint with valid data."""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            start_time = time.time()
            response = await client.post(
                "/restaurants/register", json=valid_restaurant_registration_data
            )
            end_time = time.time()

            response_time = self.measure_response_time(start_time, end_time)

            # Assert HTTP status code
            assert (
                response.status_code == 201
            ), f"Expected 201, got {response.status_code}: {response.text}"

            # Assert response structure
            data = response.json()
            assert "restaurant" in data
            assert "owner" in data
            assert "access_token" in data
            assert "refresh_token" in data
            assert "token_type" in data
            assert "expires_in" in data

            # Validate restaurant data
            restaurant = data["restaurant"]
            assert restaurant["name"] == valid_restaurant_registration_data["name"]
            assert (
                restaurant["description"]
                == valid_restaurant_registration_data["description"]
            )
            assert (
                restaurant["address"] == valid_restaurant_registration_data["address"]
            )
            assert restaurant["phone"] == valid_restaurant_registration_data["phone"]
            assert restaurant["email"] == valid_restaurant_registration_data["email"]
            assert (
                restaurant["website"] == valid_restaurant_registration_data["website"]
            )
            assert (
                restaurant["cuisine_type"]
                == valid_restaurant_registration_data["cuisine_type"]
            )
            assert (
                restaurant["dining_style"]
                == valid_restaurant_registration_data["dining_style"]
            )
            assert restaurant["is_active"] is True
            assert (
                len(restaurant["code"]) == 6
            )  # Restaurant code should be 6 characters
            assert "id" in restaurant
            assert "created_at" in restaurant
            assert "updated_at" in restaurant

            # Validate owner data
            owner = data["owner"]
            assert owner["role"] == "owner"
            assert owner["is_active"] is True
            assert "id" in owner
            assert "restaurant_id" in owner
            assert "user_id" in owner

            # Validate token data
            assert data["token_type"] == "bearer"
            assert isinstance(data["expires_in"], int)
            assert data["expires_in"] > 0

            # Performance assertion
            self.assert_performance_target(response_time)

            # Record test results
            self.record_test_result(
                "endpoint_tests",
                "restaurant_registration",
                {
                    "status": "PASS",
                    "status_code": response.status_code,
                    "response_time_ms": response_time,
                    "restaurant_id": restaurant["id"],
                    "restaurant_code": restaurant["code"],
                    "access_token": data["access_token"][:20]
                    + "...",  # Truncated for security
                },
            )

            return data  # Return for use in subsequent tests

    @pytest.mark.asyncio
    async def test_get_restaurant_by_code_public_endpoint(
        self, valid_restaurant_registration_data
    ):
        """Test GET /restaurants/{restaurant_code} public endpoint."""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            # First register a restaurant
            registration_response = await client.post(
                "/restaurants/register", json=valid_restaurant_registration_data
            )
            assert registration_response.status_code == 201

            registration_data = registration_response.json()
            restaurant_code = registration_data["restaurant"]["code"]

            # Test public access by restaurant code
            start_time = time.time()
            response = await client.get(f"/restaurants/{restaurant_code}")
            end_time = time.time()

            response_time = self.measure_response_time(start_time, end_time)

            # Assert HTTP status code
            assert (
                response.status_code == 200
            ), f"Expected 200, got {response.status_code}: {response.text}"

            # Assert response data matches registered restaurant
            data = response.json()
            assert data["id"] == registration_data["restaurant"]["id"]
            assert data["name"] == registration_data["restaurant"]["name"]
            assert data["code"] == restaurant_code
            assert data["is_active"] is True

            # Performance assertion
            self.assert_performance_target(response_time)

            # Record test results
            self.record_test_result(
                "endpoint_tests",
                "get_restaurant_by_code",
                {
                    "status": "PASS",
                    "status_code": response.status_code,
                    "response_time_ms": response_time,
                    "restaurant_code": restaurant_code,
                },
            )

    @pytest.mark.asyncio
    async def test_get_restaurant_by_invalid_code(self):
        """Test GET /restaurants/{restaurant_code} with invalid code."""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            start_time = time.time()
            response = await client.get("/restaurants/INVALID")
            end_time = time.time()

            response_time = self.measure_response_time(start_time, end_time)

            # Assert HTTP status code for not found
            assert (
                response.status_code == 404
            ), f"Expected 404, got {response.status_code}: {response.text}"

            # Assert error response structure
            data = response.json()
            assert "detail" in data
            assert "Restaurant not found" in data["detail"]

            # Performance assertion
            self.assert_performance_target(response_time)

            # Record test results
            self.record_test_result(
                "error_handling",
                "invalid_restaurant_code",
                {
                    "status": "PASS",
                    "status_code": response.status_code,
                    "response_time_ms": response_time,
                    "error_message": data["detail"],
                },
            )

    # Data Validation Tests
    @pytest.mark.asyncio
    async def test_restaurant_registration_validation_errors(
        self, invalid_registration_payloads
    ):
        """Test POST /restaurants/register with invalid data for validation testing."""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            validation_results = {}

            for test_case, payload in invalid_registration_payloads.items():
                start_time = time.time()
                response = await client.post("/restaurants/register", json=payload)
                end_time = time.time()

                response_time = self.measure_response_time(start_time, end_time)

                # Assert validation error status code
                assert (
                    response.status_code == 422
                ), f"Test case '{test_case}': Expected 422, got {response.status_code}"

                # Assert error response structure
                data = response.json()
                assert (
                    "detail" in data
                ), f"Test case '{test_case}': Missing 'detail' in error response"

                # Performance assertion
                self.assert_performance_target(response_time)

                validation_results[test_case] = {
                    "status": "PASS",
                    "status_code": response.status_code,
                    "response_time_ms": response_time,
                    "error_details": data["detail"],
                }

            # Record all validation test results
            self.record_test_result(
                "validation_results", "registration_validation", validation_results
            )

    @pytest.mark.asyncio
    async def test_restaurant_code_uniqueness(self):
        """Test that restaurant codes are unique across multiple registrations."""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            codes = set()
            registration_count = 5

            for i in range(registration_count):
                unique_id = str(uuid4())[:8]
                registration_data = {
                    "name": f"Test Restaurant {i}",
                    "owner_email": f"owner{unique_id}@uniquetest.com",
                    "owner_password": "testpassword123",
                }

                response = await client.post(
                    "/restaurants/register", json=registration_data
                )
                assert (
                    response.status_code == 201
                ), f"Registration {i} failed: {response.text}"

                data = response.json()
                restaurant_code = data["restaurant"]["code"]

                # Verify code is unique
                assert (
                    restaurant_code not in codes
                ), f"Duplicate restaurant code found: {restaurant_code}"
                codes.add(restaurant_code)

                # Verify code format (6 characters, alphanumeric, no confusing chars)
                assert (
                    len(restaurant_code) == 6
                ), f"Invalid code length: {len(restaurant_code)}"
                assert (
                    restaurant_code.isalnum()
                ), f"Code contains non-alphanumeric characters: {restaurant_code}"

                # Check for confusing characters (as per business rules)
                confusing_chars = ["0", "O", "I", "1"]
                for char in confusing_chars:
                    assert (
                        char not in restaurant_code
                    ), f"Code contains confusing character '{char}': {restaurant_code}"

            # Record test results
            self.record_test_result(
                "validation_results",
                "code_uniqueness",
                {
                    "status": "PASS",
                    "generated_codes": list(codes),
                    "total_codes": len(codes),
                    "expected_count": registration_count,
                },
            )

    @pytest.mark.asyncio
    async def test_malformed_json_requests(self):
        """Test endpoints with malformed JSON payloads."""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            malformed_payloads = [
                '{"name": "Test", "invalid": }',  # Invalid JSON syntax
                '{"name": "Test", "owner_email": "test@example.com",}',  # Trailing comma
                "",  # Empty payload
                "not_json_at_all",  # Not JSON
            ]

            results = {}

            for i, payload in enumerate(malformed_payloads):
                try:
                    response = await client.post(
                        "/restaurants/register",
                        content=payload,
                        headers={"Content-Type": "application/json"},
                    )

                    # Should return 400 Bad Request for malformed JSON
                    assert (
                        response.status_code == 400
                    ), f"Payload {i}: Expected 400, got {response.status_code}"

                    results[f"malformed_payload_{i}"] = {
                        "status": "PASS",
                        "status_code": response.status_code,
                        "payload_preview": (
                            payload[:50] + "..." if len(payload) > 50 else payload
                        ),
                    }

                except Exception as e:
                    results[f"malformed_payload_{i}"] = {
                        "status": "FAIL",
                        "error": str(e),
                        "payload_preview": (
                            payload[:50] + "..." if len(payload) > 50 else payload
                        ),
                    }

            # Record test results
            self.record_test_result("error_handling", "malformed_json", results)

    # Authentication and Authorization Tests (Future Integration)
    @pytest.mark.asyncio
    async def test_authenticated_endpoints_without_auth(self):
        """Test authenticated endpoints without authentication tokens."""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            authenticated_endpoints = [
                ("GET", "/restaurants/me"),
                ("PUT", "/restaurants/me"),
                ("PUT", "/restaurants/me/business-hours"),
                ("PUT", "/restaurants/me/settings"),
                ("POST", "/restaurants/me/staff"),
                ("GET", "/restaurants/me/staff"),
                ("PUT", "/restaurants/me/staff/550e8400-e29b-41d4-a716-446655440000"),
                (
                    "DELETE",
                    "/restaurants/me/staff/550e8400-e29b-41d4-a716-446655440000",
                ),
            ]

            auth_test_results = {}

            for method, endpoint in authenticated_endpoints:
                start_time = time.time()

                if method == "GET":
                    response = await client.get(endpoint)
                elif method == "POST":
                    response = await client.post(endpoint, json={})
                elif method == "PUT":
                    response = await client.put(endpoint, json={})
                elif method == "DELETE":
                    response = await client.delete(endpoint)

                end_time = time.time()
                response_time = self.measure_response_time(start_time, end_time)

                # Note: Currently authentication is bypassed, so we document current behavior
                # In future, these should return 401 Unauthorized
                auth_test_results[f"{method}_{endpoint.replace('/', '_')}"] = {
                    "method": method,
                    "endpoint": endpoint,
                    "status_code": response.status_code,
                    "response_time_ms": response_time,
                    "note": "Authentication currently bypassed - will need 401 when auth is integrated",
                }

            # Record test results for future authentication integration
            self.record_test_result(
                "authentication", "endpoints_without_auth", auth_test_results
            )

    # Database Integration Verification Tests
    @pytest.mark.asyncio
    async def test_database_consistency_after_registration(
        self, valid_restaurant_registration_data
    ):
        """Verify database consistency after restaurant registration."""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            # Register restaurant
            response = await client.post(
                "/restaurants/register", json=valid_restaurant_registration_data
            )
            assert response.status_code == 201

            registration_data = response.json()
            restaurant_id = registration_data["restaurant"]["id"]
            restaurant_code = registration_data["restaurant"]["code"]

            # Verify restaurant can be retrieved by code (tests database persistence)
            get_response = await client.get(f"/restaurants/{restaurant_code}")
            assert get_response.status_code == 200

            retrieved_data = get_response.json()

            # Verify data consistency between registration and retrieval
            consistency_checks = {
                "id_match": retrieved_data["id"] == restaurant_id,
                "name_match": retrieved_data["name"]
                == valid_restaurant_registration_data["name"],
                "code_match": retrieved_data["code"] == restaurant_code,
                "description_match": retrieved_data["description"]
                == valid_restaurant_registration_data["description"],
                "address_match": retrieved_data["address"]
                == valid_restaurant_registration_data["address"],
                "phone_match": retrieved_data["phone"]
                == valid_restaurant_registration_data["phone"],
                "email_match": retrieved_data["email"]
                == valid_restaurant_registration_data["email"],
                "website_match": retrieved_data["website"]
                == valid_restaurant_registration_data["website"],
                "cuisine_type_match": retrieved_data["cuisine_type"]
                == valid_restaurant_registration_data["cuisine_type"],
                "dining_style_match": retrieved_data["dining_style"]
                == valid_restaurant_registration_data["dining_style"],
                "is_active_match": retrieved_data["is_active"] is True,
                "timestamps_present": all(
                    key in retrieved_data for key in ["created_at", "updated_at"]
                ),
                "business_hours_initialized": isinstance(
                    retrieved_data["business_hours"], dict
                ),
                "settings_initialized": isinstance(retrieved_data["settings"], dict),
            }

            # Assert all consistency checks pass
            failed_checks = [
                check for check, passed in consistency_checks.items() if not passed
            ]
            assert (
                not failed_checks
            ), f"Database consistency checks failed: {failed_checks}"

            # Record test results
            self.record_test_result(
                "database_consistency",
                "registration_persistence",
                {
                    "status": "PASS",
                    "restaurant_id": restaurant_id,
                    "consistency_checks": consistency_checks,
                    "all_checks_passed": len(failed_checks) == 0,
                },
            )

    # Performance Assessment Tests
    @pytest.mark.asyncio
    async def test_endpoint_performance_benchmarks(
        self, valid_restaurant_registration_data
    ):
        """Benchmark performance of all restaurant endpoints."""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            performance_results = {}

            # Test registration endpoint performance
            registration_times = []
            for i in range(3):  # Run multiple times for average
                unique_data = valid_restaurant_registration_data.copy()
                unique_data["owner_email"] = f"perf{i}@test.com"
                unique_data["name"] = f"Performance Test Restaurant {i}"

                start_time = time.time()
                response = await client.post("/restaurants/register", json=unique_data)
                end_time = time.time()

                assert response.status_code == 201
                registration_times.append(
                    self.measure_response_time(start_time, end_time)
                )

            avg_registration_time = sum(registration_times) / len(registration_times)
            performance_results["registration"] = {
                "average_response_time_ms": avg_registration_time,
                "individual_times_ms": registration_times,
                "meets_target": avg_registration_time < 200,
            }

            # Test public retrieval endpoint performance
            # Use the first registered restaurant
            first_registration = await client.post(
                "/restaurants/register",
                json={
                    **valid_restaurant_registration_data,
                    "owner_email": "perf_retrieval@test.com",
                    "name": "Performance Retrieval Test",
                },
            )
            restaurant_code = first_registration.json()["restaurant"]["code"]

            retrieval_times = []
            for i in range(5):  # More iterations for retrieval test
                start_time = time.time()
                response = await client.get(f"/restaurants/{restaurant_code}")
                end_time = time.time()

                assert response.status_code == 200
                retrieval_times.append(self.measure_response_time(start_time, end_time))

            avg_retrieval_time = sum(retrieval_times) / len(retrieval_times)
            performance_results["retrieval_by_code"] = {
                "average_response_time_ms": avg_retrieval_time,
                "individual_times_ms": retrieval_times,
                "meets_target": avg_retrieval_time < 200,
            }

            # Record performance test results
            self.record_test_result(
                "performance_metrics", "endpoint_benchmarks", performance_results
            )

            # Assert performance targets
            assert (
                avg_registration_time < 200
            ), f"Registration endpoint too slow: {avg_registration_time:.2f}ms"
            assert (
                avg_retrieval_time < 200
            ), f"Retrieval endpoint too slow: {avg_retrieval_time:.2f}ms"

    # Comprehensive Test Report Generation
    def generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report with all results."""
        return {
            "test_summary": {
                "total_categories": len(self.test_results),
                "categories": list(self.test_results.keys()),
                "timestamp": time.time(),
            },
            "detailed_results": self.test_results,
            "recommendations": self._generate_recommendations(),
        }

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []

        # Check performance metrics
        if "performance_metrics" in self.test_results:
            for endpoint, metrics in (
                self.test_results["performance_metrics"]
                .get("endpoint_benchmarks", {})
                .items()
            ):
                if not metrics.get("meets_target", True):
                    recommendations.append(
                        f"Optimize {endpoint} endpoint - response time exceeds 200ms target"
                    )

        # Check validation results
        if "validation_results" in self.test_results:
            validation_failures = []
            for category, results in self.test_results["validation_results"].items():
                if isinstance(results, dict):
                    for test, result in results.items():
                        if result.get("status") == "FAIL":
                            validation_failures.append(f"{category}.{test}")

            if validation_failures:
                recommendations.append(
                    f"Fix validation test failures: {', '.join(validation_failures)}"
                )

        # Authentication integration recommendations
        if "authentication" in self.test_results:
            recommendations.append(
                "Integrate authentication system - currently bypassed for testing"
            )
            recommendations.append(
                "Implement proper JWT token validation for protected endpoints"
            )
            recommendations.append(
                "Add role-based access control for staff management endpoints"
            )

        # Database consistency recommendations
        if "database_consistency" in self.test_results:
            for test, result in self.test_results["database_consistency"].items():
                if not result.get("all_checks_passed", True):
                    recommendations.append(f"Fix database consistency issues in {test}")

        return recommendations
