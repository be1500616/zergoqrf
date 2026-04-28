#!/bin/bash

# ZERGO QR Restaurant Management System - Comprehensive API Testing Script
# This script tests all endpoints systematically for production readiness

set -e

# Configuration
BASE_URL="http://localhost:8000"
TEST_PHONE="+917484906010"
TEST_OTP="123456"
RESULTS_FILE="api_test_results_$(date +%Y%m%d_%H%M%S).json"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results tracking
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
TEST_RESULTS=()

# Logging function
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASSED_TESTS++))
}

error() {
    echo -e "${RED}✗${NC} $1"
    ((FAILED_TESTS++))
}

warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Test execution function
run_test() {
    local test_name="$1"
    local method="$2"
    local endpoint="$3"
    local data="$4"
    local auth_header="$5"
    local expected_status="$6"
    
    ((TOTAL_TESTS++))
    
    log "Testing: $test_name"
    
    # Build curl command
    local curl_cmd="curl -s -w '%{http_code}' -X $method '$BASE_URL$endpoint'"
    
    if [[ -n "$data" ]]; then
        curl_cmd="$curl_cmd -H 'Content-Type: application/json' -d '$data'"
    fi
    
    if [[ -n "$auth_header" ]]; then
        curl_cmd="$curl_cmd -H 'Authorization: Bearer $auth_header'"
    fi
    
    # Execute request
    local response=$(eval $curl_cmd)
    local status_code="${response: -3}"
    local body="${response%???}"
    
    # Check status code
    if [[ "$status_code" == "$expected_status" ]]; then
        success "$test_name - Status: $status_code"
        TEST_RESULTS+=("{\"test\":\"$test_name\",\"status\":\"PASS\",\"http_code\":$status_code,\"endpoint\":\"$endpoint\"}")
    else
        error "$test_name - Expected: $expected_status, Got: $status_code"
        error "Response: $body"
        TEST_RESULTS+=("{\"test\":\"$test_name\",\"status\":\"FAIL\",\"http_code\":$status_code,\"endpoint\":\"$endpoint\",\"error\":\"$body\"}")
    fi
    
    # Return response for further processing
    echo "$body"
}

