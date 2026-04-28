# Authentication Endpoints - cURL Examples

This document provides ready-to-use cURL commands for testing all authentication endpoints.

## Prerequisites

- Server running on `http://127.0.0.1:8000`
- Valid test credentials (see below)

## Test Credentials

```bash
# Email Authentication
EMAIL_1="test@gmail.com"
PASSWORD_1="test1234"

EMAIL_2="customer@gmail.com"
PASSWORD_2="customer1234"

# Phone Authentication
PHONE="+917484999999"
OTP="123456"  # Test OTP (use real OTP from SMS in production)

# Test Restaurant ID (replace with valid ID from your database)
RESTAURANT_ID="550e8400-e29b-41d4-a716-446655440000"
```

## 1. Health Check

```bash
curl -X GET http://127.0.0.1:8000/healthz
```

**Expected Response**:
```json
{"status":"ok"}
```

## 2. Email Sign Up

```bash
curl -X POST http://127.0.0.1:8000/auth/signup/email \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@gmail.com",
    "password": "test1234",
    "name": "Test User",
    "role": "customer"
  }'
```

**Expected Response** (Success):
```json
{
  "access_token": "eyJhbGci...",
  "refresh_token": "...",
  "user": {
    "id": "...",
    "email": "test@gmail.com",
    "name": "Test User",
    "role": "customer"
  }
}
```

## 3. Email Sign In

```bash
curl -X POST http://127.0.0.1:8000/auth/signin/email \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@gmail.com",
    "password": "test1234"
  }'
```

**Expected Response**:
```json
{
  "access_token": "eyJhbGci...",
  "refresh_token": "...",
  "user": {
    "id": "563e9b99-55c8-4fa0-ac3d-1df02e202ae0",
    "email": "test@gmail.com",
    "name": "Test User",
    "role": "owner"
  }
}
```

**Save the tokens for subsequent requests**:
```bash
ACCESS_TOKEN="<paste_access_token_here>"
REFRESH_TOKEN="<paste_refresh_token_here>"
```

## 4. Phone Sign In (OTP Initiation)

```bash
curl -X POST http://127.0.0.1:8000/auth/signin/phone \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+917484999999"
  }'
```

**Expected Response**:
```json
{
  "message": "OTP sent successfully",
  "phone": "+917484999999"
}
```

## 5. Phone OTP Verification

```bash
# Use the OTP received via SMS
curl -X POST http://127.0.0.1:8000/auth/verify/phone \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+917484999999",
    "token": "123456",
    "name": "Phone Test User"
  }'
```

**Expected Response**:
```json
{
  "access_token": "eyJhbGci...",
  "refresh_token": "...",
  "user": {
    "id": "...",
    "phone": "+917484999999",
    "name": "Phone Test User"
  }
}
```

## 6. Anonymous Session Creation

```bash
# Replace RESTAURANT_ID with a valid restaurant ID from your database
curl -X POST http://127.0.0.1:8000/auth/anonymous-session \
  -H "Content-Type: application/json" \
  -d '{
    "restaurant_id": "550e8400-e29b-41d4-a716-446655440000",
    "table_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

**Expected Response**:
```json
{
  "session_token": "...",
  "restaurant_id": "550e8400-e29b-41d4-a716-446655440000",
  "table_id": "550e8400-e29b-41d4-a716-446655440000",
  "expires_at": "2025-10-08T18:13:10.738124"
}
```

## 7. Token Refresh

```bash
# Use the refresh_token from sign in
curl -X POST http://127.0.0.1:8000/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "<paste_refresh_token_here>"
  }'
```

**Expected Response**:
```json
{
  "access_token": "eyJhbGci...",
  "refresh_token": "...",
  "user": {
    "id": "563e9b99-55c8-4fa0-ac3d-1df02e202ae0",
    "email": "test@gmail.com"
  }
}
```

## 8. Get Current User Profile

```bash
# Use the access_token from sign in
curl -X GET http://127.0.0.1:8000/auth/me \
  -H "Authorization: Bearer <paste_access_token_here>"
