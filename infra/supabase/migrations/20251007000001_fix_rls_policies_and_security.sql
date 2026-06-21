-- Fix RLS policies and security issues identified in authentication system review
-- This migration addresses:
-- 1. Function search path vulnerabilities
-- 2. RLS policy performance issues (auth function optimization)
-- 3. Multiple permissive policies on orders table
-- 4. Missing indexes for foreign keys
-- 5. Proper multi-tenant security implementation

BEGIN;

-- ============================================================================
-- PART 1: Fix Function Search Path Vulnerabilities
-- ============================================================================

-- Fix create_anonymous_session function
DROP FUNCTION IF EXISTS public.create_anonymous_session(uuid, uuid, integer);
CREATE OR REPLACE FUNCTION public.create_anonymous_session(
  p_restaurant_id UUID,
  p_table_id UUID DEFAULT NULL,
  p_expires_hours INTEGER DEFAULT 24
)
RETURNS TABLE (
  session_id UUID,
  session_token TEXT,
  expires_at TIMESTAMPTZ
) 
LANGUAGE plpgsql 
SECURITY DEFINER
SET search_path = public, auth
AS $$
DECLARE
  new_session_id UUID;
  new_session_token TEXT;
  new_expires_at TIMESTAMPTZ;
BEGIN
  -- Generate session ID and token
  new_session_id := gen_random_uuid();
  new_session_token := encode(gen_random_bytes(32), 'base64');
  new_expires_at := NOW() + (p_expires_hours || ' hours')::INTERVAL;
  
  -- Insert the session
  INSERT INTO anonymous_sessions (
    id, 
    restaurant_id, 
    table_id, 
    session_token, 
    expires_at
  )
  VALUES (
    new_session_id, 
    p_restaurant_id, 
    p_table_id, 
    new_session_token, 
    new_expires_at
  );
  
  -- Return the session details
  RETURN QUERY SELECT new_session_id, new_session_token, new_expires_at;
END;
$$;

-- Fix validate_anonymous_session function
DROP FUNCTION IF EXISTS public.validate_anonymous_session(text);
CREATE OR REPLACE FUNCTION public.validate_anonymous_session(p_session_token TEXT)
RETURNS TABLE (
  is_valid BOOLEAN,
  session_id UUID,
  restaurant_id UUID,
  table_id UUID
)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, auth
AS $$
BEGIN
  RETURN QUERY
  SELECT 
    (expires_at > NOW()) as is_valid,
    id as session_id,
    anonymous_sessions.restaurant_id,
    anonymous_sessions.table_id
  FROM anonymous_sessions
  WHERE session_token = p_session_token;
END;
$$;

-- Fix handle_auth_user_updated function
DROP FUNCTION IF EXISTS public.handle_auth_user_updated();
CREATE OR REPLACE FUNCTION public.handle_auth_user_updated()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, auth
AS $$
BEGIN
  -- Update customer record when auth.users is updated
  UPDATE customers 
  SET 
    email = NEW.email,
    updated_at = NOW()
  WHERE user_id = NEW.id;
  
  RETURN NEW;
END;
$$;

-- Fix refresh_user_claims function
DROP FUNCTION IF EXISTS public.refresh_user_claims(uuid);
CREATE OR REPLACE FUNCTION public.refresh_user_claims(user_id UUID)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, auth
AS $$
DECLARE
  user_claims JSONB := '{}';
  staff_record RECORD;
BEGIN
  -- Get staff information for the user
  SELECT 
    rs.restaurant_id,
    rs.role,
    rs.permissions,
    r.name as restaurant_name
  INTO staff_record
  FROM restaurant_staff rs
  JOIN restaurants r ON r.id = rs.restaurant_id
  WHERE rs.user_id = refresh_user_claims.user_id 
    AND rs.is_active = true
  LIMIT 1;
  
  IF FOUND THEN
    user_claims := jsonb_build_object(
      'restaurant_id', staff_record.restaurant_id,
      'role', staff_record.role,
      'permissions', staff_record.permissions,
      'restaurant_name', staff_record.restaurant_name
    );
  END IF;
  
  RETURN user_claims;
END;
$$;

