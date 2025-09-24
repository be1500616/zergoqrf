# Data Models

## Restaurant

**Purpose:** Core entity representing restaurant establishments with multi-tenant data isolation

**Key Attributes:**

- id: UUID - Primary restaurant identifier
- name: String - Restaurant display name
- slug: String - URL-friendly identifier for QR links
- businessHours: JSON - Operating hours configuration
- settings: JSON - Restaurant-specific configuration

**TypeScript Interface:**

```typescript
interface Restaurant {
  id: string;
  name: string;
  slug: string;
  businessHours: {
    [day: string]: { open: string; close: string; closed: boolean };
  };
  settings: {
    tableTurnoverTime: number;
    maxOrdersPerHour: number;
    paymentMethods: string[];
    whatsappNotifications: boolean;
  };
  createdAt: string;
  updatedAt: string;
}
```

**Relationships:**

- Has many Tables (1:N)
- Has many Orders (1:N)
- Has many Staff (1:N)
- Has one Menu (1:1)

## Table

**Purpose:** Physical table representation with QR code management and capacity tracking

**Key Attributes:**

- id: UUID - Unique table identifier
- restaurantId: UUID - Foreign key to restaurant
- tableNumber: String - Display number for staff
- capacity: Number - Maximum seating capacity
- qrToken: String - Encrypted access token

**TypeScript Interface:**

```typescript
interface Table {
  id: string;
  restaurantId: string;
  tableNumber: string;
  capacity: number;
  qrToken: string;
  position: { x: number; y: number };
  status: "available" | "occupied" | "reserved" | "cleaning";
  currentOrder?: string;
  createdAt: string;
  updatedAt: string;
}
```

**Relationships:**

- Belongs to Restaurant (N:1)
- Has many Orders (1:N)
- Has many QR Scan Events (1:N)

## Order

**Purpose:** Customer order tracking with payment integration and status management

**Key Attributes:**

- id: UUID - Unique order identifier
- restaurantId: UUID - Multi-tenant isolation
- tableId: UUID - Table association
- customerId: UUID - Customer reference
- items: JSON - Ordered items with customizations
- status: Enum - Order lifecycle status
- paymentStatus: Enum - Payment processing status

**TypeScript Interface:**

```typescript
interface Order {
  id: string;
  restaurantId: string;
  tableId: string;
  customerId: string;
  items: OrderItem[];
  totalAmount: number;
  status:
    | "pending"
    | "confirmed"
    | "preparing"
    | "ready"
    | "completed"
    | "cancelled";
  paymentStatus: "pending" | "processing" | "completed" | "failed" | "refunded";
  specialInstructions?: string;
  estimatedPrepTime: number;
  createdAt: string;
  updatedAt: string;
}

interface OrderItem {
  menuItemId: string;
  name: string;
  quantity: number;
  unitPrice: number;
  customizations: { [key: string]: any };
  totalPrice: number;
}
```

**Relationships:**

- Belongs to Restaurant (N:1)
- Belongs to Table (N:1)
- Belongs to Customer (N:1)
- Has many Payment Transactions (1:N)

## Menu

**Purpose:** Restaurant menu management with real-time updates and version control

**Key Attributes:**

- id: UUID - Menu identifier
- restaurantId: UUID - Restaurant association
- categories: JSON - Menu categories with items
- version: String - Version tracking for cache invalidation
- isActive: Boolean - Menu availability status

**TypeScript Interface:**

```typescript
interface Menu {
  id: string;
  restaurantId: string;
  categories: MenuCategory[];
  version: string;
  isActive: boolean;
  publishedAt?: string;
  createdAt: string;
  updatedAt: string;
}

interface MenuCategory {
  id: string;
  name: string;
  description?: string;
  items: MenuItem[];
  displayOrder: number;
}

interface MenuItem {
  id: string;
  name: string;
  description: string;
  price: number;
  imageUrl?: string;
  isAvailable: boolean;
  dietaryInfo: string[];
  customizations: MenuCustomization[];
}

interface MenuCustomization {
  id: string;
  name: string;
  type: "single" | "multiple";
  required: boolean;
  options: { name: string; price: number }[];
}
```

**Relationships:**

- Belongs to Restaurant (N:1)
- Has many Menu Items (1:N)
