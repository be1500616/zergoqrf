-- Fix Diner Schema Migration
-- This migration establishes proper database foundation for diner ordering flow
-- Addresses: Missing menu_categories table, incompatible menu_items schema, missing restaurant branding fields

BEGIN;

-- ============================================================================
-- STEP 1: Drop Incompatible Tables
-- ============================================================================

-- Drop old menu_items table that references non-existent menu_id
-- CASCADE will handle foreign key constraints from cart_items and order_items
DROP TABLE IF EXISTS menu_items CASCADE;

-- Drop old menus table (JSONB-based design, replaced by normalized approach)
DROP TABLE IF EXISTS menus CASCADE;

-- ============================================================================
-- STEP 2: Create Menu Categories Table
-- ============================================================================

CREATE TABLE menu_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    image_url TEXT,
    sort_order INTEGER NOT NULL DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_menu_categories_restaurant_id ON menu_categories(restaurant_id);
CREATE INDEX idx_menu_categories_sort_order ON menu_categories(restaurant_id, sort_order);
CREATE INDEX idx_menu_categories_active ON menu_categories(restaurant_id, is_active);

-- ============================================================================
-- STEP 3: Create Enhanced Menu Items Table
-- ============================================================================

CREATE TABLE menu_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    category_id UUID NOT NULL REFERENCES menu_categories(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    base_price DECIMAL(10,2) NOT NULL CHECK (base_price > 0),
    image_url TEXT,
    gallery_images TEXT[] DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'available' CHECK (status IN ('available', 'unavailable', 'featured')),
    dietary_indicators TEXT[] DEFAULT '{}',
    allergen_info TEXT[] DEFAULT '{}',
    preparation_time INTEGER,
    sort_order INTEGER NOT NULL DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_menu_items_restaurant_id ON menu_items(restaurant_id);
CREATE INDEX idx_menu_items_category_id ON menu_items(category_id);
CREATE INDEX idx_menu_items_status ON menu_items(restaurant_id, status);
CREATE INDEX idx_menu_items_active ON menu_items(restaurant_id, is_active);
CREATE INDEX idx_menu_items_sort_order ON menu_items(category_id, sort_order);

-- ============================================================================
-- STEP 4: Add Branding Columns to Restaurants Table
-- ============================================================================

ALTER TABLE restaurants ADD COLUMN IF NOT EXISTS logo_url TEXT;
ALTER TABLE restaurants ADD COLUMN IF NOT EXISTS primary_color VARCHAR(7) DEFAULT '#FF6B35';
ALTER TABLE restaurants ADD COLUMN IF NOT EXISTS secondary_color VARCHAR(7) DEFAULT '#2C3E50';
ALTER TABLE restaurants ADD COLUMN IF NOT EXISTS accent_color VARCHAR(7) DEFAULT '#F39C12';
ALTER TABLE restaurants ADD COLUMN IF NOT EXISTS operating_hours JSONB;
ALTER TABLE restaurants ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true;

-- ============================================================================
-- STEP 5: RLS Policies for Public Menu Access
-- ============================================================================

-- Enable RLS on new tables
ALTER TABLE menu_categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE menu_items ENABLE ROW LEVEL SECURITY;

-- Public read access for menu categories (anonymous users can browse)
CREATE POLICY "menu_categories_public_select" ON menu_categories
    FOR SELECT USING (is_active = true);

-- Public read access for menu items (anonymous users can browse)
CREATE POLICY "menu_items_public_select" ON menu_items
    FOR SELECT USING (is_active = true);

-- Staff can manage menu categories
CREATE POLICY "menu_categories_staff_all" ON menu_categories
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM restaurant_staff
            WHERE restaurant_staff.restaurant_id = menu_categories.restaurant_id
            AND restaurant_staff.user_id = auth.uid()
            AND restaurant_staff.is_active = true
        )
    );

-- Staff can manage menu items
CREATE POLICY "menu_items_staff_all" ON menu_items
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM restaurant_staff
            WHERE restaurant_staff.restaurant_id = menu_items.restaurant_id
            AND restaurant_staff.user_id = auth.uid()
            AND restaurant_staff.is_active = true
        )
    );

-- ============================================================================
-- STEP 6: Insert Test Data - Restaurant 1 (The Spice Route)
-- ============================================================================

