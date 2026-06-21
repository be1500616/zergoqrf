-- Order Management Schema Migration
-- Story 3.3: Order Placement & Payment Status Management
-- This migration creates the order management system with dual status tracking

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Order Status Enum
CREATE TYPE order_status AS ENUM (
    'placed',
    'confirmed', 
    'preparing',
    'ready',
    'completed',
    'cancelled'
);

-- Payment Status Enum
CREATE TYPE payment_status AS ENUM (
    'payment_pending',
    'payment_collected',
    'payment_failed'
);

-- Payment Method Enum (extensible for future digital payments)
CREATE TYPE payment_method AS ENUM (
    'cash',
    'razorpay',
    'upi',
    'card'
);

-- Orders Table
-- Main order entity with dual status tracking
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Order identification
    order_number VARCHAR(20) UNIQUE NOT NULL, -- Format: ORD-YYYYMMDD-XXXX
    
    -- Restaurant and table context
    restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    table_id UUID REFERENCES tables(id) ON DELETE SET NULL,
    
    -- Customer context (supports both anonymous and authenticated)
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    customer_name VARCHAR(255) NOT NULL,
    customer_phone VARCHAR(20) NOT NULL, -- Indian +91 format
    customer_email VARCHAR(255),
    
    -- Cart session reference (for traceability)
    cart_session_id UUID REFERENCES cart_sessions(id) ON DELETE SET NULL,
    
    -- Dual status tracking (core feature)
    order_status order_status NOT NULL DEFAULT 'placed',
    payment_status payment_status NOT NULL DEFAULT 'payment_pending',
    payment_method payment_method NOT NULL DEFAULT 'cash',
    
    -- Order details
    special_instructions TEXT,
    estimated_preparation_time INTEGER DEFAULT 30, -- minutes
    
    -- Pricing (GST compliant for India)
    subtotal DECIMAL(10,2) NOT NULL CHECK (subtotal >= 0),
    gst_rate DECIMAL(5,4) NOT NULL DEFAULT 0.05, -- 5% for restaurant services
    gst_amount DECIMAL(10,2) NOT NULL CHECK (gst_amount >= 0),
    total_amount DECIMAL(10,2) NOT NULL CHECK (total_amount >= 0),
    
    -- Payment collection reference
    payment_reference VARCHAR(50) UNIQUE NOT NULL, -- For restaurant staff
    
    -- Status timestamps
    placed_at TIMESTAMPTZ DEFAULT NOW(),
    confirmed_at TIMESTAMPTZ,
    preparing_at TIMESTAMPTZ,
    ready_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    cancelled_at TIMESTAMPTZ,
    payment_collected_at TIMESTAMPTZ,
    
    -- Audit fields
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Business constraints
    CHECK (total_amount = subtotal + gst_amount),
    CHECK (gst_amount = subtotal * gst_rate)
);

-- Order Items Table
-- Migrated from cart_items with order context
CREATE TABLE order_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Order relationship
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    
    -- Menu item relationship
    restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    menu_item_id UUID NOT NULL REFERENCES menu_items(id) ON DELETE CASCADE,
    
    -- Item details (snapshot at time of order placement)
    item_name VARCHAR(255) NOT NULL,
    item_description TEXT,
    base_price DECIMAL(8,2) NOT NULL CHECK (base_price >= 0),
    
    -- Quantity and customizations
    quantity INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0),
    customizations JSONB DEFAULT '{}',
    special_instructions TEXT,
    
    -- Pricing
    unit_price DECIMAL(8,2) NOT NULL CHECK (unit_price >= 0), -- base_price + customizations
    total_price DECIMAL(8,2) NOT NULL CHECK (total_price >= 0), -- unit_price * quantity
    
    -- Status
    is_available BOOLEAN DEFAULT true,
    
    -- Audit fields
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Pricing validation
    CHECK (total_price = unit_price * quantity)
);

