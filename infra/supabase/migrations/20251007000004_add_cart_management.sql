-- Cart Management Schema Migration
-- Story 3.2: Cart Management & Session Security
-- This migration creates the cart management system with hybrid authentication support

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Cart Sessions Table
-- Unified session management for both anonymous and authenticated users
CREATE TABLE cart_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Session identification
    session_token TEXT UNIQUE NOT NULL,
    session_type VARCHAR(20) NOT NULL CHECK (session_type IN ('anonymous', 'authenticated')),
    
    -- User context
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE, -- NULL for anonymous sessions
    anonymous_session_id UUID REFERENCES anonymous_sessions(id) ON DELETE CASCADE, -- NULL for authenticated sessions
    
    -- Restaurant context
    restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    table_id UUID REFERENCES tables(id) ON DELETE SET NULL,
    
    -- Session management
    expires_at TIMESTAMPTZ NOT NULL,
    last_activity_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true,
    
    -- Cart metadata
    item_count INTEGER DEFAULT 0 CHECK (item_count >= 0 AND item_count <= 50),
    total_amount DECIMAL(10,2) DEFAULT 0.00 CHECK (total_amount >= 0),
    
    -- Audit fields
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    CHECK (
        (session_type = 'anonymous' AND user_id IS NULL AND anonymous_session_id IS NOT NULL) OR
        (session_type = 'authenticated' AND user_id IS NOT NULL AND anonymous_session_id IS NULL)
    )
);

-- Cart Items Table
-- Persistent storage for cart items with proper relationships
CREATE TABLE cart_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Cart relationship
    cart_session_id UUID NOT NULL REFERENCES cart_sessions(id) ON DELETE CASCADE,
    
    -- Menu item relationship
    restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    menu_item_id UUID NOT NULL REFERENCES menu_items(id) ON DELETE CASCADE,
    
    -- Item details (snapshot at time of adding to cart)
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
    is_available BOOLEAN DEFAULT true, -- false if menu item becomes unavailable
    
    -- Audit fields
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Unique constraint to prevent duplicate items in same cart
    UNIQUE(cart_session_id, menu_item_id, customizations)
);

-- Indexes for performance
CREATE INDEX idx_cart_sessions_session_token ON cart_sessions(session_token);
CREATE INDEX idx_cart_sessions_user_id ON cart_sessions(user_id) WHERE user_id IS NOT NULL;
CREATE INDEX idx_cart_sessions_anonymous_session_id ON cart_sessions(anonymous_session_id) WHERE anonymous_session_id IS NOT NULL;
CREATE INDEX idx_cart_sessions_restaurant_id ON cart_sessions(restaurant_id);
CREATE INDEX idx_cart_sessions_expires_at ON cart_sessions(expires_at);
CREATE INDEX idx_cart_sessions_last_activity ON cart_sessions(last_activity_at);

CREATE INDEX idx_cart_items_cart_session_id ON cart_items(cart_session_id);
CREATE INDEX idx_cart_items_restaurant_id ON cart_items(restaurant_id);
CREATE INDEX idx_cart_items_menu_item_id ON cart_items(menu_item_id);
CREATE INDEX idx_cart_items_created_at ON cart_items(created_at);

-- Enable RLS on cart tables
ALTER TABLE cart_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE cart_items ENABLE ROW LEVEL SECURITY;

-- RLS Policies for cart_sessions
-- Anonymous users can only access their own cart sessions
CREATE POLICY "cart_sessions_anonymous_access" ON cart_sessions
    FOR ALL USING (
        -- Anonymous session access via session token validation
        (session_type = 'anonymous' AND 
         anonymous_session_id IN (
             SELECT id FROM anonymous_sessions 
             WHERE session_token = current_setting('request.jwt.claims', true)::json->>'session_token'
             AND expires_at > NOW()
         )) OR
        -- Authenticated user access
        (session_type = 'authenticated' AND user_id = auth.uid()) OR
        -- Service role access
        auth.role() = 'service_role'
    );

-- RLS Policies for cart_items
-- Users can only access cart items from their own cart sessions
CREATE POLICY "cart_items_session_access" ON cart_items
    FOR ALL USING (
        cart_session_id IN (
            SELECT id FROM cart_sessions
            WHERE (
                -- Anonymous session access
                (session_type = 'anonymous' AND 
                 anonymous_session_id IN (
                     SELECT id FROM anonymous_sessions 
                     WHERE session_token = current_setting('request.jwt.claims', true)::json->>'session_token'
                     AND expires_at > NOW()
                 )) OR
                -- Authenticated user access
                (session_type = 'authenticated' AND user_id = auth.uid()) OR
                -- Service role access
                auth.role() = 'service_role'
            )
        )
    );