-- Insert or update restaurant 1
INSERT INTO restaurants (id, name, code, description, cuisine_type, phone, address, logo_url, primary_color, secondary_color, accent_color, is_active)
VALUES (
    'a0000000-0000-0000-0000-000000000001'::uuid,
    'The Spice Route',
    'SPICE001',
    'Authentic Indian cuisine with a modern twist',
    'Indian',
    '+91-9876543210',
    '123 MG Road, Bangalore, Karnataka 560001',
    'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=400',
    '#FF6B35',
    '#2C3E50',
    '#F39C12',
    true
)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    code = EXCLUDED.code,
    description = EXCLUDED.description,
    cuisine_type = EXCLUDED.cuisine_type,
    phone = EXCLUDED.phone,
    address = EXCLUDED.address,
    logo_url = EXCLUDED.logo_url,
    primary_color = EXCLUDED.primary_color,
    secondary_color = EXCLUDED.secondary_color,
    accent_color = EXCLUDED.accent_color,
    is_active = EXCLUDED.is_active;

-- Insert categories for Restaurant 1
INSERT INTO menu_categories (id, restaurant_id, name, description, sort_order, is_active) VALUES
('c1000000-0000-0000-0000-000000000001'::uuid, 'a0000000-0000-0000-0000-000000000001'::uuid, 'Appetizers', 'Start your meal with our delicious starters', 1, true),
('c1000000-0000-0000-0000-000000000002'::uuid, 'a0000000-0000-0000-0000-000000000001'::uuid, 'Main Course', 'Hearty main dishes to satisfy your hunger', 2, true),
('c1000000-0000-0000-0000-000000000003'::uuid, 'a0000000-0000-0000-0000-000000000001'::uuid, 'Breads', 'Freshly baked Indian breads', 3, true),
('c1000000-0000-0000-0000-000000000004'::uuid, 'a0000000-0000-0000-0000-000000000001'::uuid, 'Desserts', 'Sweet endings to your meal', 4, true),
('c1000000-0000-0000-0000-000000000005'::uuid, 'a0000000-0000-0000-0000-000000000001'::uuid, 'Beverages', 'Refreshing drinks', 5, true)
ON CONFLICT (id) DO NOTHING;

-- Insert menu items for Restaurant 1
INSERT INTO menu_items (id, restaurant_id, category_id, name, description, base_price, image_url, status, dietary_indicators, allergen_info, preparation_time, sort_order, is_active) VALUES
-- Appetizers
('m1000000-0000-0000-0000-000000000001'::uuid, 'a0000000-0000-0000-0000-000000000001'::uuid, 'c1000000-0000-0000-0000-000000000001'::uuid, 'Samosa (2 pcs)', 'Crispy pastry filled with spiced potatoes and peas', 4.99, 'https://images.unsplash.com/photo-1601050690597-df0568f70950?w=400', 'featured', ARRAY['vegetarian', 'vegan'], ARRAY['gluten'], 15, 1, true),
('m1000000-0000-0000-0000-000000000002'::uuid, 'a0000000-0000-0000-0000-000000000001'::uuid, 'c1000000-0000-0000-0000-000000000001'::uuid, 'Paneer Tikka', 'Grilled cottage cheese marinated in spices', 8.99, 'https://images.unsplash.com/photo-1567188040759-fb8a883dc6d8?w=400', 'available', ARRAY['vegetarian'], ARRAY['dairy'], 20, 2, true),
('m1000000-0000-0000-0000-000000000003'::uuid, 'a0000000-0000-0000-0000-000000000001'::uuid, 'c1000000-0000-0000-0000-000000000001'::uuid, 'Chicken 65', 'Spicy fried chicken with curry leaves', 9.99, 'https://images.unsplash.com/photo-1603894584373-5ac82b2ae398?w=400', 'available', ARRAY['spicy'], ARRAY[], 18, 3, true),