-- Payment Collections Table
-- Cash payment tracking for restaurant staff
CREATE TABLE payment_collections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Order relationship
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    payment_reference VARCHAR(50) NOT NULL,
    
    -- Payment details
    amount DECIMAL(10,2) NOT NULL CHECK (amount >= 0),
    payment_method payment_method NOT NULL DEFAULT 'cash',
    
    -- Collection details
    collected_by UUID REFERENCES auth.users(id) ON DELETE SET NULL, -- Staff member
    collected_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Notes and verification
    collection_notes TEXT,
    verification_code VARCHAR(10), -- For customer verification
    
    -- Audit fields
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Order Payment History Table
-- Comprehensive audit trail for compliance
CREATE TABLE order_payment_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Order relationship
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    
    -- Status change details
    previous_order_status order_status,
    new_order_status order_status,
    previous_payment_status payment_status,
    new_payment_status payment_status,
    
    -- Change context
    changed_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    change_reason TEXT,
    change_notes TEXT,
    
    -- Audit fields
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance optimization
CREATE INDEX idx_orders_restaurant_id ON orders(restaurant_id);
CREATE INDEX idx_orders_table_id ON orders(table_id) WHERE table_id IS NOT NULL;
CREATE INDEX idx_orders_user_id ON orders(user_id) WHERE user_id IS NOT NULL;
CREATE INDEX idx_orders_order_status ON orders(order_status);
CREATE INDEX idx_orders_payment_status ON orders(payment_status);
CREATE INDEX idx_orders_order_number ON orders(order_number);
CREATE INDEX idx_orders_payment_reference ON orders(payment_reference);
CREATE INDEX idx_orders_created_at ON orders(created_at);
CREATE INDEX idx_orders_placed_at ON orders(placed_at);

CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_restaurant_id ON order_items(restaurant_id);
CREATE INDEX idx_order_items_menu_item_id ON order_items(menu_item_id);

CREATE INDEX idx_payment_collections_order_id ON payment_collections(order_id);
CREATE INDEX idx_payment_collections_payment_reference ON payment_collections(payment_reference);
CREATE INDEX idx_payment_collections_collected_by ON payment_collections(collected_by) WHERE collected_by IS NOT NULL;
CREATE INDEX idx_payment_collections_collected_at ON payment_collections(collected_at);

CREATE INDEX idx_order_payment_history_order_id ON order_payment_history(order_id);
CREATE INDEX idx_order_payment_history_created_at ON order_payment_history(created_at);

-- Enable RLS on order tables
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE order_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE payment_collections ENABLE ROW LEVEL SECURITY;
ALTER TABLE order_payment_history ENABLE ROW LEVEL SECURITY;

-- RLS Policies for orders
-- Multi-tenant isolation with restaurant-specific access
CREATE POLICY "orders_restaurant_access" ON orders
    FOR ALL USING (
        -- Restaurant staff access
        restaurant_id IN (
            SELECT restaurant_id FROM restaurant_staff 
            WHERE user_id = auth.uid()
        ) OR
        -- Customer access (own orders)
        user_id = auth.uid() OR
        -- Anonymous customer access via session validation
        (user_id IS NULL AND cart_session_id IN (
            SELECT id FROM cart_sessions 
            WHERE session_token = current_setting('request.jwt.claims', true)::json->>'session_token'
            AND expires_at > NOW()
        )) OR
        -- Service role access
        auth.role() = 'service_role'
    );

-- RLS Policies for order_items
CREATE POLICY "order_items_order_access" ON order_items
    FOR ALL USING (
        order_id IN (
            SELECT id FROM orders
            WHERE (
                -- Restaurant staff access
                restaurant_id IN (
                    SELECT restaurant_id FROM restaurant_staff 
                    WHERE user_id = auth.uid()
                ) OR
                -- Customer access (own orders)
                user_id = auth.uid() OR
                -- Anonymous customer access
                (user_id IS NULL AND cart_session_id IN (
                    SELECT id FROM cart_sessions 
                    WHERE session_token = current_setting('request.jwt.claims', true)::json->>'session_token'
                    AND expires_at > NOW()
                )) OR
                -- Service role access
                auth.role() = 'service_role'
            )
        )
    );

