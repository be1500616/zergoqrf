"""Comprehensive end-to-end testing script for authentication endpoints.

This script tests all authentication endpoints against the running FastAPI server
with the actual Supabase database.
"""

import json
import sys
from datetime import datetime
from typing import Any, Dict, Optional

import requests

# Configuration
BASE_URL = "http://127.0.0.1:8000"
TEST_EMAIL_1 = "test@gmail.com"
TEST_PASSWORD_1 = "test1234"
TEST_EMAIL_2 = "customer@gmail.com"
TEST_PASSWORD_2 = "customer1234"
TEST_PHONE = "+917484999999"
TEST_OTP = "123456"


class Colors:
    """ANSI color codes for terminal output."""

    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


class TestResult:
    """Container for test results."""

    def __init__(
        self, name: str, passed: bool, message: str, response: Optional[Dict] = None
    ):
        self.name = name
        self.passed = passed
        self.message = message
        self.response = response
        self.timestamp = datetime.now()


class AuthEndpointTester:
    """Tester for authentication endpoints."""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.results = []
        self.access_token = None
        self.refresh_token = None

    def log_test(
        self, name: str, passed: bool, message: str, response: Optional[Dict] = None
    ):
        """Log a test result."""
        result = TestResult(name, passed, message, response)
        self.results.append(result)

        status = (
            f"{Colors.GREEN}✓ PASS{Colors.RESET}"
            if passed
            else f"{Colors.RED}✗ FAIL{Colors.RESET}"
        )
        print(f"{status}: {name}")
        print(f"  {message}")
        if not passed and response:
            print(f"  Response: {json.dumps(response, indent=2)}")
        print()

    def test_health_check(self) -> bool:
        """Test the health check endpoint."""
        try:
            response = requests.get(f"{self.base_url}/healthz", timeout=5)
            if response.status_code == 200:
                self.log_test(
                    "Health Check",
                    True,
                    f"Server is healthy (status: {response.status_code})",
                )
                return True
            else:
                self.log_test(
                    "Health Check",
                    False,
                    f"Unexpected status code: {response.status_code}",
                    response.json() if response.text else None,
                )
                return False
        except Exception as e:
            self.log_test("Health Check", False, f"Connection error: {str(e)}")
            return False

    def test_email_signup(
        self, email: str, password: str, name: str = "Test User"
    ) -> bool:
        """Test email signup endpoint."""
        try:
            payload = {
                "email": email,
                "password": password,
                "name": name,
                "role": "customer",
            }
            response = requests.post(
                f"{self.base_url}/auth/signup/email", json=payload, timeout=10
            )

            if response.status_code in [200, 201]:
                data = response.json()
                if "access_token" in data:
                    self.access_token = data["access_token"]
                    self.refresh_token = data.get("refresh_token")
                    self.log_test(
                        f"Email Signup ({email})",
                        True,
                        f"User created successfully (status: {response.status_code})",
                        data,
                    )
                    return True
                else:
                    self.log_test(
                        f"Email Signup ({email})",
                        False,
                        "Response missing access_token",
                        data,
                    )
                    return False
            elif response.status_code == 409:
                # User already exists - this is okay for testing
                self.log_test(
                    f"Email Signup ({email})",
                    True,
                    "User already exists (expected for repeat tests)",
                    response.json() if response.text else None,
                )
                return True
            else:
                self.log_test(
                    f"Email Signup ({email})",
                    False,
                    f"Unexpected status code: {response.status_code}",
                    response.json() if response.text else None,
                )
                return False
        except Exception as e:
            self.log_test(f"Email Signup ({email})", False, f"Error: {str(e)}")
            return False

    def test_email_signin(self, email: str, password: str) -> bool:
        """Test email signin endpoint."""
        try:
            payload = {"email": email, "password": password}
            response = requests.post(
                f"{self.base_url}/auth/signin/email", json=payload, timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.access_token = data["access_token"]
                    self.refresh_token = data.get("refresh_token")
                    self.log_test(
                        f"Email Sign In ({email})",
                        True,
                        "Authentication successful",
                        data,
                    )
                    return True
                else:
                    self.log_test(
                        f"Email Sign In ({email})",
                        False,
                        "Response missing access_token",
                        data,
                    )
                    return False
            else:
                self.log_test(
                    f"Email Sign In ({email})",
                    False,
                    f"Authentication failed (status: {response.status_code})",
                    response.json() if response.text else None,
                )
                return False
        except Exception as e:
            self.log_test(f"Email Sign In ({email})", False, f"Error: {str(e)}")
            return False

    def test_email_signin_invalid(self, email: str, password: str) -> bool:
        """Test email signin with invalid credentials."""
        try:
            payload = {"email": email, "password": password}
            response = requests.post(
                f"{self.base_url}/auth/signin/email", json=payload, timeout=10
            )

            if response.status_code in [401, 400]:
                self.log_test(
                    f"Email Sign In - Invalid Credentials ({email})",
                    True,
                    f"Correctly rejected invalid credentials (status: {response.status_code})",
                )
                return True
            else:
                self.log_test(
                    f"Email Sign In - Invalid Credentials ({email})",
                    False,
                    f"Unexpected status code: {response.status_code}",
                    response.json() if response.text else None,
                )
                return False
        except Exception as e:
            self.log_test(
                f"Email Sign In - Invalid Credentials ({email})",
                False,
                f"Error: {str(e)}",
            )
            return False

    def test_phone_signin(self, phone: str) -> bool:
        """Test phone signin (OTP initiation) endpoint."""
        try:
            payload = {"phone": phone}
            response = requests.post(
                f"{self.base_url}/auth/signin/phone", json=payload, timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    f"Phone Sign In - OTP Sent ({phone})",
                    True,
                    "OTP sent successfully",
                    data,
                )
                return True
            else:
                self.log_test(
                    f"Phone Sign In - OTP Sent ({phone})",
                    False,
                    f"Failed to send OTP (status: {response.status_code})",
                    response.json() if response.text else None,
                )
                return False
        except Exception as e:
            self.log_test(
                f"Phone Sign In - OTP Sent ({phone})", False, f"Error: {str(e)}"
            )
            return False

    def test_phone_verify(
        self, phone: str, token: str, name: str = "Phone User"
    ) -> bool:
        """Test phone OTP verification endpoint."""
        try:
            payload = {"phone": phone, "token": token, "name": name}
            response = requests.post(
                f"{self.base_url}/auth/verify/phone", json=payload, timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.access_token = data["access_token"]
                    self.refresh_token = data.get("refresh_token")
                    self.log_test(
                        f"Phone OTP Verification ({phone})",
                        True,
                        "OTP verified successfully",
                        data,
                    )
                    return True
                else:
                    self.log_test(
                        f"Phone OTP Verification ({phone})",
                        False,
                        "Response missing access_token",
                        data,
                    )
                    return False
            else:
                self.log_test(
                    f"Phone OTP Verification ({phone})",
                    False,
                    f"OTP verification failed (status: {response.status_code})",
                    response.json() if response.text else None,
                )
                return False
        except Exception as e:
            self.log_test(
                f"Phone OTP Verification ({phone})", False, f"Error: {str(e)}"
            )
            return False

    def test_anonymous_session(
        self, restaurant_id: str, table_id: Optional[str] = None
    ) -> bool:
        """Test anonymous session creation endpoint."""
        try:
            payload = {
                "restaurant_id": restaurant_id,
                "table_id": table_id or restaurant_id,  # Use restaurant_id as fallback
            }
            response = requests.post(
                f"{self.base_url}/auth/anonymous-session", json=payload, timeout=10
            )

            if response.status_code in [200, 201]:
                data = response.json()
                if "session_token" in data:
                    self.log_test(
                        "Anonymous Session Creation",
                        True,
                        "Anonymous session created successfully",
                        data,
                    )
                    return True
                else:
                    self.log_test(
                        "Anonymous Session Creation",
                        False,
                        "Response missing session_token",
                        data,
                    )
                    return False
            else:
                self.log_test(
                    "Anonymous Session Creation",
                    False,
                    f"Failed to create session (status: {response.status_code})",
                    response.json() if response.text else None,
                )
                return False
        except Exception as e:
            self.log_test("Anonymous Session Creation", False, f"Error: {str(e)}")
            return False

    def test_token_refresh(self) -> bool:
        """Test token refresh endpoint."""
        if not self.refresh_token:
            self.log_test(
                "Token Refresh",
                False,
                "No refresh token available (must sign in first)",
            )
            return False

        try:
            payload = {"refresh_token": self.refresh_token}
            response = requests.post(
                f"{self.base_url}/auth/refresh", json=payload, timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.access_token = data["access_token"]
                    self.log_test(
                        "Token Refresh", True, "Token refreshed successfully", data
                    )
                    return True
                else:
                    self.log_test(
                        "Token Refresh", False, "Response missing access_token", data
                    )
                    return False
            else:
                self.log_test(
                    "Token Refresh",
                    False,
                    f"Token refresh failed (status: {response.status_code})",
                    response.json() if response.text else None,
                )
                return False
        except Exception as e:
            self.log_test("Token Refresh", False, f"Error: {str(e)}")
            return False

    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 70)
        print(f"{Colors.BOLD}TEST SUMMARY{Colors.RESET}")
        print("=" * 70)

        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed

        print(f"Total Tests: {total}")
        print(f"{Colors.GREEN}Passed: {passed}{Colors.RESET}")
        print(f"{Colors.RED}Failed: {failed}{Colors.RESET}")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        print()

        if failed > 0:
            print(f"{Colors.RED}Failed Tests:{Colors.RESET}")
            for result in self.results:
                if not result.passed:
                    print(f"  - {result.name}: {result.message}")

        print("=" * 70)
        return passed == total


def main():
    """Run all authentication endpoint tests."""
    print(f"\n{Colors.BOLD}╔{'=' * 68}╗{Colors.RESET}")
    print(
        f"{Colors.BOLD}║{' ' * 15}AUTHENTICATION ENDPOINTS E2E TESTING{' ' * 15}║{Colors.RESET}"
    )
    print(f"{Colors.BOLD}╚{'=' * 68}╝{Colors.RESET}\n")

    tester = AuthEndpointTester(BASE_URL)

    # Test 1: Health Check
    print(f"{Colors.BLUE}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BLUE}Phase 1: Server Health Check{Colors.RESET}")
    print(f"{Colors.BLUE}{'=' * 70}{Colors.RESET}\n")

    if not tester.test_health_check():
        print(
            f"\n{Colors.RED}Server is not responding. Please start the server first.{Colors.RESET}"
        )
        print(
            f"Run: cd apps/backend && source venv/bin/activate && uvicorn app.main:app --reload"
        )
        return 1

    # Test 2: Email Authentication
    print(f"{Colors.BLUE}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BLUE}Phase 2: Email Authentication{Colors.RESET}")
    print(f"{Colors.BLUE}{'=' * 70}{Colors.RESET}\n")

    tester.test_email_signup(TEST_EMAIL_1, TEST_PASSWORD_1, "Test User 1")
    tester.test_email_signin(TEST_EMAIL_1, TEST_PASSWORD_1)
    tester.test_email_signin_invalid(TEST_EMAIL_1, "wrongpassword")

    # Test 3: Phone Authentication
    print(f"{Colors.BLUE}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BLUE}Phase 3: Phone Authentication{Colors.RESET}")
    print(f"{Colors.BLUE}{'=' * 70}{Colors.RESET}\n")

    tester.test_phone_signin(TEST_PHONE)
    tester.test_phone_verify(TEST_PHONE, TEST_OTP, "Phone Test User")

    # Test 4: Anonymous Session
    print(f"{Colors.BLUE}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BLUE}Phase 4: Anonymous Session{Colors.RESET}")
    print(f"{Colors.BLUE}{'=' * 70}{Colors.RESET}\n")

    # Use a test restaurant ID (you may need to adjust this)
    test_restaurant_id = "550e8400-e29b-41d4-a716-446655440000"
    tester.test_anonymous_session(test_restaurant_id)

    # Test 5: Token Refresh
    print(f"{Colors.BLUE}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BLUE}Phase 5: Token Refresh{Colors.RESET}")
    print(f"{Colors.BLUE}{'=' * 70}{Colors.RESET}\n")

    # First sign in to get a refresh token
    tester.test_email_signin(TEST_EMAIL_1, TEST_PASSWORD_1)
    tester.test_token_refresh()

    # Print summary
    all_passed = tester.print_summary()

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