-- Main Course
('m1000000-0000-0000-0000-000000000004'::uuid, 'a0000000-0000-0000-0000-000000000001'::uuid, 'c1000000-0000-0000-0000-000000000002'::uuid, 'Butter Chicken', 'Tender chicken in creamy tomato sauce', 14.99, 'https://images.unsplash.com/photo-1603894584373-5ac82b2ae398?w=400', 'featured', ARRAY[], ARRAY['dairy'], 25, 1, true),
('m1000000-0000-0000-0000-000000000005'::uuid, 'a0000000-0000-0000-0000-000000000001'::uuid, 'c1000000-0000-0000-0000-000000000002'::uuid, 'Palak Paneer', 'Cottage cheese in spinach gravy', 12.99, 'https://images.unsplash.com/photo-1601050690597-df0568f70950?w=400', 'available', ARRAY['vegetarian'], ARRAY['dairy'], 22, 2, true),
('m1000000-0000-0000-0000-000000000006'::uuid, 'a0000000-0000-0000-0000-000000000001'::uuid, 'c1000000-0000-0000-0000-000000000002'::uuid, 'Lamb Rogan Josh', 'Aromatic lamb curry with Kashmiri spices', 16.99, 'https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=400', 'available', ARRAY['spicy'], ARRAY[], 30, 3, true),
('m1000000-0000-0000-0000-000000000007'::uuid, 'a0000000-0000-0000-0000-000000000001'::uuid, 'c1000000-0000-0000-0000-000000000002'::uuid, 'Dal Makhani', 'Black lentils cooked overnight with butter', 11.99, 'https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=400', 'available', ARRAY['vegetarian'], ARRAY['dairy'], 20, 4, true),

-- Breads
('m1000000-0000-0000-0000-000000000008'::uuid, 'a0000000-0000-0000-0000-000000000001'::uuid, 'c1000000-0000-0000-0000-000000000003'::uuid, 'Garlic Naan', 'Leavened bread with garlic and butter', 3.99, 'https://images.unsplash.com/photo-1601050690597-df0568f70950?w=400', 'available', ARRAY['vegetarian'], ARRAY['gluten', 'dairy'], 10, 1, true),
('m1000000-0000-0000-0000-000000000009'::uuid, 'a0000000-0000-0000-0000-000000000001'::uuid, 'c1000000-0000-0000-0000-000000000003'::uuid, 'Tandoori Roti', 'Whole wheat flatbread', 2.99, 'https://images.unsplash.com/photo-1601050690597-df0568f70950?w=400', 'available', ARRAY['vegetarian', 'vegan'], ARRAY['gluten'], 8, 2, true),

-- Desserts
('m1000000-0000-0000-0000-000000000010'::uuid, 'a0000000-0000-0000-0000-000000000001'::uuid, 'c1000000-0000-0000-0000-000000000004'::uuid, 'Gulab Jamun (2 pcs)', 'Soft milk dumplings in rose syrup', 5.99, 'https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=400', 'available', ARRAY['vegetarian'], ARRAY['dairy', 'gluten'], 5, 1, true),
('m1000000-0000-0000-0000-000000000011'::uuid, 'a0000000-0000-0000-0000-000000000001'::uuid, 'c1000000-0000-0000-0000-000000000004'::uuid, 'Mango Kulfi', 'Traditional Indian ice cream', 6.99, 'https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=400', 'featured', ARRAY['vegetarian'], ARRAY['dairy'], 0, 2, true),

-- Beverages
('m1000000-0000-0000-0000-000000000012'::uuid, 'a0000000-0000-0000-0000-000000000001'::uuid, 'c1000000-0000-0000-0000-000000000005'::uuid, 'Mango Lassi', 'Yogurt-based mango smoothie', 4.99, 'https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=400', 'available', ARRAY['vegetarian'], ARRAY['dairy'], 5, 1, true),
('m1000000-0000-0000-0000-000000000013'::uuid, 'a0000000-0000-0000-0000-000000000001'::uuid, 'c1000000-0000-0000-0000-000000000005'::uuid, 'Masala Chai', 'Spiced Indian tea', 2.99, 'https://images.unsplash.com/photo-1597318130878-aa1baa8bc1c9?w=400', 'available', ARRAY['vegetarian'], ARRAY[], 5, 2, true)
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- STEP 7: Insert Test Data - Restaurant 2 (Bella Italia)
-- ============================================================================

