# Cart Management System Implementation

## Overview

This document describes the complete implementation of the Cart Management system for the ZERGO QR restaurant management platform, following Story 3.2 specifications.

## Architecture

The cart management system follows Clean Architecture principles with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                       │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │   FastAPI       │  │   Pydantic      │                  │
│  │   Routers       │  │   Schemas       │                  │
│  └─────────────────┘  └─────────────────┘                  │
├─────────────────────────────────────────────────────────────┤
│                    Application Layer                        │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │   Use Cases     │  │      DTOs       │                  │
│  │   Services      │  │                 │                  │
│  └─────────────────┘  └─────────────────┘                  │
├─────────────────────────────────────────────────────────────┤
│                      Domain Layer                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │    Entities     │  │  Value Objects  │  │ Repository  │ │
│  │                 │  │                 │  │ Interfaces  │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                   Infrastructure Layer                      │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │   Supabase      │  │   Repository    │                  │
│  │   Integration   │  │ Implementations │                  │
│  └─────────────────┘  └─────────────────┘                  │
└─────────────────────────────────────────────────────────────┘
```

## Database Schema

### Cart Sessions Table
```sql
CREATE TABLE cart_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_token TEXT UNIQUE NOT NULL,
    session_type VARCHAR(20) NOT NULL CHECK (session_type IN ('anonymous', 'authenticated')),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    anonymous_session_id UUID REFERENCES anonymous_sessions(id) ON DELETE CASCADE,
    restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    table_id UUID REFERENCES tables(id) ON DELETE SET NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    last_activity_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true,
    item_count INTEGER DEFAULT 0 CHECK (item_count >= 0 AND item_count <= 50),
    total_amount DECIMAL(10,2) DEFAULT 0.00 CHECK (total_amount >= 0),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Cart Items Table
```sql
CREATE TABLE cart_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cart_session_id UUID NOT NULL REFERENCES cart_sessions(id) ON DELETE CASCADE,
    restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    menu_item_id UUID NOT NULL REFERENCES menu_items(id) ON DELETE CASCADE,
    item_name VARCHAR(255) NOT NULL,
    item_description TEXT,
    base_price DECIMAL(8,2) NOT NULL CHECK (base_price >= 0),
    quantity INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0),
    customizations JSONB DEFAULT '{}',
    special_instructions TEXT,
    unit_price DECIMAL(8,2) NOT NULL CHECK (unit_price >= 0),
    total_price DECIMAL(8,2) NOT NULL CHECK (total_price >= 0),
    is_available BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(cart_session_id, menu_item_id, customizations)
);
```

## Key Features Implemented

### 1. Hybrid Authentication Support
- **Anonymous Sessions**: 2-hour expiration, automatically extended with activity
- **Authenticated Sessions**: 24-hour expiration, linked to user accounts
- **Seamless Migration**: Transfer cart contents from anonymous to authenticated sessions

### 2. Cart Session Management
- Secure session token generation using cryptographic random bytes
- Session validation and expiration handling
- Activity-based session extension for anonymous users
- Multi-tenant isolation with Row Level Security (RLS)

### 3. Cart Item Operations
- Add items with customizations and special instructions
- Update item quantities and customizations
- Remove individual items or clear entire cart
- Automatic quantity combination for identical items
- 50-item cart capacity limit enforcement

### 4. Price Management
- Real-time price validation against current menu prices
- Customization-based pricing calculations
- Price change detection and notification
- Consistent pricing snapshots in cart items

### 5. Security Features
- Row Level Security (RLS) policies for multi-tenant data isolation
- Secure session token generation and validation
- Input validation and sanitization
- SQL injection prevention through parameterized queries

## API Endpoints

### Cart Session Management
```
POST   /api/v1/cart/sessions/anonymous          # Create anonymous session
POST   /api/v1/cart/sessions/authenticated      # Create authenticated session
GET    /api/v1/cart/sessions/{token}            # Get session details
POST   /api/v1/cart/sessions/{token}/extend     # Extend session activity
POST   /api/v1/cart/sessions/migrate            # Migrate anonymous to authenticated
```

### Cart Item Management
```
POST   /api/v1/cart/sessions/{token}/items      # Add item to cart
PUT    /api/v1/cart/items/{item_id}             # Update cart item
DELETE /api/v1/cart/items/{item_id}             # Remove cart item
GET    /api/v1/cart/sessions/{token}/items      # Get all cart items
DELETE /api/v1/cart/sessions/{token}/items      # Clear cart
```

### Cart Summary and Validation
```
GET    /api/v1/cart/sessions/{token}/summary    # Get cart summary with totals
POST   /api/v1/cart/sessions/{token}/validate-prices  # Validate all cart prices
POST   /api/v1/cart/validate-price              # Validate individual item price
```

## Domain Model