-- RLS Policies for payment_collections
CREATE POLICY "payment_collections_restaurant_access" ON payment_collections
    FOR ALL USING (
        order_id IN (
            SELECT id FROM orders
            WHERE restaurant_id IN (
                SELECT restaurant_id FROM restaurant_staff 
                WHERE user_id = auth.uid()
            )
        ) OR
        -- Service role access
        auth.role() = 'service_role'
    );

-- RLS Policies for order_payment_history
CREATE POLICY "order_payment_history_restaurant_access" ON order_payment_history
    FOR ALL USING (
        order_id IN (
            SELECT id FROM orders
            WHERE restaurant_id IN (
                SELECT restaurant_id FROM restaurant_staff 
                WHERE user_id = auth.uid()
            )
        ) OR
        -- Service role access
        auth.role() = 'service_role'
    );

-- Function to generate unique order number
CREATE OR REPLACE FUNCTION generate_order_number()
RETURNS TEXT AS $$
DECLARE
    date_part TEXT;
    sequence_part TEXT;
    order_number TEXT;
    counter INTEGER;
BEGIN
    -- Get current date in YYYYMMDD format
    date_part := to_char(NOW(), 'YYYYMMDD');

    -- Get next sequence number for today
    SELECT COALESCE(MAX(CAST(SUBSTRING(order_number FROM 13 FOR 4) AS INTEGER)), 0) + 1
    INTO counter
    FROM orders
    WHERE order_number LIKE 'ORD-' || date_part || '-%';

    -- Format sequence with leading zeros
    sequence_part := LPAD(counter::TEXT, 4, '0');

    -- Combine parts
    order_number := 'ORD-' || date_part || '-' || sequence_part;

    RETURN order_number;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to generate payment reference
CREATE OR REPLACE FUNCTION generate_payment_reference()
RETURNS TEXT AS $$
DECLARE
    reference TEXT;
BEGIN
    -- Generate payment reference: PAY-YYYYMMDD-HHMMSS-XXX
    reference := 'PAY-' || to_char(NOW(), 'YYYYMMDD-HH24MISS') || '-' ||
                 LPAD((EXTRACT(EPOCH FROM NOW())::INTEGER % 1000)::TEXT, 3, '0');

    RETURN reference;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to create order from cart session
CREATE OR REPLACE FUNCTION create_order_from_cart(
    p_cart_session_id UUID,
    p_customer_name VARCHAR(255),
    p_customer_phone VARCHAR(20),
    p_customer_email VARCHAR(255) DEFAULT NULL,
    p_special_instructions TEXT DEFAULT NULL,
    p_user_id UUID DEFAULT NULL
)
RETURNS TABLE (
    order_id UUID,
    order_number TEXT,
    payment_reference TEXT,
    total_amount DECIMAL(10,2)
) AS $$
DECLARE
    v_order_id UUID;
    v_order_number TEXT;
    v_payment_reference TEXT;
    v_restaurant_id UUID;
    v_table_id UUID;
    v_subtotal DECIMAL(10,2);
    v_gst_amount DECIMAL(10,2);
    v_total_amount DECIMAL(10,2);
    cart_item RECORD;
