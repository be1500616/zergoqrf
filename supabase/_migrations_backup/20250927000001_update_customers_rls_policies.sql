-- Update RLS policies for customers table to use the new user_id foreign key
-- This migration fixes the broken RLS policies that were trying to use auth.uid()
-- without a proper relationship to the customers table

BEGIN;

-- Drop existing customers RLS policies that were broken
DROP POLICY IF EXISTS "customers_select_own" ON customers;
DROP POLICY IF EXISTS "customers_insert_public" ON customers;
DROP POLICY IF EXISTS "customers_update_own" ON customers;
DROP POLICY IF EXISTS "customers_delete_own" ON customers;

-- Create new RLS policies using the user_id foreign key

-- Customers can only see their own data (using user_id FK)
CREATE POLICY "customers_select_own" ON customers
  FOR SELECT USING (
    user_id = auth.uid() OR
    auth.role() = 'service_role'
  );

-- Allow authenticated users to create customer records for themselves
-- Also allow service role for system operations
CREATE POLICY "customers_insert_authenticated" ON customers
  FOR INSERT WITH CHECK (
    (user_id = auth.uid() AND auth.uid() IS NOT NULL) OR
    auth.role() = 'service_role'
  );

-- Customers can only update their own data
CREATE POLICY "customers_update_own" ON customers
  FOR UPDATE USING (
    user_id = auth.uid() OR
    auth.role() = 'service_role'
  );

-- Customers can delete their own data
CREATE POLICY "customers_delete_own" ON customers
  FOR DELETE USING (
    user_id = auth.uid() OR
    auth.role() = 'service_role'
  );

-- Create policy for anonymous customers (user_id IS NULL)
-- These are customers who placed orders without creating accounts
-- They can only be accessed by service role for order processing
CREATE POLICY "customers_anonymous_service_only" ON customers
  FOR ALL USING (
    (user_id IS NULL AND auth.role() = 'service_role') OR
    (user_id IS NOT NULL AND user_id = auth.uid())
  );

-- Update orders table RLS policies to work with the new customer relationship
-- Drop existing order policies that might be affected
DROP POLICY IF EXISTS "orders_customer_access" ON orders;

-- Create new order policy that uses the customer-user relationship
CREATE POLICY "orders_customer_access" ON orders
  FOR SELECT USING (
    -- Restaurant staff can see all orders for their restaurant
    (auth.get_restaurant_id() = restaurant_id AND auth.get_user_role() IN ('owner', 'manager', 'kitchen', 'service')) OR
    -- Customers can see their own orders (through customer_id -> user_id relationship)
    (customer_id IN (
      SELECT id FROM customers WHERE user_id = auth.uid()
    )) OR
    -- Service role can access all orders
    auth.role() = 'service_role'
  );

-- Add policy for customers to create orders
CREATE POLICY "orders_customer_create" ON orders
  FOR INSERT WITH CHECK (
    -- Restaurant staff can create orders for their restaurant
    (auth.get_restaurant_id() = restaurant_id AND auth.get_user_role() IN ('owner', 'manager', 'service')) OR
    -- Customers can create orders for themselves
    (customer_id IN (
      SELECT id FROM customers WHERE user_id = auth.uid()
    )) OR
    -- Anonymous orders (customer_id IS NULL) can be created by anyone
    (customer_id IS NULL AND anonymous_session_id IS NOT NULL) OR
    -- Service role can create any order
    auth.role() = 'service_role'
  );

-- Add comment to document the RLS policy changes
COMMENT ON TABLE customers IS 'Customer records with RLS policies based on user_id foreign key to auth.users';

COMMIT;