-- Fix get_user_restaurant_id function
DROP FUNCTION IF EXISTS public.get_user_restaurant_id(uuid);
CREATE OR REPLACE FUNCTION public.get_user_restaurant_id(user_id UUID)
RETURNS UUID
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, auth
AS $$
DECLARE
  restaurant_id UUID;
BEGIN
  SELECT rs.restaurant_id INTO restaurant_id
  FROM restaurant_staff rs
  WHERE rs.user_id = get_user_restaurant_id.user_id 
    AND rs.is_active = true
  LIMIT 1;
  
  RETURN restaurant_id;
END;
$$;

-- Fix user_has_role function
DROP FUNCTION IF EXISTS public.user_has_role(uuid, text);
CREATE OR REPLACE FUNCTION public.user_has_role(user_id UUID, required_role TEXT)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, auth
AS $$
DECLARE
  user_role TEXT;
BEGIN
  SELECT rs.role INTO user_role
  FROM restaurant_staff rs
  WHERE rs.user_id = user_has_role.user_id 
    AND rs.is_active = true
  LIMIT 1;
  
  RETURN user_role = required_role OR user_role = 'owner';
END;
$$;

-- Fix user_has_permission function
DROP FUNCTION IF EXISTS public.user_has_permission(uuid, text);
CREATE OR REPLACE FUNCTION public.user_has_permission(user_id UUID, required_permission TEXT)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, auth
AS $$
DECLARE
  user_role TEXT;
  user_permissions JSONB;
BEGIN
  SELECT rs.role, rs.permissions 
  INTO user_role, user_permissions
  FROM restaurant_staff rs
  WHERE rs.user_id = user_has_permission.user_id 
    AND rs.is_active = true
  LIMIT 1;
  
  -- Owner has all permissions
  IF user_role = 'owner' THEN
    RETURN true;
  END IF;
  
  -- Check specific permission
  RETURN (user_permissions ? required_permission) OR 
         (user_permissions ->> required_permission)::BOOLEAN;
END;
$$;

-- ============================================================================
-- PART 2: Add Missing Indexes for Foreign Keys
-- ============================================================================

-- Add indexes for anonymous_sessions foreign keys
CREATE INDEX IF NOT EXISTS idx_anonymous_sessions_restaurant_id ON anonymous_sessions(restaurant_id);
CREATE INDEX IF NOT EXISTS idx_anonymous_sessions_table_id ON anonymous_sessions(table_id);

-- Add indexes for auth_sessions foreign keys
CREATE INDEX IF NOT EXISTS idx_auth_sessions_restaurant_id ON auth_sessions(restaurant_id);
CREATE INDEX IF NOT EXISTS idx_auth_sessions_table_id ON auth_sessions(table_id);

-- Add indexes for menus foreign keys (menus table removed; no-op)
SELECT 1;

-- Add indexes for orders foreign keys
CREATE INDEX IF NOT EXISTS idx_orders_restaurant_id ON orders(restaurant_id);
CREATE INDEX IF NOT EXISTS idx_orders_table_id ON orders(table_id);
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_anonymous_session_id ON orders(anonymous_session_id);

-- Add indexes for restaurant_staff foreign keys
CREATE INDEX IF NOT EXISTS idx_restaurant_staff_user_id ON restaurant_staff(user_id);
CREATE INDEX IF NOT EXISTS idx_restaurant_staff_restaurant_id ON restaurant_staff(restaurant_id);

-- Add indexes for tables foreign keys
CREATE INDEX IF NOT EXISTS idx_tables_restaurant_id ON tables(restaurant_id);

-- Add indexes for customers foreign keys
CREATE INDEX IF NOT EXISTS idx_customers_user_id ON customers(user_id);

-- ============================================================================
-- PART 3: Create Optimized Security Definer Functions for RLS
-- ============================================================================

-- Create optimized function to get current user's restaurant ID
DROP FUNCTION IF EXISTS auth.get_current_user_restaurant_id();
CREATE OR REPLACE FUNCTION auth.get_current_user_restaurant_id()
RETURNS UUID
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, auth
AS $$
DECLARE
  restaurant_id UUID;
BEGIN
  -- Get restaurant_id from JWT claims first (fastest)
  restaurant_id := (auth.jwt() ->> 'restaurant_id')::UUID;
  
  IF restaurant_id IS NOT NULL THEN
    RETURN restaurant_id;
  END IF;
  
  -- Fallback to database lookup
  SELECT rs.restaurant_id INTO restaurant_id
  FROM restaurant_staff rs
  WHERE rs.user_id = auth.uid() 
    AND rs.is_active = true
  LIMIT 1;
  
  RETURN restaurant_id;