BEGIN
    -- Get cart session details
    SELECT restaurant_id, table_id, total_amount
    INTO v_restaurant_id, v_table_id, v_subtotal
    FROM cart_sessions
    WHERE id = p_cart_session_id
    AND is_active = true
    AND expires_at > NOW();

    IF v_restaurant_id IS NULL THEN
        RAISE EXCEPTION 'Cart session not found or expired';
    END IF;

    -- Calculate GST (5% for restaurant services in India)
    v_gst_amount := v_subtotal * 0.05;
    v_total_amount := v_subtotal + v_gst_amount;

    -- Generate order identifiers
    v_order_id := gen_random_uuid();
    v_order_number := generate_order_number();
    v_payment_reference := generate_payment_reference();

    -- Create order
    INSERT INTO orders (
        id,
        order_number,
        restaurant_id,
        table_id,
        user_id,
        customer_name,
        customer_phone,
        customer_email,
        cart_session_id,
        special_instructions,
        subtotal,
        gst_amount,
        total_amount,
        payment_reference
    ) VALUES (
        v_order_id,
        v_order_number,
        v_restaurant_id,
        v_table_id,
        p_user_id,
        p_customer_name,
        p_customer_phone,
        p_customer_email,
        p_cart_session_id,
        p_special_instructions,
        v_subtotal,
        v_gst_amount,
        v_total_amount,
        v_payment_reference
    );

    -- Migrate cart items to order items
    FOR cart_item IN
        SELECT * FROM cart_items
        WHERE cart_session_id = p_cart_session_id
    LOOP
        INSERT INTO order_items (
            order_id,
            restaurant_id,
            menu_item_id,
            item_name,
            item_description,
            base_price,
            quantity,
            customizations,
            special_instructions,
            unit_price,
            total_price
        ) VALUES (
            v_order_id,
            cart_item.restaurant_id,
            cart_item.menu_item_id,
            cart_item.item_name,
            cart_item.item_description,
            cart_item.base_price,
            cart_item.quantity,
            cart_item.customizations,
            cart_item.special_instructions,
            cart_item.unit_price,
            cart_item.total_price
        );
    END LOOP;

    -- Mark cart session as converted
    UPDATE cart_sessions
    SET is_active = false, updated_at = NOW()
    WHERE id = p_cart_session_id;

    -- Return order details
    RETURN QUERY SELECT v_order_id, v_order_number, v_payment_reference, v_total_amount;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to update order status with audit trail
CREATE OR REPLACE FUNCTION update_order_status(
    p_order_id UUID,
    p_new_order_status order_status,
    p_changed_by UUID DEFAULT NULL,
    p_change_reason TEXT DEFAULT NULL,
    p_change_notes TEXT DEFAULT NULL
)
RETURNS BOOLEAN AS $$
DECLARE
    v_current_order_status order_status;
    v_current_payment_status payment_status;
    v_timestamp_column TEXT;
BEGIN
    -- Get current status
    SELECT order_status, payment_status
    INTO v_current_order_status, v_current_payment_status
    FROM orders
    WHERE id = p_order_id;

    IF v_current_order_status IS NULL THEN
        RAISE EXCEPTION 'Order not found';
    END IF;

    -- Validate state transition
    IF NOT is_valid_order_status_transition(v_current_order_status, p_new_order_status) THEN
        RAISE EXCEPTION 'Invalid order status transition from % to %', v_current_order_status, p_new_order_status;
    END IF;

    -- Determine timestamp column to update
    v_timestamp_column := CASE p_new_order_status
        WHEN 'confirmed' THEN 'confirmed_at'
        WHEN 'preparing' THEN 'preparing_at'
        WHEN 'ready' THEN 'ready_at'
        WHEN 'completed' THEN 'completed_at'
        WHEN 'cancelled' THEN 'cancelled_at'
        ELSE NULL
    END;

    -- Update order status and timestamp
    IF v_timestamp_column IS NOT NULL THEN
        EXECUTE format('UPDATE orders SET order_status = $1, %I = NOW(), updated_at = NOW() WHERE id = $2',
                      v_timestamp_column)
        USING p_new_order_status, p_order_id;
    ELSE
        UPDATE orders
        SET order_status = p_new_order_status, updated_at = NOW()
        WHERE id = p_order_id;
    END IF;

    -- Record status change in audit trail
    INSERT INTO order_payment_history (
        order_id,
        previous_order_status,
        new_order_status,
        previous_payment_status,
        new_payment_status,
        changed_by,
        change_reason,
        change_notes
    ) VALUES (
        p_order_id,
        v_current_order_status,
        p_new_order_status,
        v_current_payment_status,
        v_current_payment_status, -- Payment status unchanged
        p_changed_by,
        p_change_reason,
        p_change_notes
    );

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to collect payment and update status
CREATE OR REPLACE FUNCTION collect_payment(
    p_order_id UUID,
    p_payment_reference VARCHAR(50),
    p_amount DECIMAL(10,2),
    p_payment_method payment_method DEFAULT 'cash',
    p_collected_by UUID DEFAULT NULL,
    p_collection_notes TEXT DEFAULT NULL,
    p_verification_code VARCHAR(10) DEFAULT NULL
)
RETURNS BOOLEAN AS $$
DECLARE
    v_current_payment_status payment_status;
    v_current_order_status order_status;
    v_expected_amount DECIMAL(10,2);