-- Function to create anonymous cart session
CREATE OR REPLACE FUNCTION create_anonymous_cart_session(
    p_anonymous_session_id UUID,
    p_restaurant_id UUID,
    p_table_id UUID DEFAULT NULL,
    p_expires_hours INTEGER DEFAULT 2
)
RETURNS TABLE (
    session_id UUID,
    session_token TEXT,
    expires_at TIMESTAMPTZ
) AS $$
DECLARE
    new_session_id UUID;
    new_session_token TEXT;
    new_expires_at TIMESTAMPTZ;
BEGIN
    -- Generate session ID and token
    new_session_id := gen_random_uuid();
    new_session_token := encode(gen_random_bytes(32), 'base64');
    new_expires_at := NOW() + (p_expires_hours || ' hours')::INTERVAL;
    
    -- Insert the cart session
    INSERT INTO cart_sessions (
        id,
        session_token,
        session_type,
        anonymous_session_id,
        restaurant_id,
        table_id,
        expires_at
    ) VALUES (
        new_session_id,
        new_session_token,
        'anonymous',
        p_anonymous_session_id,
        p_restaurant_id,
        p_table_id,
        new_expires_at
    );
    
    -- Return session details
    RETURN QUERY SELECT new_session_id, new_session_token, new_expires_at;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to create authenticated cart session
CREATE OR REPLACE FUNCTION create_authenticated_cart_session(
    p_user_id UUID,
    p_restaurant_id UUID,
    p_table_id UUID DEFAULT NULL,
    p_expires_hours INTEGER DEFAULT 24
)
RETURNS TABLE (
    session_id UUID,
    session_token TEXT,
    expires_at TIMESTAMPTZ
) AS $$
DECLARE
    new_session_id UUID;
    new_session_token TEXT;
    new_expires_at TIMESTAMPTZ;
BEGIN
    -- Generate session ID and token
    new_session_id := gen_random_uuid();
    new_session_token := encode(gen_random_bytes(32), 'base64');
    new_expires_at := NOW() + (p_expires_hours || ' hours')::INTERVAL;
    
    -- Insert the cart session
    INSERT INTO cart_sessions (
        id,
        session_token,
        session_type,
        user_id,
        restaurant_id,
        table_id,
        expires_at
    ) VALUES (
        new_session_id,
        new_session_token,
        'authenticated',
        p_user_id,
        p_restaurant_id,
        p_table_id,
        new_expires_at
    );
    
    -- Return session details
    RETURN QUERY SELECT new_session_id, new_session_token, new_expires_at;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to validate cart session
