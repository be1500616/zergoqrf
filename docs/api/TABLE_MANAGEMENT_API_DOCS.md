# Table Management API Documentation

## Overview

The Table Management API provides comprehensive endpoints for managing restaurant tables, floors, and occupancy tracking. All endpoints require authentication and are scoped to the authenticated user's restaurant.

## Base URL
```
http://localhost:8000/api/v1/tables
```

## Authentication
All endpoints require a valid JWT token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

## Floor Management Endpoints

### Create Floor
**POST** `/floors`

Create a new floor for the restaurant.

**Request Body:**
```json
{
  "name": "Ground Floor",
  "description": "Main dining area",
  "floor_number": 1,
  "layout_config": {
    "width": 800,
    "height": 600,
    "grid_size": 16
  }
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "restaurant_id": "uuid",
  "name": "Ground Floor",
  "description": "Main dining area",
  "floor_number": 1,
  "is_active": true,
  "layout_config": {...},
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### List Floors
**GET** `/floors`

Get all floors for the restaurant.

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "restaurant_id": "uuid",
    "name": "Ground Floor",
    "floor_number": 1,
    "is_active": true,
    ...
  }
]
```

### Get Floor Plan
**GET** `/floors/{floor_id}/plan`

Get complete floor plan with tables and occupancy statistics.

**Response:** `200 OK`
```json
{
  "floor": {
    "id": "uuid",
    "name": "Ground Floor",
    ...
  },
  "tables": [
    {
      "id": "uuid",
      "table_number": "T001",
      "status": "available",
      "position": {"x": 100, "y": 100},
      ...
    }
  ],
  "occupancy_stats": {
    "total_tables": 10,
    "available_tables": 7,
    "occupied_tables": 2,
    "reserved_tables": 1,
    "occupancy_rate": 30.0
  }
}
```

## Table Management Endpoints

### Create Table
**POST** `/`

Create a new table.

**Request Body:**
```json
{
  "floor_id": "uuid",
  "table_number": "T001",
  "capacity": 4,
  "shape": "round",
  "category": "regular",
  "position": {"x": 100, "y": 100},
  "dimensions": {"width": 80, "height": 80},
  "rotation": 0.0,
  "is_accessible": false,
  "has_power_outlet": false,
  "has_window_view": true,
  "min_party_size": 1,
  "max_party_size": 4,
  "notes": "Window table"
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "restaurant_id": "uuid",
  "table_number": "T001",
  "capacity": 4,
  "status": "available",
  "qr_code_data": {
    "token": "unique-token",
    "url": "qr-code-url",
    "data": {...}
  },
  ...
}
```

### List Tables
**GET** `/`

Get tables with optional filters.

**Query Parameters:**
- `floor_id` (optional): Filter by floor ID
- `status` (optional): Filter by table status
- `party_size` (optional): Filter available tables for party size

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "table_number": "T001",
    "capacity": 4,
    "status": "available",
    ...
  }
]
```

### Get Table
**GET** `/{table_id}`

Get table details by ID.

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "table_number": "T001",
  "capacity": 4,
  "status": "available",
  "position": {"x": 100, "y": 100},
  "qr_code_data": {...},
  ...
}
```

### Update Table Status
**PATCH** `/{table_id}/status`

Update table status.

**Request Body:**
```json
{
  "status": "occupied"
}
```

**Response:** `200 OK`
```json
{
  "message": "Table status updated successfully"
}
```

### Get Occupancy Statistics
**GET** `/stats`

Get restaurant occupancy statistics.

**Response:** `200 OK`
```json
{
  "total_tables": 20,
  "available_tables": 15,
  "occupied_tables": 3,
  "reserved_tables": 2,
  "cleaning_tables": 0,
  "maintenance_tables": 0,
  "occupancy_rate": 25.0
}
```

## Data Models

### Table Status Values
- `available` - Table is ready for seating
- `occupied` - Table is currently occupied
- `reserved` - Table has a reservation
- `cleaning` - Table is being cleaned
- `maintenance` - Table is under maintenance
- `out_of_order` - Table is out of service

### Table Shapes
- `round` - Round table
- `square` - Square table
- `rectangular` - Rectangular table
- `oval` - Oval table

### Table Categories
- `regular` - Standard dining table
- `vip` - VIP/premium table
- `outdoor` - Outdoor seating
- `bar` - Bar seating
- `counter` - Counter seating
- `booth` - Booth seating

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Validation error message"
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication required"
}
```

### 403 Forbidden
```json
{
  "detail": "Access denied"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Testing

Use the provided test script to validate API functionality:

```bash
cd apps/backend
python test_table_management_api.py
```

## Interactive Documentation

When the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