-- Insert or update restaurant 2
INSERT INTO restaurants (id, name, code, description, cuisine_type, phone, address, logo_url, primary_color, secondary_color, accent_color, is_active)
VALUES (
    'a0000000-0000-0000-0000-000000000002'::uuid,
    'Bella Italia',
    'BELLA002',
    'Traditional Italian cuisine with fresh ingredients',
    'Italian',
    '+91-9876543211',
    '456 Brigade Road, Bangalore, Karnataka 560025',
    'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=400',
    '#C8102E',
    '#009246',
    '#FFD700',
    true
)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    code = EXCLUDED.code,
    description = EXCLUDED.description,
    cuisine_type = EXCLUDED.cuisine_type,
    phone = EXCLUDED.phone,
    address = EXCLUDED.address,
    logo_url = EXCLUDED.logo_url,
    primary_color = EXCLUDED.primary_color,
    secondary_color = EXCLUDED.secondary_color,
    accent_color = EXCLUDED.accent_color,
    is_active = EXCLUDED.is_active;

-- Insert categories for Restaurant 2
INSERT INTO menu_categories (id, restaurant_id, name, description, sort_order, is_active) VALUES
('c2000000-0000-0000-0000-000000000001'::uuid, 'a0000000-0000-0000-0000-000000000002'::uuid, 'Antipasti', 'Italian appetizers and starters', 1, true),
('c2000000-0000-0000-0000-000000000002'::uuid, 'a0000000-0000-0000-0000-000000000002'::uuid, 'Pasta', 'Fresh handmade pasta dishes', 2, true),
('c2000000-0000-0000-0000-000000000003'::uuid, 'a0000000-0000-0000-0000-000000000002'::uuid, 'Pizza', 'Wood-fired authentic pizzas', 3, true),
('c2000000-0000-0000-0000-000000000004'::uuid, 'a0000000-0000-0000-0000-000000000002'::uuid, 'Dolci', 'Italian desserts', 4, true),
('c2000000-0000-0000-0000-000000000005'::uuid, 'a0000000-0000-0000-0000-000000000002'::uuid, 'Beverages', 'Italian drinks and wines', 5, true)
ON CONFLICT (id) DO NOTHING;

-- Insert menu items for Restaurant 2
INSERT INTO menu_items (id, restaurant_id, category_id, name, description, base_price, image_url, status, dietary_indicators, allergen_info, preparation_time, sort_order, is_active) VALUES
-- Antipasti
('m2000000-0000-0000-0000-000000000001'::uuid, 'a0000000-0000-0000-0000-000000000002'::uuid, 'c2000000-0000-0000-0000-000000000001'::uuid, 'Bruschetta', 'Toasted bread with tomatoes, garlic, and basil', 6.99, 'https://images.unsplash.com/photo-1572695157366-5e585ab2b69f?w=400', 'featured', ARRAY['vegetarian', 'vegan'], ARRAY['gluten'], 10, 1, true),
('m2000000-0000-0000-0000-000000000002'::uuid, 'a0000000-0000-0000-0000-000000000002'::uuid, 'c2000000-0000-0000-0000-000000000001'::uuid, 'Caprese Salad', 'Fresh mozzarella, tomatoes, and basil', 8.99, 'https://images.unsplash.com/photo-1608897013039-887f21d8c804?w=400', 'available', ARRAY['vegetarian'], ARRAY['dairy'], 8, 2, true),
('m2000000-0000-0000-0000-000000000003'::uuid, 'a0000000-0000-0000-0000-000000000002'::uuid, 'c2000000-0000-0000-0000-000000000001'::uuid, 'Arancini (3 pcs)', 'Fried rice balls with mozzarella', 7.99, 'https://images.unsplash.com/photo-1633504581786-316c8002b1b9?w=400', 'available', ARRAY['vegetarian'], ARRAY['dairy', 'gluten'], 15, 3, true),