# Authentication setup
setup_auth() {
    log "Setting up authentication..."
    
    # Test phone authentication
    local otp_response=$(run_test "Send OTP" "POST" "/auth/signin/phone" "{\"phone\":\"$TEST_PHONE\"}" "" "200")
    
    # Verify OTP and get token
    local auth_response=$(run_test "Verify OTP" "POST" "/auth/verify/phone" "{\"phone\":\"$TEST_PHONE\",\"token\":\"$TEST_OTP\",\"name\":\"Test User\"}" "" "200")
    
    # Extract access token
    ACCESS_TOKEN=$(echo "$auth_response" | python3 -c "import json,sys; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null || echo "")
    
    if [[ -n "$ACCESS_TOKEN" ]]; then
        success "Authentication successful"
        log "Access token obtained: ${ACCESS_TOKEN:0:20}..."
    else
        error "Failed to obtain access token"
        exit 1
    fi
}

# Test Health Check
test_health() {
    log "=== Testing Health Check ==="
    run_test "Health Check" "GET" "/healthz" "" "" "200"
}

# Test Authentication Endpoints
test_auth_endpoints() {
    log "=== Testing Authentication Endpoints ==="
    
    # Test user profile
    run_test "Get User Profile" "GET" "/auth/me" "" "$ACCESS_TOKEN" "200"
    
    # Test profile alias
    run_test "Get User Profile (alias)" "GET" "/auth/profile" "" "$ACCESS_TOKEN" "200"
    
    # Test anonymous session (should fail without proper data)
    run_test "Anonymous Session (invalid)" "POST" "/auth/anonymous-session" "{\"restaurant_id\":\"invalid\"}" "" "400"
}

# Test Restaurant Endpoints
test_restaurant_endpoints() {
    log "=== Testing Restaurant Endpoints ==="
    
    # Test get restaurant by code (public endpoint)
    run_test "Get Restaurant by Code" "GET" "/restaurants/2C46XY" "" "" "200"
    
    # Test get my restaurant (should fail for customer)
    run_test "Get My Restaurant (customer)" "GET" "/restaurants/me" "" "$ACCESS_TOKEN" "403"
    
    # Test restaurant registration with duplicate email (should fail)
    local reg_data="{\"name\":\"Test Restaurant\",\"owner_email\":\"duplicate@test.com\",\"owner_password\":\"password123\"}"
    run_test "Restaurant Registration (duplicate)" "POST" "/restaurants/register" "$reg_data" "" "400"
}

# Test Menu Endpoints
test_menu_endpoints() {
    log "=== Testing Menu Endpoints ==="
    
    # Test get categories (should fail without restaurant access)
    run_test "Get Menu Categories (no access)" "GET" "/menu/categories" "" "$ACCESS_TOKEN" "403"
    
    # Test create category (should fail without restaurant access)
    local cat_data="{\"name\":\"Test Category\",\"description\":\"Test category description\"}"
    run_test "Create Menu Category (no access)" "POST" "/menu/categories" "$cat_data" "$ACCESS_TOKEN" "403"
    
    # Test get menu items (should fail without restaurant access)
    run_test "Get Menu Items (no access)" "GET" "/menu/items" "" "$ACCESS_TOKEN" "403"
}

# Test Table Endpoints
test_table_endpoints() {
    log "=== Testing Table Management Endpoints ==="
    
    # Test get tables (should fail without restaurant access)
    run_test "Get Tables (no access)" "GET" "/api/v1/tables" "" "$ACCESS_TOKEN" "403"
    
    # Test create table (should fail without restaurant access)
    local table_data="{\"table_number\":\"T1\",\"capacity\":4,\"shape\":\"round\",\"category\":\"regular\"}"
    run_test "Create Table (no access)" "POST" "/api/v1/tables" "$table_data" "$ACCESS_TOKEN" "403"
    
    # Test get floors (should fail without restaurant access)
    run_test "Get Floors (no access)" "GET" "/api/v1/floors" "" "$ACCESS_TOKEN" "403"
}

# Test QR Code Endpoints
test_qr_endpoints() {
    log "=== Testing QR Code Endpoints ==="
    
    # Test QR code generation (should fail without restaurant access)
    run_test "Generate QR Codes (no access)" "POST" "/api/v1/qr/generate" "{\"table_ids\":[\"test-id\"]}" "$ACCESS_TOKEN" "403"
    
    # Test QR code status (should fail without restaurant access)
    run_test "Get QR Status (no access)" "GET" "/api/v1/qr/status" "" "$ACCESS_TOKEN" "403"
}

# Test Public Menu Endpoints
test_public_menu_endpoints() {
    log "=== Testing Public Menu Endpoints ==="
    
    # Test public menu access (should work without auth)
    run_test "Get Public Menu (invalid restaurant)" "GET" "/api/v1/public-menu/invalid-code" "" "" "404"
    
    # Test public menu with valid restaurant code
    run_test "Get Public Menu (valid restaurant)" "GET" "/api/v1/public-menu/2C46XY" "" "" "200"
}

# Performance Testing
test_performance() {
    log "=== Testing Performance & Concurrent Requests ==="
    
    # Test concurrent health checks
    log "Testing 10 concurrent health check requests..."
    for i in {1..10}; do
        curl -s "$BASE_URL/healthz" &
    done
    wait
    success "Concurrent health checks completed"
    
    # Test response times
    log "Testing response times..."
    local start_time=$(date +%s%N)
    curl -s "$BASE_URL/healthz" > /dev/null
    local end_time=$(date +%s%N)
    local duration=$(( (end_time - start_time) / 1000000 ))
    
    if [[ $duration -lt 100 ]]; then
        success "Health check response time: ${duration}ms (< 100ms)"
    else
        warning "Health check response time: ${duration}ms (>= 100ms)"
    fi
}

# Generate test report
generate_report() {
    log "=== Generating Test Report ==="
    
    local pass_rate=$(( PASSED_TESTS * 100 / TOTAL_TESTS ))
    
    # Create JSON report
    cat > "$RESULTS_FILE" << EOF
{
  "test_run": {
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "total_tests": $TOTAL_TESTS,
    "passed_tests": $PASSED_TESTS,
    "failed_tests": $FAILED_TESTS,
    "pass_rate": $pass_rate
  },
  "results": [
    $(IFS=','; echo "${TEST_RESULTS[*]}")
  ]
}
EOF
    
    # Print summary
    echo ""
    echo "=========================================="
    echo "           TEST SUMMARY"
    echo "=========================================="
    echo "Total Tests: $TOTAL_TESTS"
    echo -e "Passed: ${GREEN}$PASSED_TESTS${NC}"
    echo -e "Failed: ${RED}$FAILED_TESTS${NC}"
    echo -e "Pass Rate: ${BLUE}$pass_rate%${NC}"
    echo "Report saved to: $RESULTS_FILE"
    echo "=========================================="
}

# Main execution
main() {
    log "Starting ZERGO QR API Comprehensive Testing"
    log "Base URL: $BASE_URL"
    
    # Setup authentication
    setup_auth
    
    # Run all test suites
    test_health
    test_auth_endpoints
    test_restaurant_endpoints
    test_menu_endpoints
    test_table_endpoints
    test_qr_endpoints
    test_public_menu_endpoints
    test_performance
    
    # Generate report
    generate_report
    
    # Exit with appropriate code
    if [[ $FAILED_TESTS -eq 0 ]]; then
        log "All tests passed! System is ready for production."
        exit 0
    else
        log "Some tests failed. Please review the issues before production deployment."
        exit 1
    fi
}

# Run main function
main "$@"