CREATE OR REPLACE FUNCTION validate_cart_session(p_session_token TEXT)
RETURNS TABLE (
    session_id UUID,
    session_type VARCHAR(20),
    user_id UUID,
    restaurant_id UUID,
    table_id UUID,
    is_valid BOOLEAN,
    expires_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        cs.id,
        cs.session_type,
        cs.user_id,
        cs.restaurant_id,
        cs.table_id,
        (cs.expires_at > NOW() AND cs.is_active) as is_valid,
        cs.expires_at
    FROM cart_sessions cs
    WHERE cs.session_token = p_session_token;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to extend cart session activity
CREATE OR REPLACE FUNCTION extend_cart_session_activity(p_session_token TEXT)
RETURNS BOOLEAN AS $$
DECLARE
    session_found BOOLEAN := false;
BEGIN
    UPDATE cart_sessions 
    SET 
        last_activity_at = NOW(),
        expires_at = CASE 
            WHEN session_type = 'anonymous' THEN NOW() + INTERVAL '2 hours'
            ELSE expires_at -- Don't extend authenticated sessions automatically
        END,
        updated_at = NOW()
    WHERE session_token = p_session_token
    AND expires_at > NOW()
    AND is_active = true;

    RETURN FOUND;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to migrate anonymous cart to authenticated session
CREATE OR REPLACE FUNCTION migrate_cart_to_authenticated(
    p_anonymous_session_token TEXT,
    p_user_id UUID,
    p_restaurant_id UUID
)
RETURNS TABLE (
    new_session_id UUID,
    new_session_token TEXT,
    migrated_items_count INTEGER
) AS $$
DECLARE
    old_cart_session_id UUID;
    new_cart_session_id UUID;
    new_cart_session_token TEXT;
    items_count INTEGER := 0;
BEGIN
    -- Find the anonymous cart session
    SELECT id INTO old_cart_session_id
    FROM cart_sessions
    WHERE session_token = p_anonymous_session_token
    AND session_type = 'anonymous'
    AND expires_at > NOW()
    AND is_active = true;

    IF old_cart_session_id IS NULL THEN
        RAISE EXCEPTION 'Anonymous cart session not found or expired';
    END IF;

    -- Create new authenticated cart session
    SELECT session_id, session_token INTO new_cart_session_id, new_cart_session_token
    FROM create_authenticated_cart_session(p_user_id, p_restaurant_id);

    -- Migrate cart items
    UPDATE cart_items
    SET cart_session_id = new_cart_session_id,
        updated_at = NOW()
    WHERE cart_session_id = old_cart_session_id;

    GET DIAGNOSTICS items_count = ROW_COUNT;

    -- Update cart session totals
    UPDATE cart_sessions
    SET
        item_count = (SELECT COALESCE(SUM(quantity), 0) FROM cart_items WHERE cart_session_id = new_cart_session_id),
        total_amount = (SELECT COALESCE(SUM(total_price), 0) FROM cart_items WHERE cart_session_id = new_cart_session_id),
        updated_at = NOW()
    WHERE id = new_cart_session_id;

    -- Deactivate old anonymous session
    UPDATE cart_sessions
    SET is_active = false, updated_at = NOW()
    WHERE id = old_cart_session_id;

    RETURN QUERY SELECT new_cart_session_id, new_cart_session_token, items_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to update cart session totals
CREATE OR REPLACE FUNCTION update_cart_session_totals(p_cart_session_id UUID)
RETURNS VOID AS $$
BEGIN
    UPDATE cart_sessions
    SET
        item_count = (
            SELECT COALESCE(SUM(quantity), 0)
            FROM cart_items
            WHERE cart_session_id = p_cart_session_id
        ),
        total_amount = (
            SELECT COALESCE(SUM(total_price), 0)
            FROM cart_items
            WHERE cart_session_id = p_cart_session_id
        ),
        updated_at = NOW()
    WHERE id = p_cart_session_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to cleanup expired cart sessions
CREATE OR REPLACE FUNCTION cleanup_expired_cart_sessions()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER := 0;
BEGIN
    -- Delete expired cart sessions and their items (CASCADE will handle items)
    DELETE FROM cart_sessions
    WHERE expires_at < NOW() OR is_active = false;

    GET DIAGNOSTICS deleted_count = ROW_COUNT;

    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to update cart session totals when cart items change
CREATE OR REPLACE FUNCTION trigger_update_cart_totals()
RETURNS TRIGGER AS $$
BEGIN
    -- Update totals for the affected cart session
    IF TG_OP = 'DELETE' THEN
        PERFORM update_cart_session_totals(OLD.cart_session_id);
        RETURN OLD;
    ELSE
        PERFORM update_cart_session_totals(NEW.cart_session_id);
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for cart items
CREATE TRIGGER cart_items_update_totals_trigger
    AFTER INSERT OR UPDATE OR DELETE ON cart_items
    FOR EACH ROW EXECUTE FUNCTION trigger_update_cart_totals();

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER cart_sessions_updated_at_trigger
    BEFORE UPDATE ON cart_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER cart_items_updated_at_trigger
    BEFORE UPDATE ON cart_items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON cart_sessions TO anon, authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON cart_items TO anon, authenticated;
GRANT EXECUTE ON FUNCTION create_anonymous_cart_session TO anon, authenticated;
GRANT EXECUTE ON FUNCTION create_authenticated_cart_session TO authenticated;
GRANT EXECUTE ON FUNCTION validate_cart_session TO anon, authenticated;
GRANT EXECUTE ON FUNCTION extend_cart_session_activity TO anon, authenticated;
GRANT EXECUTE ON FUNCTION migrate_cart_to_authenticated TO authenticated;
GRANT EXECUTE ON FUNCTION update_cart_session_totals TO anon, authenticated;
GRANT EXECUTE ON FUNCTION cleanup_expired_cart_sessions TO service_role;
