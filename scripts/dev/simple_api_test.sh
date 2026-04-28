#!/bin/bash

# Simple API Testing Script for ZERGO QR
set -e

BASE_URL="http://localhost:8000"
ACCESS_TOKEN="eyJhbGciOiJIUzI1NiIsImtpZCI6Im1xNHhCS3JNY21lZEVVOHgiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2twc3l6c21nenV3ZWFkcG5mZnd5LnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiIxZmZjN2YzNy1kNzljLTQzNzAtYWU0OS0wNTgxNDY2MzQwNzUiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzU5MDQ5NjI5LCJpYXQiOjE3NTkwNDYwMjksImVtYWlsIjoiIiwicGhvbmUiOiI5MTc0ODQ5MDYwMTAiLCJhcHBfbWV0YWRhdGEiOnsicHJvdmlkZXIiOiJwaG9uZSIsInByb3ZpZGVycyI6WyJwaG9uZSJdfSwidXNlcl9tZXRhZGF0YSI6eyJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsIm5hbWUiOiJzdHJpbmciLCJwaG9uZV92ZXJpZmllZCI6ZmFsc2UsInN1YiI6IjFmZmM3ZjM3LWQ3OWMtNDc3MC1hZTQ5LTA1ODE0NjYzNDA3NSJ9LCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImFhbCI6ImFhbDEiLCJhbXIiOlt7Im1ldGhvZCI6Im90cCIsInRpbWVzdGFtcCI6MTc1OTA0NjAyOX1dLCJzZXNzaW9uX2lkIjoiZTk3YzFjMWMtMjU4OC00YzkxLWE3ZTItMDVjODA0ZGI0NDgxIiwiaXNfYW5vbnltb3VzIjpmYWxzZX0.raxggcLmQo5oan8pl_XEFnzAiAjRs1Vs1PIIww9M4-c"

echo "=== ZERGO QR API Testing ==="
echo "Base URL: $BASE_URL"
echo ""

# Test 1: Health Check
echo "1. Testing Health Check..."
curl -s "$BASE_URL/healthz" | python3 -m json.tool
echo ""

# Test 2: User Profile
echo "2. Testing User Profile..."
curl -s -H "Authorization: Bearer $ACCESS_TOKEN" "$BASE_URL/auth/me" | python3 -m json.tool
echo ""

# Test 3: Restaurant by Code (Public)
echo "3. Testing Get Restaurant by Code (Public)..."
curl -s "$BASE_URL/restaurants/2C46XY" | python3 -m json.tool
echo ""

# Test 4: Public Menu Access
echo "4. Testing Public Menu Access..."
curl -s "$BASE_URL/api/v1/public-menu/2C46XY" | python3 -m json.tool
echo ""

# Test 5: Menu Categories (should fail - no restaurant access)
echo "5. Testing Menu Categories (should fail)..."
curl -s -H "Authorization: Bearer $ACCESS_TOKEN" "$BASE_URL/menu/categories" | python3 -m json.tool
echo ""

# Test 6: Tables (should fail - no restaurant access)
echo "6. Testing Tables (should fail)..."
curl -s -H "Authorization: Bearer $ACCESS_TOKEN" "$BASE_URL/api/v1/tables" | python3 -m json.tool
echo ""

# Test 7: QR Status (should fail - no restaurant access)
echo "7. Testing QR Status (should fail)..."
curl -s -H "Authorization: Bearer $ACCESS_TOKEN" "$BASE_URL/api/v1/qr/status" | python3 -m json.tool
echo ""

# Test 8: Anonymous Session Creation
echo "8. Testing Anonymous Session Creation..."
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"restaurant_id":"5eebc804-81eb-4401-800c-6efd6f488de5"}' \
  "$BASE_URL/auth/anonymous-session" | python3 -m json.tool
echo ""

# Test 9: Performance Test - Multiple concurrent requests
echo "9. Testing Performance - 5 concurrent health checks..."
start_time=$(date +%s%N)
for i in {1..5}; do
  curl -s "$BASE_URL/healthz" > /dev/null &
done
wait
end_time=$(date +%s%N)
duration=$(( (end_time - start_time) / 1000000 ))
echo "Concurrent requests completed in ${duration}ms"
echo ""

echo "=== Testing Complete ==="