### Core Entities

#### CartSession
- Manages cart session lifecycle and metadata
- Supports both anonymous and authenticated users
- Handles session expiration and activity tracking
- Enforces cart capacity limits (50 items maximum)

#### CartItem
- Represents individual items in a cart
- Stores pricing snapshots for consistency
- Supports customizations and special instructions
- Maintains quantity and total price calculations

### Value Objects

#### Money
- Immutable monetary value representation
- Prevents negative amounts
- Supports arithmetic operations with validation

#### Quantity
- Represents item quantities with positive validation
- Supports arithmetic operations

#### CartSessionToken
- Secure session token with validation
- Minimum 16-character requirement for security

#### CustomizationOptions
- Flexible customization storage using key-value pairs
- Immutable with equality comparison support

## Use Cases

### Session Management Use Cases
- `CreateAnonymousCartSessionUseCase`: Creates anonymous cart sessions
- `CreateAuthenticatedCartSessionUseCase`: Creates authenticated cart sessions
- `GetCartSessionUseCase`: Retrieves and validates cart sessions
- `ExtendCartSessionActivityUseCase`: Extends session expiration
- `MigrateCartSessionUseCase`: Migrates anonymous to authenticated sessions

### Item Management Use Cases
- `AddCartItemUseCase`: Adds items to cart with validation
- `UpdateCartItemUseCase`: Updates item quantities and customizations
- `RemoveCartItemUseCase`: Removes items from cart
- `GetCartItemsUseCase`: Retrieves all cart items
- `ClearCartUseCase`: Removes all items from cart

### Summary and Validation Use Cases
- `GetCartSummaryUseCase`: Generates complete cart summary with totals
- `ValidateCartPricesUseCase`: Validates all cart item prices
- `ValidateMenuItemPriceUseCase`: Validates individual menu item prices

## Error Handling

### Domain Exceptions
- `CartSessionNotFoundError`: Session not found or invalid
- `CartSessionExpiredError`: Session has expired
- `CartItemNotFoundError`: Cart item not found
- `CartFullError`: Cart exceeds 50-item limit
- `CartMigrationError`: Migration operation failed
- `PriceValidationError`: Price validation failed
- `InvalidQuantityError`: Invalid quantity specified

### HTTP Error Mapping
- 400 Bad Request: Domain validation errors
- 401 Unauthorized: Expired sessions
- 404 Not Found: Missing sessions or items
- 422 Unprocessable Entity: Invalid request format
- 500 Internal Server Error: Unexpected errors

## Performance Characteristics

### Response Time Requirements
- All cart operations complete within 3 seconds
- Session creation: < 500ms
- Item operations: < 1 second
- Cart summary generation: < 2 seconds

### Scalability Features
- Database indexes on frequently queried columns
- Efficient RLS policies for multi-tenant isolation
- Automatic cleanup of expired sessions
- Connection pooling for database operations

### Concurrency Support
- Supports 100+ concurrent cart sessions
- Atomic operations for cart modifications
- Database-level consistency guarantees
- Optimistic locking for cart updates

## Testing Strategy

### Unit Tests
- Domain entity behavior validation
- Value object constraints and operations
- Use case business logic verification
- Error handling and edge cases

### Integration Tests
- Database operations and transactions
- Repository implementations
- Use case orchestration
- End-to-end workflows

### API Tests
- HTTP endpoint functionality
- Request/response validation
- Error handling and status codes
- Authentication and authorization

### Performance Tests
- Response time validation
- Concurrent operation handling
- Load testing with multiple sessions
- Database performance optimization

## Security Considerations

### Data Protection
- Row Level Security (RLS) for multi-tenant isolation
- Encrypted session tokens
- Input validation and sanitization
- SQL injection prevention

### Session Security
- Cryptographically secure token generation
- Session expiration and cleanup
- Activity-based session extension
- Secure session migration

### Access Control
- Anonymous session isolation
- Authenticated user session binding
- Restaurant-specific cart isolation
- Proper authorization checks

## Deployment and Operations

### Database Migrations
- Automated schema creation and updates
- Index creation for performance optimization
- RLS policy deployment
- Function and trigger installation

### Monitoring and Logging
- Structured logging with contextual information
- Performance metrics collection
- Error tracking and alerting
- Session activity monitoring

### Maintenance Operations
- Automated cleanup of expired sessions
- Database performance monitoring
- Index maintenance and optimization
- Backup and recovery procedures

## Future Enhancements

### Planned Features
- Real-time cart synchronization using WebSockets
- Advanced pricing rules and promotions
- Cart sharing between users
- Persistent cart storage for authenticated users
- Analytics and reporting capabilities

### Scalability Improvements
- Redis caching for session data
- Database sharding for large-scale deployments
- CDN integration for static assets
- Microservice decomposition for high-traffic scenarios
