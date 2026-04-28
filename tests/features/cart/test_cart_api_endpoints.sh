#!/bin/bash

# Cart Management API Endpoint Tests
# Comprehensive test suite for cart management functionality using cURL

set -e

BASE_URL="http://localhost:8000"
RESTAURANT_ID="5eebc804-81eb-4401-800c-6efd6f488de5"  # Using existing restaurant from menu tests
MENU_ITEM_ID="550e8400-e29b-41d4-a716-446655440000"  # Placeholder menu item ID

echo "🛒 CART MANAGEMENT API ENDPOINT TESTS"
echo "====================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test result tracking
TESTS_PASSED=0
TESTS_FAILED=0
TOTAL_TESTS=0

# Helper function to run test
run_test() {
    local test_name="$1"
    local curl_command="$2"
    local expected_status="$3"
    local description="$4"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    echo -e "${BLUE}Test $TOTAL_TESTS: $test_name${NC}"
    echo "Description: $description"
    echo "Command: $curl_command"
    
    # Execute curl command and capture response
    response=$(eval "$curl_command" 2>/dev/null)
    status_code=$(eval "$curl_command -w '%{http_code}' -o /dev/null -s" 2>/dev/null)
    
    if [ "$status_code" = "$expected_status" ]; then
        echo -e "${GREEN}✅ PASS${NC} - Status: $status_code"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        
        # Pretty print JSON response if it's JSON
        if echo "$response" | jq . >/dev/null 2>&1; then
            echo "Response:"
            echo "$response" | jq .
        else
            echo "Response: $response"
        fi
    else
        echo -e "${RED}❌ FAIL${NC} - Expected: $expected_status, Got: $status_code"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        echo "Response: $response"
    fi
    
    echo ""
}

# Test 1: Create Anonymous Cart Session
echo -e "${YELLOW}=== CART SESSION MANAGEMENT TESTS ===${NC}"
echo ""

ANONYMOUS_SESSION_ID=$(uuidgen)
run_test "Create Anonymous Cart Session" \
    "curl -s -X POST '$BASE_URL/api/v1/cart/sessions/anonymous' \
    -H 'Content-Type: application/json' \
    -d '{
        \"anonymous_session_id\": \"$ANONYMOUS_SESSION_ID\",
        \"restaurant_id\": \"$RESTAURANT_ID\"
    }'" \
    "200" \
    "Create a new anonymous cart session for a restaurant"

# Extract session token from response for subsequent tests
ANONYMOUS_SESSION_TOKEN=$(curl -s -X POST "$BASE_URL/api/v1/cart/sessions/anonymous" \
    -H "Content-Type: application/json" \
    -d "{
        \"anonymous_session_id\": \"$ANONYMOUS_SESSION_ID\",
        \"restaurant_id\": \"$RESTAURANT_ID\"
    }" | jq -r '.session_token' 2>/dev/null || echo "")

if [ -z "$ANONYMOUS_SESSION_TOKEN" ] || [ "$ANONYMOUS_SESSION_TOKEN" = "null" ]; then
    echo -e "${RED}⚠️  Warning: Could not extract session token. Some tests may fail.${NC}"
    ANONYMOUS_SESSION_TOKEN="dummy-token-for-testing"
fi

echo "Using session token: ${ANONYMOUS_SESSION_TOKEN:0:8}..."
echo ""

# Test 2: Get Cart Session
run_test "Get Cart Session" \
    "curl -s -X GET '$BASE_URL/api/v1/cart/sessions/$ANONYMOUS_SESSION_TOKEN'" \
    "200" \
    "Retrieve cart session details by token"

# Test 3: Extend Cart Session Activity
run_test "Extend Cart Session Activity" \
    "curl -s -X POST '$BASE_URL/api/v1/cart/sessions/$ANONYMOUS_SESSION_TOKEN/extend'" \
    "200" \
    "Extend anonymous cart session expiration time"

