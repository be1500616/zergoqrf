-- Add RLS policies for multi-tenancy

-- Enable RLS on all tables
ALTER TABLE restaurants ENABLE ROW LEVEL SECURITY;
ALTER TABLE tables ENABLE ROW LEVEL SECURITY;
ALTER TABLE menus ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE restaurant_staff ENABLE ROW LEVEL SECURITY;
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE anonymous_sessions ENABLE ROW LEVEL SECURITY;

-- Helper function to get restaurant_id from JWT
CREATE OR REPLACE FUNCTION auth.get_restaurant_id()
RETURNS UUID AS $$
BEGIN
  RETURN (auth.jwt() ->> 'restaurant_id')::UUID;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Helper function to get user role from JWT
CREATE OR REPLACE FUNCTION auth.get_user_role()
RETURNS TEXT AS $$
BEGIN
  RETURN auth.jwt() ->> 'role';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Helper function to check if user has permission
CREATE OR REPLACE FUNCTION auth.has_permission(required_permission TEXT)
RETURNS BOOLEAN AS $$
DECLARE
  user_restaurant_id UUID;
  user_role TEXT;
  staff_permissions JSONB;
BEGIN
  user_restaurant_id := auth.get_restaurant_id();
  user_role := auth.get_user_role();

  -- Service role has all permissions
  IF auth.role() = 'service_role' THEN
    RETURN true;
  END IF;

  -- Anonymous users have no permissions
  IF auth.role() = 'anon' THEN
    RETURN false;
  END IF;

  -- Check staff permissions
  SELECT permissions INTO staff_permissions
  FROM restaurant_staff
  WHERE user_id = auth.uid()
    AND restaurant_id = user_restaurant_id
    AND is_active = true;

  -- Owner has all permissions
  IF user_role = 'owner' THEN
    RETURN true;
  END IF;

  -- Check specific permission
  RETURN (staff_permissions ? required_permission) OR (staff_permissions ->> required_permission)::BOOLEAN;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- RESTAURANTS POLICIES
-- Public read access for restaurant info (needed for QR codes)
CREATE POLICY "restaurants_select_public" ON restaurants
  FOR SELECT USING (true);

-- Only owners can create restaurants
CREATE POLICY "restaurants_insert_owner" ON restaurants
  FOR INSERT WITH CHECK (auth.has_permission('create_restaurant'));

-- Only staff of the restaurant can update it
CREATE POLICY "restaurants_update_staff" ON restaurants
  FOR UPDATE USING (
    auth.get_restaurant_id() = id AND
    auth.has_permission('manage_restaurant')
  );

-- Only owners can delete restaurants
CREATE POLICY "restaurants_delete_owner" ON restaurants
  FOR DELETE USING (
    auth.get_restaurant_id() = id AND
    auth.get_user_role() = 'owner'
  );

-- TABLES POLICIES
-- Public read access for table info (needed for QR codes)
CREATE POLICY "tables_select_public" ON tables
  FOR SELECT USING (true);

-- Only staff can create tables
CREATE POLICY "tables_insert_staff" ON tables
  FOR INSERT WITH CHECK (
    auth.get_restaurant_id() = restaurant_id AND
    auth.has_permission('manage_tables')
  );

-- Only staff can update tables
CREATE POLICY "tables_update_staff" ON tables
  FOR UPDATE USING (
    auth.get_restaurant_id() = restaurant_id AND
    auth.has_permission('manage_tables')
  );

-- Only managers and owners can delete tables
CREATE POLICY "tables_delete_manager" ON tables
  FOR DELETE USING (
    auth.get_restaurant_id() = restaurant_id AND
    (auth.get_user_role() IN ('owner', 'manager'))
  );

-- MENUS POLICIES
-- Public read access for menu info (needed for customers)
CREATE POLICY "menus_select_public" ON menus
  FOR SELECT USING (true);

-- Only staff can create menus
CREATE POLICY "menus_insert_staff" ON menus
  FOR INSERT WITH CHECK (
    auth.get_restaurant_id() = restaurant_id AND
    auth.has_permission('manage_menu')
  );

-- Only staff can update menus
CREATE POLICY "menus_update_staff" ON menus
  FOR UPDATE USING (
    auth.get_restaurant_id() = restaurant_id AND
    auth.has_permission('manage_menu')
  );