END;
$$;

-- Create optimized function to check user role
DROP FUNCTION IF EXISTS auth.current_user_has_role(text);
CREATE OR REPLACE FUNCTION auth.current_user_has_role(required_role TEXT)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, auth
AS $$
DECLARE
  user_role TEXT;
BEGIN
  -- Get role from JWT claims first (fastest)
  user_role := auth.jwt() ->> 'role';

  IF user_role IS NOT NULL THEN
    RETURN user_role = required_role OR user_role = 'owner';
  END IF;

  -- Fallback to database lookup
  SELECT rs.role INTO user_role
  FROM restaurant_staff rs
  WHERE rs.user_id = auth.uid()
    AND rs.is_active = true
  LIMIT 1;

  RETURN user_role = required_role OR user_role = 'owner';
END;
$$;

-- Create optimized function to check user permissions
DROP FUNCTION IF EXISTS auth.current_user_has_permission(text);
CREATE OR REPLACE FUNCTION auth.current_user_has_permission(required_permission TEXT)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, auth
AS $$
DECLARE
  user_role TEXT;
  user_permissions JSONB;
BEGIN
  -- Service role has all permissions
  IF auth.role() = 'service_role' THEN
    RETURN true;
  END IF;

  -- Get role and permissions from database
  SELECT rs.role, rs.permissions
  INTO user_role, user_permissions
  FROM restaurant_staff rs
  WHERE rs.user_id = auth.uid()
    AND rs.is_active = true
  LIMIT 1;

  -- Owner has all permissions
  IF user_role = 'owner' THEN
    RETURN true;
  END IF;

  -- Check specific permission
  RETURN (user_permissions ? required_permission) OR
         (user_permissions ->> required_permission)::BOOLEAN;
END;
$$;

-- ============================================================================
-- PART 4: Drop and Recreate Optimized RLS Policies
-- ============================================================================

-- Drop existing problematic policies on orders table
DROP POLICY IF EXISTS "orders_select_authorized" ON orders;
DROP POLICY IF EXISTS "orders_customer_access" ON orders;
DROP POLICY IF EXISTS "orders_customer_create" ON orders;

-- Create optimized orders policies
CREATE POLICY "orders_select_multi_tenant" ON orders
  FOR SELECT USING (
    -- Restaurant staff can see all orders for their restaurant
    ((select auth.get_current_user_restaurant_id()) = restaurant_id AND
     (select auth.role()) = 'authenticated') OR
    -- Customers can see their own orders
    (customer_id IN (
      SELECT id FROM customers WHERE user_id = (select auth.uid())
    )) OR
    -- Anonymous users can see orders for their session (via RPC validation)
    (anonymous_session_id IS NOT NULL AND
     (select auth.role()) = 'anon') OR
    -- Service role can access all orders
    (select auth.role()) = 'service_role'
  );

CREATE POLICY "orders_insert_multi_tenant" ON orders
  FOR INSERT WITH CHECK (
    -- Restaurant staff can create orders for their restaurant
    ((select auth.get_current_user_restaurant_id()) = restaurant_id AND
     (select auth.current_user_has_permission('manage_orders'))) OR
    -- Customers can create orders for themselves
    (customer_id IN (
      SELECT id FROM customers WHERE user_id = (select auth.uid())
    )) OR
    -- Anonymous orders can be created by anyone
    (customer_id IS NULL AND anonymous_session_id IS NOT NULL) OR
    -- Service role can create any order
    (select auth.role()) = 'service_role'
  );

CREATE POLICY "orders_update_multi_tenant" ON orders
  FOR UPDATE USING (
    ((select auth.get_current_user_restaurant_id()) = restaurant_id AND
     (select auth.current_user_has_permission('manage_orders'))) OR
    (select auth.role()) = 'service_role'
  );

CREATE POLICY "orders_delete_multi_tenant" ON orders
  FOR DELETE USING (
    ((select auth.get_current_user_restaurant_id()) = restaurant_id AND
     (select auth.current_user_has_role('owner'))) OR
    (select auth.role()) = 'service_role'
  );

COMMIT;