# Test 4: Get Cart Session with Invalid Token
run_test "Get Cart Session - Invalid Token" \
    "curl -s -X GET '$BASE_URL/api/v1/cart/sessions/invalid-token-123456789'" \
    "404" \
    "Attempt to get cart session with invalid token"

echo -e "${YELLOW}=== CART ITEM MANAGEMENT TESTS ===${NC}"
echo ""

# Test 5: Add Item to Cart
run_test "Add Item to Cart" \
    "curl -s -X POST '$BASE_URL/api/v1/cart/sessions/$ANONYMOUS_SESSION_TOKEN/items' \
    -H 'Content-Type: application/json' \
    -d '{
        \"menu_item_id\": \"$MENU_ITEM_ID\",
        \"quantity\": 2,
        \"customizations\": {\"size\": \"large\", \"extra_cheese\": true},
        \"special_instructions\": \"Extra spicy please\"
    }'" \
    "200" \
    "Add a menu item to the cart with customizations"

# Test 6: Add Same Item Again (Should combine quantities)
run_test "Add Same Item Again" \
    "curl -s -X POST '$BASE_URL/api/v1/cart/sessions/$ANONYMOUS_SESSION_TOKEN/items' \
    -H 'Content-Type: application/json' \
    -d '{
        \"menu_item_id\": \"$MENU_ITEM_ID\",
        \"quantity\": 1,
        \"customizations\": {\"size\": \"large\", \"extra_cheese\": true},
        \"special_instructions\": \"Extra spicy please\"
    }'" \
    "200" \
    "Add same item with identical customizations (should combine quantities)"

# Test 7: Add Different Item
MENU_ITEM_ID_2="550e8400-e29b-41d4-a716-446655440001"
run_test "Add Different Item" \
    "curl -s -X POST '$BASE_URL/api/v1/cart/sessions/$ANONYMOUS_SESSION_TOKEN/items' \
    -H 'Content-Type: application/json' \
    -d '{
        \"menu_item_id\": \"$MENU_ITEM_ID_2\",
        \"quantity\": 1,
        \"customizations\": {\"size\": \"medium\"},
        \"special_instructions\": \"No onions\"
    }'" \
    "200" \
    "Add a different menu item to the cart"

# Test 8: Get Cart Items
run_test "Get Cart Items" \
    "curl -s -X GET '$BASE_URL/api/v1/cart/sessions/$ANONYMOUS_SESSION_TOKEN/items'" \
    "200" \
    "Retrieve all items in the cart"

# Test 9: Add Item with Invalid Session Token
run_test "Add Item - Invalid Session" \
    "curl -s -X POST '$BASE_URL/api/v1/cart/sessions/invalid-token-123456789/items' \
    -H 'Content-Type: application/json' \
    -d '{
        \"menu_item_id\": \"$MENU_ITEM_ID\",
        \"quantity\": 1
    }'" \
    "404" \
    "Attempt to add item with invalid session token"

# Test 10: Add Item with Invalid Quantity
run_test "Add Item - Invalid Quantity" \
    "curl -s -X POST '$BASE_URL/api/v1/cart/sessions/$ANONYMOUS_SESSION_TOKEN/items' \
    -H 'Content-Type: application/json' \
    -d '{
        \"menu_item_id\": \"$MENU_ITEM_ID\",
        \"quantity\": 0
    }'" \
    "422" \
    "Attempt to add item with invalid quantity (0)"

# Test 11: Add Item with Excessive Quantity
run_test "Add Item - Excessive Quantity" \
    "curl -s -X POST '$BASE_URL/api/v1/cart/sessions/$ANONYMOUS_SESSION_TOKEN/items' \
    -H 'Content-Type: application/json' \
    -d '{
        \"menu_item_id\": \"$MENU_ITEM_ID\",
        \"quantity\": 51
    }'" \
    "422" \
    "Attempt to add item with excessive quantity (>50)"

echo -e "${YELLOW}=== CART SUMMARY AND VALIDATION TESTS ===${NC}"
echo ""