-- Only managers and owners can delete menus
CREATE POLICY "menus_delete_manager" ON menus
  FOR DELETE USING (
    auth.get_restaurant_id() = restaurant_id AND
    (auth.get_user_role() IN ('owner', 'manager'))
  );

-- RESTAURANT STAFF POLICIES
-- Staff can only see other staff in their restaurant
CREATE POLICY "restaurant_staff_select_same_restaurant" ON restaurant_staff
  FOR SELECT USING (
    auth.get_restaurant_id() = restaurant_id
  );

-- Only owners and managers can add staff
CREATE POLICY "restaurant_staff_insert_manager" ON restaurant_staff
  FOR INSERT WITH CHECK (
    auth.get_restaurant_id() = restaurant_id AND
    (auth.get_user_role() IN ('owner', 'manager'))
  );

-- Only owners and managers can update staff
CREATE POLICY "restaurant_staff_update_manager" ON restaurant_staff
  FOR UPDATE USING (
    auth.get_restaurant_id() = restaurant_id AND
    (auth.get_user_role() IN ('owner', 'manager'))
  );

-- Only owners can delete staff
CREATE POLICY "restaurant_staff_delete_owner" ON restaurant_staff
  FOR DELETE USING (
    auth.get_restaurant_id() = restaurant_id AND
    auth.get_user_role() = 'owner'
  );

-- CUSTOMERS POLICIES
-- Customers can only see their own data
CREATE POLICY "customers_select_own" ON customers
  FOR SELECT USING (
    auth.uid()::TEXT = id::TEXT OR
    auth.role() = 'service_role'
  );

-- Anyone can create customer records (for registration)
CREATE POLICY "customers_insert_public" ON customers
  FOR INSERT WITH CHECK (true);

-- Customers can only update their own data
CREATE POLICY "customers_update_own" ON customers
  FOR UPDATE USING (
    auth.uid()::TEXT = id::TEXT OR
    auth.role() = 'service_role'
  );

-- Customers can delete their own data
CREATE POLICY "customers_delete_own" ON customers
  FOR DELETE USING (
    auth.uid()::TEXT = id::TEXT OR
    auth.role() = 'service_role'
  );

-- ANONYMOUS SESSIONS POLICIES
-- Anonymous sessions are readable by anyone (needed for validation)
CREATE POLICY "anonymous_sessions_select_public" ON anonymous_sessions
  FOR SELECT USING (true);

-- Only service role can create anonymous sessions
CREATE POLICY "anonymous_sessions_insert_service" ON anonymous_sessions
  FOR INSERT WITH CHECK (auth.role() = 'service_role');

-- No updates allowed on anonymous sessions
-- Sessions expire naturally

-- Only service role can delete expired sessions
CREATE POLICY "anonymous_sessions_delete_service" ON anonymous_sessions
  FOR DELETE USING (auth.role() = 'service_role');

-- ORDERS POLICIES
-- Staff can see all orders for their restaurant
-- Customers can see their own orders
-- Anonymous users can see orders for their session
CREATE POLICY "orders_select_authorized" ON orders
  FOR SELECT USING (
    -- Staff can see all orders for their restaurant
    (auth.get_restaurant_id() = restaurant_id AND auth.role() = 'authenticated') OR
    -- Customers can see their own orders
    (auth.uid()::TEXT = customer_id::TEXT) OR
    -- Anonymous users can see orders for their session
    (anonymous_session_id IS NOT NULL AND
     EXISTS (SELECT 1 FROM anonymous_sessions
             WHERE id = orders.anonymous_session_id
             AND session_token = auth.jwt() ->> 'session_token'))
  );

-- Anyone can create orders (customers, anonymous users, staff)
CREATE POLICY "orders_insert_public" ON orders
  FOR INSERT WITH CHECK (
    -- Must be for a valid restaurant
    restaurant_id IS NOT NULL AND
    -- Must have either customer_id or anonymous_session_id
    (customer_id IS NOT NULL OR anonymous_session_id IS NOT NULL)
  );

-- Only staff can update orders
CREATE POLICY "orders_update_staff" ON orders
  FOR UPDATE USING (
    auth.get_restaurant_id() = restaurant_id AND
    auth.has_permission('manage_orders')
  );

-- Only managers and owners can delete orders
CREATE POLICY "orders_delete_manager" ON orders
  FOR DELETE USING (
    auth.get_restaurant_id() = restaurant_id AND
    (auth.get_user_role() IN ('owner', 'manager'))
  );