```

**Expected Response**:
```json
{
  "id": "563e9b99-55c8-4fa0-ac3d-1df02e202ae0",
  "email": "test@gmail.com",
  "name": "Test User",
  "role": "owner",
  "restaurant_id": "c6f0476b-8576-43ac-a9ac-0dd2b9b92c03"
}
```

## 9. Sign Out

```bash
# Use the access_token from sign in
curl -X POST http://127.0.0.1:8000/auth/signout \
  -H "Authorization: Bearer <paste_access_token_here>"
```

**Expected Response**:
```json
{
  "message": "Successfully signed out"
}
```

## Complete Test Flow Example

Here's a complete flow testing email authentication:

```bash
# 1. Health check
echo "=== Health Check ==="
curl -s http://127.0.0.1:8000/healthz | jq

# 2. Sign in
echo -e "\n=== Sign In ==="
RESPONSE=$(curl -s -X POST http://127.0.0.1:8000/auth/signin/email \
  -H "Content-Type: application/json" \
  -d '{"email": "test@gmail.com", "password": "test1234"}')

echo $RESPONSE | jq

# 3. Extract tokens
ACCESS_TOKEN=$(echo $RESPONSE | jq -r '.access_token')
REFRESH_TOKEN=$(echo $RESPONSE | jq -r '.refresh_token')

echo "Access Token: ${ACCESS_TOKEN:0:50}..."
echo "Refresh Token: ${REFRESH_TOKEN:0:50}..."

# 4. Get current user
echo -e "\n=== Get Current User ==="
curl -s -X GET http://127.0.0.1:8000/auth/me \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq

# 5. Refresh token
echo -e "\n=== Refresh Token ==="
NEW_RESPONSE=$(curl -s -X POST http://127.0.0.1:8000/auth/refresh \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}")

echo $NEW_RESPONSE | jq

# 6. Extract new access token
NEW_ACCESS_TOKEN=$(echo $NEW_RESPONSE | jq -r '.access_token')
echo "New Access Token: ${NEW_ACCESS_TOKEN:0:50}..."

# 7. Sign out
echo -e "\n=== Sign Out ==="
curl -s -X POST http://127.0.0.1:8000/auth/signout \
  -H "Authorization: Bearer $NEW_ACCESS_TOKEN" | jq
```

## Error Testing

### Test Invalid Credentials

```bash
curl -X POST http://127.0.0.1:8000/auth/signin/email \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@gmail.com",
    "password": "wrongpassword"
  }'
```

**Expected**: 401 Unauthorized (currently returns 500)

### Test Duplicate Sign Up

```bash
curl -X POST http://127.0.0.1:8000/auth/signup/email \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@gmail.com",
    "password": "test1234",
    "name": "Test User"
  }'
```

**Expected**: 409 Conflict (currently returns 500)

### Test Invalid OTP

```bash
curl -X POST http://127.0.0.1:8000/auth/verify/phone \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+917484999999",
    "token": "000000",
    "name": "Test"
  }'
```

**Expected**: 401 Unauthorized (currently returns 500)

## Notes

1. **jq**: The examples use `jq` for JSON formatting. Install with `brew install jq` (macOS) or `apt-get install jq` (Linux).

2. **Access Tokens**: Access tokens expire after 1 hour. Use the refresh token to get a new access token.

3. **Refresh Tokens**: Refresh tokens are long-lived but should be stored securely.

4. **Phone OTP**: The test OTP (123456) won't work in production. Use the actual OTP received via SMS.

5. **Restaurant IDs**: Replace the test restaurant ID with a valid ID from your database.

6. **CORS**: If testing from a browser, ensure CORS is properly configured.

## Troubleshooting

### Connection Refused
```bash
curl: (7) Failed to connect to 127.0.0.1 port 8000: Connection refused
```
**Solution**: Start the FastAPI server:
```bash
cd apps/backend
source venv/bin/activate
uvicorn app.main:app --reload
```

### 404 Not Found
```bash
{"detail":"Not Found"}
```
**Solution**: Check the endpoint path. All auth endpoints should start with `/auth/`.

### 500 Internal Server Error
**Solution**: Check server logs for detailed error messages:
```bash
tail -f /tmp/fastapi_server.log
```

## API Documentation

For interactive API documentation, visit:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