-- Pasta
('m2000000-0000-0000-0000-000000000004'::uuid, 'a0000000-0000-0000-0000-000000000002'::uuid, 'c2000000-0000-0000-0000-000000000002'::uuid, 'Spaghetti Carbonara', 'Classic Roman pasta with eggs, cheese, and pancetta', 13.99, 'https://images.unsplash.com/photo-1612874742237-6526221588e3?w=400', 'featured', ARRAY[], ARRAY['dairy', 'gluten'], 18, 1, true),
('m2000000-0000-0000-0000-000000000005'::uuid, 'a0000000-0000-0000-0000-000000000002'::uuid, 'c2000000-0000-0000-0000-000000000002'::uuid, 'Penne Arrabbiata', 'Spicy tomato sauce with garlic and chili', 11.99, 'https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?w=400', 'available', ARRAY['vegetarian', 'vegan', 'spicy'], ARRAY['gluten'], 15, 2, true),
('m2000000-0000-0000-0000-000000000006'::uuid, 'a0000000-0000-0000-0000-000000000002'::uuid, 'c2000000-0000-0000-0000-000000000002'::uuid, 'Fettuccine Alfredo', 'Creamy parmesan sauce with butter', 12.99, 'https://images.unsplash.com/photo-1645112411341-6c4fd023714a?w=400', 'available', ARRAY['vegetarian'], ARRAY['dairy', 'gluten'], 16, 3, true),
('m2000000-0000-0000-0000-000000000007'::uuid, 'a0000000-0000-0000-0000-000000000002'::uuid, 'c2000000-0000-0000-0000-000000000002'::uuid, 'Lasagna Bolognese', 'Layered pasta with meat sauce and béchamel', 14.99, 'https://images.unsplash.com/photo-1574894709920-11b28e7367e3?w=400', 'available', ARRAY[], ARRAY['dairy', 'gluten'], 25, 4, true),

-- Pizza
('m2000000-0000-0000-0000-000000000008'::uuid, 'a0000000-0000-0000-0000-000000000002'::uuid, 'c2000000-0000-0000-0000-000000000003'::uuid, 'Margherita', 'Tomato sauce, mozzarella, and fresh basil', 11.99, 'https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=400', 'featured', ARRAY['vegetarian'], ARRAY['dairy', 'gluten'], 12, 1, true),
('m2000000-0000-0000-0000-000000000009'::uuid, 'a0000000-0000-0000-0000-000000000002'::uuid, 'c2000000-0000-0000-0000-000000000003'::uuid, 'Quattro Formaggi', 'Four cheese pizza', 13.99, 'https://images.unsplash.com/photo-1513104890138-7c749659a591?w=400', 'available', ARRAY['vegetarian'], ARRAY['dairy', 'gluten'], 12, 2, true),
('m2000000-0000-0000-0000-000000000010'::uuid, 'a0000000-0000-0000-0000-000000000002'::uuid, 'c2000000-0000-0000-0000-000000000003'::uuid, 'Pepperoni', 'Classic pepperoni with mozzarella', 12.99, 'https://images.unsplash.com/photo-1628840042765-356cda07504e?w=400', 'available', ARRAY[], ARRAY['dairy', 'gluten'], 12, 3, true),

-- Dolci
('m2000000-0000-0000-0000-000000000011'::uuid, 'a0000000-0000-0000-0000-000000000002'::uuid, 'c2000000-0000-0000-0000-000000000004'::uuid, 'Tiramisu', 'Classic Italian coffee-flavored dessert', 7.99, 'https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?w=400', 'featured', ARRAY['vegetarian'], ARRAY['dairy', 'gluten'], 0, 1, true),
('m2000000-0000-0000-0000-000000000012'::uuid, 'a0000000-0000-0000-0000-000000000002'::uuid, 'c2000000-0000-0000-0000-000000000004'::uuid, 'Panna Cotta', 'Creamy vanilla dessert with berry sauce', 6.99, 'https://images.unsplash.com/photo-1488477181946-6428a0291777?w=400', 'available', ARRAY['vegetarian'], ARRAY['dairy'], 0, 2, true),

-- Beverages
('m2000000-0000-0000-0000-000000000013'::uuid, 'a0000000-0000-0000-0000-000000000002'::uuid, 'c2000000-0000-0000-0000-000000000005'::uuid, 'Espresso', 'Strong Italian coffee', 3.99, 'https://images.unsplash.com/photo-1510591509098-f4fdc6d0ff04?w=400', 'available', ARRAY['vegan'], ARRAY[], 3, 1, true),
('m2000000-0000-0000-0000-000000000014'::uuid, 'a0000000-0000-0000-0000-000000000002'::uuid, 'c2000000-0000-0000-0000-000000000005'::uuid, 'San Pellegrino', 'Sparkling mineral water', 2.99, 'https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=400', 'available', ARRAY['vegan'], ARRAY[], 0, 2, true)
ON CONFLICT (id) DO NOTHING;

COMMIT;

