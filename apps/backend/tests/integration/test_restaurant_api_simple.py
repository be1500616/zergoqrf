#!/usr/bin/env python3
"""Simple Restaurant API Test Runner.

This script tests the restaurant API endpoints directly without complex setup.
It focuses on testing the core functionality and generating a comprehensive report.
"""

import json
import time
import requests
from datetime import datetime
from typing import Dict, Any, List
from uuid import uuid4


class RestaurantAPITester:
    """Simple restaurant API tester."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = {
            "endpoint_tests": {},
            "performance_metrics": {},
            "validation_results": {},
            "error_handling": {},
        }
        
    def test_server_health(self) -> bool:
        """Test if the server is running and accessible."""
        try:
            response = requests.get(f"{self.base_url}/healthz", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def measure_response_time(self, start_time: float, end_time: float) -> float:
        """Calculate response time in milliseconds."""
        return (end_time - start_time) * 1000
    
    def record_test_result(self, category: str, test_name: str, result: Dict[str, Any]):
        """Record test result for reporting."""
        if category not in self.test_results:
            self.test_results[category] = {}
        self.test_results[category][test_name] = result
    
    def test_restaurant_registration(self) -> Dict[str, Any]:
        """Test restaurant registration endpoint."""
        print("🧪 Testing restaurant registration endpoint...")
        
        unique_id = str(uuid4())[:8]
        registration_data = {
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
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/restaurants/register",
                json=registration_data,
                timeout=10
            )
            end_time = time.time()
            
            response_time = self.measure_response_time(start_time, end_time)
            
            result = {
                "status": "PASS" if response.status_code == 201 else "FAIL",
                "status_code": response.status_code,
                "response_time_ms": response_time,
                "meets_performance_target": response_time < 200,
            }
            
            if response.status_code == 201:
                data = response.json()
                result.update({
                    "restaurant_id": data.get("restaurant", {}).get("id"),
                    "restaurant_code": data.get("restaurant", {}).get("code"),
                    "has_access_token": "access_token" in data,
                    "has_refresh_token": "refresh_token" in data,
                })
                
                # Validate response structure
                required_fields = ["restaurant", "owner", "access_token", "refresh_token"]
                missing_fields = [field for field in required_fields if field not in data]
                result["missing_fields"] = missing_fields
                result["response_structure_valid"] = len(missing_fields) == 0
                
                return data  # Return for use in subsequent tests
            else:
                result["error_message"] = response.text
                
        except Exception as e:
            result = {
                "status": "ERROR",
                "error": str(e),
                "response_time_ms": 0,
                "meets_performance_target": False,
            }
        
        self.record_test_result("endpoint_tests", "restaurant_registration", result)
        return result
    
    def test_get_restaurant_by_code(self, restaurant_code: str) -> Dict[str, Any]:
        """Test getting restaurant by code (public endpoint)."""
        print(f"🧪 Testing get restaurant by code: {restaurant_code}")
        
        try:
            start_time = time.time()
            response = requests.get(
                f"{self.base_url}/restaurants/{restaurant_code}",
                timeout=10
            )
            end_time = time.time()
            
            response_time = self.measure_response_time(start_time, end_time)
            
            result = {
                "status": "PASS" if response.status_code == 200 else "FAIL",
                "status_code": response.status_code,
                "response_time_ms": response_time,
                "meets_performance_target": response_time < 200,
                "restaurant_code": restaurant_code,
            }
            
            if response.status_code == 200:
                data = response.json()
                result.update({
                    "restaurant_id": data.get("id"),
                    "restaurant_name": data.get("name"),
                    "is_active": data.get("is_active"),
                })
            else:
                result["error_message"] = response.text
                
        except Exception as e:
            result = {
                "status": "ERROR",
                "error": str(e),
                "response_time_ms": 0,
                "meets_performance_target": False,
            }
        
        self.record_test_result("endpoint_tests", "get_restaurant_by_code", result)
        return result
    
    def test_invalid_restaurant_code(self) -> Dict[str, Any]:
        """Test getting restaurant with invalid code."""
        print("🧪 Testing invalid restaurant code handling...")
        
        try:
            start_time = time.time()
            response = requests.get(
                f"{self.base_url}/restaurants/INVALID",
                timeout=10
            )
            end_time = time.time()
            
            response_time = self.measure_response_time(start_time, end_time)
            
            result = {
                "status": "PASS" if response.status_code == 404 else "FAIL",
                "status_code": response.status_code,
                "response_time_ms": response_time,
                "expected_status": 404,
            }
            
            if response.status_code == 404:
                data = response.json()
                result["error_message"] = data.get("detail", "")
                result["proper_error_format"] = "detail" in data
            else:
                result["unexpected_response"] = response.text
                
        except Exception as e:
            result = {
                "status": "ERROR",
                "error": str(e),
                "response_time_ms": 0,
            }
        
        self.record_test_result("error_handling", "invalid_restaurant_code", result)
        return result
    
    def test_validation_errors(self) -> Dict[str, Any]:
        """Test input validation with invalid data."""
        print("🧪 Testing input validation...")
        
        invalid_payloads = {
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
        }
        
        validation_results = {}
        
        for test_case, payload in invalid_payloads.items():
            try:
                start_time = time.time()
                response = requests.post(
                    f"{self.base_url}/restaurants/register",
                    json=payload,
                    timeout=10
                )
                end_time = time.time()
                
                response_time = self.measure_response_time(start_time, end_time)
                
                validation_results[test_case] = {
                    "status": "PASS" if response.status_code == 422 else "FAIL",
                    "status_code": response.status_code,
                    "response_time_ms": response_time,
                    "expected_status": 422,
                }
                
                if response.status_code == 422:
                    data = response.json()
                    validation_results[test_case]["error_details"] = data.get("detail", [])
                else:
                    validation_results[test_case]["unexpected_response"] = response.text
                    
            except Exception as e:
                validation_results[test_case] = {
                    "status": "ERROR",
                    "error": str(e),
                }
        
        self.record_test_result("validation_results", "input_validation", validation_results)
        return validation_results
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and generate comprehensive report."""
        print("🚀 Starting Restaurant API Testing...")
        print("=" * 60)
        
        # Check if server is running
        if not self.test_server_health():
            print("❌ Server is not running or not accessible!")
            print("Please start the server with: cd apps/backend && python -m uvicorn app.main:app --reload")
            return {"error": "Server not accessible"}
        
        print("✅ Server is running and accessible")
        
        start_time = time.time()
        
        # Test 1: Restaurant Registration
        registration_result = self.test_restaurant_registration()
        
        # Test 2: Get Restaurant by Code (if registration succeeded)
        if isinstance(registration_result, dict) and "restaurant" in registration_result:
            restaurant_code = registration_result["restaurant"]["code"]
            self.test_get_restaurant_by_code(restaurant_code)
        
        # Test 3: Invalid Restaurant Code
        self.test_invalid_restaurant_code()
        
        # Test 4: Validation Errors
        self.test_validation_errors()
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        # Generate comprehensive report
        report = self.generate_comprehensive_report(total_duration)
        
        return report
    
    def generate_comprehensive_report(self, duration: float) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        # Count test results
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        
        for category, tests in self.test_results.items():
            if isinstance(tests, dict):
                for test_name, result in tests.items():
                    if isinstance(result, dict):
                        if "status" in result:
                            total_tests += 1
                            if result["status"] == "PASS":
                                passed_tests += 1
                            else:
                                failed_tests += 1
                    elif isinstance(result, dict):  # Nested results like validation
                        for sub_test, sub_result in result.items():
                            if isinstance(sub_result, dict) and "status" in sub_result:
                                total_tests += 1
                                if sub_result["status"] == "PASS":
                                    passed_tests += 1
                                else:
                                    failed_tests += 1
        
        # Calculate performance metrics
        performance_summary = self.calculate_performance_summary()
        
        report = {
            "executive_summary": {
                "overall_status": "PASS" if failed_tests == 0 else "FAIL",
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                "test_execution_duration_seconds": round(duration, 2),
                "performance_target_met": performance_summary["all_meet_target"],
                "average_response_time_ms": performance_summary["average_response_time"],
            },
            "detailed_results": self.test_results,
            "performance_analysis": performance_summary,
            "recommendations": self.generate_recommendations(),
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "base_url": self.base_url,
                "target_performance": "200ms response time",
            }
        }
        
        return report
    
    def calculate_performance_summary(self) -> Dict[str, Any]:
        """Calculate performance metrics summary."""
        response_times = []
        meets_target_count = 0
        total_performance_tests = 0
        
        for category, tests in self.test_results.items():
            for test_name, result in tests.items():
                if isinstance(result, dict) and "response_time_ms" in result:
                    response_times.append(result["response_time_ms"])
                    total_performance_tests += 1
                    if result.get("meets_performance_target", False):
                        meets_target_count += 1
        
        return {
            "total_performance_tests": total_performance_tests,
            "average_response_time": round(sum(response_times) / len(response_times), 2) if response_times else 0,
            "max_response_time": max(response_times) if response_times else 0,
            "min_response_time": min(response_times) if response_times else 0,
            "meets_target_count": meets_target_count,
            "all_meet_target": meets_target_count == total_performance_tests if total_performance_tests > 0 else False,
        }
    
    def generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []
        
        # Check for failed tests
        for category, tests in self.test_results.items():
            for test_name, result in tests.items():
                if isinstance(result, dict) and result.get("status") == "FAIL":
                    recommendations.append(f"Fix failing test: {category}.{test_name}")
        
        # Performance recommendations
        performance_summary = self.calculate_performance_summary()
        if not performance_summary["all_meet_target"]:
            recommendations.append("Optimize endpoints that exceed 200ms response time target")
        
        # General recommendations
        recommendations.extend([
            "Integrate JWT authentication system",
            "Implement comprehensive error logging",
            "Add request rate limiting",
            "Set up monitoring and alerting",
            "Add comprehensive integration tests",
        ])
        
        return recommendations
    
    def save_report(self, report: Dict[str, Any], filename: str = None) -> str:
        """Save test report to file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"restaurant_api_test_report_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return filename
    
    def print_summary(self, report: Dict[str, Any]):
        """Print executive summary to console."""
        print("\n" + "=" * 60)
        print("🏁 RESTAURANT API TEST EXECUTION COMPLETE")
        print("=" * 60)
        
        summary = report["executive_summary"]
        print(f"📊 Overall Status: {summary['overall_status']}")
        print(f"🧪 Tests: {summary['passed_tests']}/{summary['total_tests']} passed ({summary['success_rate']:.1f}%)")
        print(f"⏱️  Execution Time: {summary['test_execution_duration_seconds']}s")
        print(f"🚀 Performance: Avg {summary['average_response_time_ms']}ms (Target: <200ms)")
        
        if summary['failed_tests'] > 0:
            print(f"❌ Failed Tests: {summary['failed_tests']}")
        
        print("\n📋 Key Recommendations:")
        for i, rec in enumerate(report["recommendations"][:5], 1):
            print(f"  {i}. {rec}")
        
        print("=" * 60)


def main():
    """Main test execution function."""
    tester = RestaurantAPITester()
    
    try:
        # Run all tests
        report = tester.run_all_tests()
        
        if "error" in report:
            print(f"❌ {report['error']}")
            return 1
        
        # Save detailed report
        report_file = tester.save_report(report)
        
        # Print summary
        tester.print_summary(report)
        
        print(f"\n📄 Full report saved to: {report_file}")
        
        # Return appropriate exit code
        return 0 if report["executive_summary"]["overall_status"] == "PASS" else 1
        
    except Exception as e:
        print(f"\n❌ Test execution failed: {str(e)}")
        return 1


if __name__ == "__main__":
    import sys
    exit_code = main()
    sys.exit(exit_code)