BEGIN
    -- Get current order details
    SELECT payment_status, order_status, total_amount
    INTO v_current_payment_status, v_current_order_status, v_expected_amount
    FROM orders
    WHERE id = p_order_id
    AND payment_reference = p_payment_reference;

    IF v_current_payment_status IS NULL THEN
        RAISE EXCEPTION 'Order not found or payment reference mismatch';
    END IF;

    -- Validate payment status
    IF v_current_payment_status != 'payment_pending' THEN
        RAISE EXCEPTION 'Payment already processed for this order';
    END IF;

    -- Validate payment amount
    IF p_amount != v_expected_amount THEN
        RAISE EXCEPTION 'Payment amount mismatch. Expected: %, Received: %', v_expected_amount, p_amount;
    END IF;

    -- Record payment collection
    INSERT INTO payment_collections (
        order_id,
        payment_reference,
        amount,
        payment_method,
        collected_by,
        collection_notes,
        verification_code
    ) VALUES (
        p_order_id,
        p_payment_reference,
        p_amount,
        p_payment_method,
        p_collected_by,
        p_collection_notes,
        p_verification_code
    );

    -- Update order payment status and timestamp
    UPDATE orders
    SET
        payment_status = 'payment_collected',
        payment_collected_at = NOW(),
        updated_at = NOW()
    WHERE id = p_order_id;

    -- Auto-transition order to confirmed if still in placed status
    IF v_current_order_status = 'placed' THEN
        UPDATE orders
        SET
            order_status = 'confirmed',
            confirmed_at = NOW(),
            updated_at = NOW()
        WHERE id = p_order_id;

        -- Record status change in audit trail
        INSERT INTO order_payment_history (
            order_id,
            previous_order_status,
            new_order_status,
            previous_payment_status,
            new_payment_status,
            changed_by,
            change_reason,
            change_notes
        ) VALUES (
            p_order_id,
            'placed',
            'confirmed',
            'payment_pending',
            'payment_collected',
            p_collected_by,
            'Payment collected - auto-confirmed',
            'Order automatically confirmed after payment collection'
        );
    ELSE
        -- Record only payment status change
        INSERT INTO order_payment_history (
            order_id,
            previous_order_status,
            new_order_status,
            previous_payment_status,
            new_payment_status,
            changed_by,
            change_reason,
            change_notes
        ) VALUES (
            p_order_id,
            v_current_order_status,
            v_current_order_status, -- Order status unchanged
            'payment_pending',
            'payment_collected',
            p_collected_by,
            'Payment collected',
            p_collection_notes
        );
    END IF;

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to validate order status transitions
CREATE OR REPLACE FUNCTION is_valid_order_status_transition(
    p_current_status order_status,
    p_new_status order_status
)
RETURNS BOOLEAN AS $$
BEGIN
    -- Define valid state transitions
    RETURN CASE
        WHEN p_current_status = 'placed' THEN p_new_status IN ('confirmed', 'cancelled')
        WHEN p_current_status = 'confirmed' THEN p_new_status IN ('preparing', 'cancelled')
        WHEN p_current_status = 'preparing' THEN p_new_status IN ('ready', 'cancelled')
        WHEN p_current_status = 'ready' THEN p_new_status IN ('completed', 'cancelled')
        WHEN p_current_status = 'completed' THEN FALSE -- Terminal state
        WHEN p_current_status = 'cancelled' THEN FALSE -- Terminal state
        ELSE FALSE
    END;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Function to get orders by restaurant with filters
