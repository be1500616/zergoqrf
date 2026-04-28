# Test Plan: Restaurant API

**Objective:** To ensure all restaurant-related endpoints are functioning as expected and to verify data integrity with the Supabase database.

## 1. Scope

This test plan covers the following endpoints:

- `POST /register`: Register a new restaurant and owner.
- `GET /me`: Get the current user's restaurant information.
- `PUT /me`: Update the current user's restaurant information.
- `PUT /me/business-hours`: Update the restaurant's business hours.
- `PUT /me/settings`: Update the restaurant's settings.
- `GET /{restaurant_code}`: Get restaurant information by its code.
- `POST /me/staff`: Create a new staff member.
- `GET /me/staff`: Get all staff members for the restaurant.
- `PUT /me/staff/{staff_id}`: Update a staff member.
- `DELETE /me/staff/{staff_id}`: Delete a staff member.

## 2. Test Strategy

### 2.1. Authentication and Authorization

- Verify that all endpoints requiring authentication return a `401 Unauthorized` error when no token is provided.
- Test role-based access control for staff management endpoints, ensuring only authorized users (owners, managers) can perform create, update, and delete operations.

### 2.2. Input Validation

- Test all endpoints with both valid and invalid data to ensure proper input validation and error handling. This includes testing for required fields, data types, and format constraints.

### 2.3. Business Logic

- **Restaurant Registration:**
  - Verify that a new restaurant, owner, and staff record are created in a single transaction.
  - Ensure that the response includes the restaurant and owner details, along with authentication tokens.
- **Data Integrity:**
  - Cross-reference the API responses with the Supabase database to ensure that all create, update, and delete operations are correctly reflected.
- **Error Handling:**
  - Test for graceful error handling for scenarios such as duplicate entries, invalid references, and server-side exceptions.

## 3. Test Cases

### 3.1. `POST /register`

- **Positive:**
  - Register a new restaurant with valid data.
- **Negative:**
  - Attempt to register with a duplicate email.
  - Register with missing required fields.

### 3.2. `GET /me`

- **Positive:**
  - Retrieve the restaurant information for an authenticated user.
- **Negative:**
  - Attempt to retrieve information without authentication.

### 3.3. `PUT /me`

- **Positive:**
  - Update the restaurant's name, description, and other fields.
- **Negative:**
  - Attempt to update with invalid data types.

### 3.4. Staff Management (`/me/staff`)

- **Positive:**
  - Create, update, and delete staff members with an authorized account.
- **Negative:**
  - Attempt to create a staff member with a non-manager account.
  - Attempt to delete a staff member with a non-owner account.

## 4. Test Environment

- **API:** Local instance of the FastAPI application.
- **Database:** Development instance of the Supabase database.

## 5. Reporting

- A final report will be generated summarizing the test results, including any identified defects or discrepancies.