# Test 12: Get Cart Summary
run_test "Get Cart Summary" \
    "curl -s -X GET '$BASE_URL/api/v1/cart/sessions/$ANONYMOUS_SESSION_TOKEN/summary'" \
    "200" \
    "Get complete cart summary with totals and tax calculation"

# Test 13: Validate Cart Prices
run_test "Validate Cart Prices" \
    "curl -s -X POST '$BASE_URL/api/v1/cart/sessions/$ANONYMOUS_SESSION_TOKEN/validate-prices'" \
    "200" \
    "Validate all cart item prices against current menu prices"

# Test 14: Validate Individual Menu Item Price
run_test "Validate Menu Item Price" \
    "curl -s -X POST '$BASE_URL/api/v1/cart/validate-price' \
    -H 'Content-Type: application/json' \
    -d '{
        \"menu_item_id\": \"$MENU_ITEM_ID\",
        \"expected_base_price\": 10.00,
        \"customizations\": {\"size\": \"large\"}
    }'" \
    "200" \
    "Validate individual menu item price with customizations"

echo -e "${YELLOW}=== CART CLEANUP TESTS ===${NC}"
echo ""

# Test 15: Clear Cart
run_test "Clear Cart" \
    "curl -s -X DELETE '$BASE_URL/api/v1/cart/sessions/$ANONYMOUS_SESSION_TOKEN/items'" \
    "200" \
    "Clear all items from the cart"

# Test 16: Get Cart Items After Clear
run_test "Get Cart Items After Clear" \
    "curl -s -X GET '$BASE_URL/api/v1/cart/sessions/$ANONYMOUS_SESSION_TOKEN/items'" \
    "200" \
    "Verify cart is empty after clearing"

echo -e "${YELLOW}=== AUTHENTICATION AND MIGRATION TESTS ===${NC}"
echo ""

# Test 17: Create Authenticated Cart Session (will fail without proper auth)
run_test "Create Authenticated Cart Session" \
    "curl -s -X POST '$BASE_URL/api/v1/cart/sessions/authenticated' \
    -H 'Content-Type: application/json' \
    -H 'Authorization: Bearer dummy-token' \
    -d '{
        \"restaurant_id\": \"$RESTAURANT_ID\"
    }'" \
    "401" \
    "Attempt to create authenticated session without proper authentication"

# Test 18: Migrate Cart Session (will fail without proper auth)
run_test "Migrate Cart Session" \
    "curl -s -X POST '$BASE_URL/api/v1/cart/sessions/migrate' \
    -H 'Content-Type: application/json' \
    -H 'Authorization: Bearer dummy-token' \
    -d '{
        \"anonymous_session_token\": \"$ANONYMOUS_SESSION_TOKEN\",
        \"restaurant_id\": \"$RESTAURANT_ID\"
    }'" \
    "401" \
    "Attempt to migrate anonymous cart to authenticated without proper authentication"

echo -e "${YELLOW}=== ERROR HANDLING TESTS ===${NC}"
echo ""

# Test 19: Invalid JSON Request
run_test "Invalid JSON Request" \
    "curl -s -X POST '$BASE_URL/api/v1/cart/sessions/anonymous' \
    -H 'Content-Type: application/json' \
    -d 'invalid-json'" \
    "422" \
    "Send invalid JSON in request body"

# Test 20: Missing Required Fields
run_test "Missing Required Fields" \
    "curl -s -X POST '$BASE_URL/api/v1/cart/sessions/anonymous' \
    -H 'Content-Type: application/json' \
    -d '{}'" \
    "422" \
    "Send request with missing required fields"

echo ""
echo "====================================="
echo -e "${BLUE}CART MANAGEMENT API TEST SUMMARY${NC}"
echo "====================================="
echo -e "Total Tests: $TOTAL_TESTS"
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Failed: $TESTS_FAILED${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed. Please review the output above.${NC}"
    exit 1
fi