CREATE OR REPLACE FUNCTION get_restaurant_orders(
    p_restaurant_id UUID,
    p_order_status order_status DEFAULT NULL,
    p_payment_status payment_status DEFAULT NULL,
    p_limit INTEGER DEFAULT 50,
    p_offset INTEGER DEFAULT 0
)
RETURNS TABLE (
    id UUID,
    order_number TEXT,
    customer_name VARCHAR(255),
    customer_phone VARCHAR(20),
    order_status order_status,
    payment_status payment_status,
    total_amount DECIMAL(10,2),
    payment_reference VARCHAR(50),
    placed_at TIMESTAMPTZ,
    estimated_preparation_time INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        o.id,
        o.order_number,
        o.customer_name,
        o.customer_phone,
        o.order_status,
        o.payment_status,
        o.total_amount,
        o.payment_reference,
        o.placed_at,
        o.estimated_preparation_time
    FROM orders o
    WHERE o.restaurant_id = p_restaurant_id
    AND (p_order_status IS NULL OR o.order_status = p_order_status)
    AND (p_payment_status IS NULL OR o.payment_status = p_payment_status)
    ORDER BY o.placed_at DESC
    LIMIT p_limit OFFSET p_offset;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get order details with items
CREATE OR REPLACE FUNCTION get_order_with_items(p_order_id UUID)
RETURNS JSON AS $$
DECLARE
    order_data JSON;
    items_data JSON;
    result JSON;
BEGIN
    -- Get order details
    SELECT row_to_json(o) INTO order_data
    FROM (
        SELECT
            id,
            order_number,
            restaurant_id,
            table_id,
            user_id,
            customer_name,
            customer_phone,
            customer_email,
            order_status,
            payment_status,
            payment_method,
            special_instructions,
            estimated_preparation_time,
            subtotal,
            gst_rate,
            gst_amount,
            total_amount,
            payment_reference,
            placed_at,
            confirmed_at,
            preparing_at,
            ready_at,
            completed_at,
            cancelled_at,
            payment_collected_at,
            created_at,
            updated_at
        FROM orders
        WHERE id = p_order_id
    ) o;

    -- Get order items
    SELECT json_agg(oi) INTO items_data
    FROM (
        SELECT
            id,
            menu_item_id,
            item_name,
            item_description,
            base_price,
            quantity,
            customizations,
            special_instructions,
            unit_price,
            total_price,
            is_available
        FROM order_items
        WHERE order_id = p_order_id
        ORDER BY created_at
    ) oi;

    -- Combine order and items
    result := json_build_object(
        'order', order_data,
        'items', COALESCE(items_data, '[]'::json)
    );

    RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger function to update order updated_at timestamp
CREATE OR REPLACE FUNCTION update_order_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers
CREATE TRIGGER orders_updated_at_trigger
    BEFORE UPDATE ON orders
    FOR EACH ROW EXECUTE FUNCTION update_order_updated_at();

CREATE TRIGGER order_items_updated_at_trigger
    BEFORE UPDATE ON order_items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER payment_collections_updated_at_trigger
    BEFORE UPDATE ON payment_collections
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON orders TO anon, authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON order_items TO anon, authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON payment_collections TO authenticated; -- Only authenticated users can collect payments
GRANT SELECT ON order_payment_history TO authenticated;

GRANT EXECUTE ON FUNCTION generate_order_number TO anon, authenticated;
GRANT EXECUTE ON FUNCTION generate_payment_reference TO anon, authenticated;
GRANT EXECUTE ON FUNCTION create_order_from_cart TO anon, authenticated;
GRANT EXECUTE ON FUNCTION update_order_status TO authenticated;
GRANT EXECUTE ON FUNCTION collect_payment TO authenticated;
GRANT EXECUTE ON FUNCTION is_valid_order_status_transition TO anon, authenticated;
GRANT EXECUTE ON FUNCTION get_restaurant_orders TO authenticated;
GRANT EXECUTE ON FUNCTION get_order_with_items TO anon, authenticated;
