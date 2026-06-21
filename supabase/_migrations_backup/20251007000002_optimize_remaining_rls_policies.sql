-- Optimize remaining RLS policies to fix auth function re-evaluation issues
-- This migration updates all remaining RLS policies to use optimized auth function calls

BEGIN;

-- ============================================================================
-- RESTAURANTS TABLE - Update policies to use optimized auth functions
-- ============================================================================

-- Drop existing policies
DROP POLICY IF EXISTS "restaurants_insert_service" ON restaurants;
DROP POLICY IF EXISTS "restaurants_update_service" ON restaurants;
DROP POLICY IF EXISTS "restaurants_delete_service" ON restaurants;

-- Create optimized policies
CREATE POLICY "restaurants_insert_service" ON restaurants
  FOR INSERT WITH CHECK (
    (select auth.role()) = 'service_role' OR
    (select auth.current_user_has_permission('create_restaurant'))
  );

CREATE POLICY "restaurants_update_service" ON restaurants
  FOR UPDATE USING (
    (select auth.role()) = 'service_role' OR
    ((select auth.get_current_user_restaurant_id()) = id AND
     (select auth.current_user_has_permission('manage_restaurant')))
  );

CREATE POLICY "restaurants_delete_service" ON restaurants
  FOR DELETE USING (
    (select auth.role()) = 'service_role' OR
    ((select auth.get_current_user_restaurant_id()) = id AND
     (select auth.current_user_has_role('owner')))
  );

-- ============================================================================
-- TABLES TABLE - Update policies to use optimized auth functions
-- ============================================================================

-- Drop existing policies
DROP POLICY IF EXISTS "tables_insert_service" ON tables;
DROP POLICY IF EXISTS "tables_update_service" ON tables;
DROP POLICY IF EXISTS "tables_delete_service" ON tables;

-- Create optimized policies
CREATE POLICY "tables_insert_service" ON tables
  FOR INSERT WITH CHECK (
    (select auth.role()) = 'service_role' OR
    ((select auth.get_current_user_restaurant_id()) = restaurant_id AND
     (select auth.current_user_has_permission('manage_tables')))
  );

CREATE POLICY "tables_update_service" ON tables
  FOR UPDATE USING (
    (select auth.role()) = 'service_role' OR
    ((select auth.get_current_user_restaurant_id()) = restaurant_id AND
     (select auth.current_user_has_permission('manage_tables')))
  );

CREATE POLICY "tables_delete_service" ON tables
  FOR DELETE USING (
    (select auth.role()) = 'service_role' OR
    ((select auth.get_current_user_restaurant_id()) = restaurant_id AND
     (select auth.current_user_has_role('manager')))
  );

-- ============================================================================
-- MENUS TABLE - Update policies to use optimized auth functions
-- ============================================================================

-- Drop existing policies
DROP POLICY IF EXISTS "menus_insert_service" ON menus;
DROP POLICY IF EXISTS "menus_update_service" ON menus;
DROP POLICY IF EXISTS "menus_delete_service" ON menus;

-- Create optimized policies
CREATE POLICY "menus_insert_service" ON menus
  FOR INSERT WITH CHECK (
    (select auth.role()) = 'service_role' OR
    ((select auth.get_current_user_restaurant_id()) = restaurant_id AND
     (select auth.current_user_has_permission('manage_menu')))
  );

CREATE POLICY "menus_update_service" ON menus
  FOR UPDATE USING (
    (select auth.role()) = 'service_role' OR
    ((select auth.get_current_user_restaurant_id()) = restaurant_id AND
     (select auth.current_user_has_permission('manage_menu')))
  );

CREATE POLICY "menus_delete_service" ON menus
  FOR DELETE USING (
    (select auth.role()) = 'service_role' OR
    ((select auth.get_current_user_restaurant_id()) = restaurant_id AND
     (select auth.current_user_has_role('manager')))
  );

-- ============================================================================
-- RESTAURANT_STAFF TABLE - Update policies to use optimized auth functions
-- ============================================================================

-- Drop existing policies
DROP POLICY IF EXISTS "restaurant_staff_select_service" ON restaurant_staff;
DROP POLICY IF EXISTS "restaurant_staff_insert_service" ON restaurant_staff;
DROP POLICY IF EXISTS "restaurant_staff_update_service" ON restaurant_staff;
DROP POLICY IF EXISTS "restaurant_staff_delete_service" ON restaurant_staff;

-- Create optimized policies
CREATE POLICY "restaurant_staff_select_service" ON restaurant_staff
  FOR SELECT USING (
    (select auth.role()) = 'service_role' OR
    (select auth.get_current_user_restaurant_id()) = restaurant_id
  );

CREATE POLICY "restaurant_staff_insert_service" ON restaurant_staff
  FOR INSERT WITH CHECK (
    (select auth.role()) = 'service_role' OR
    ((select auth.get_current_user_restaurant_id()) = restaurant_id AND
     (select auth.current_user_has_role('manager')))
  );

CREATE POLICY "restaurant_staff_update_service" ON restaurant_staff
  FOR UPDATE USING (
    (select auth.role()) = 'service_role' OR
    ((select auth.get_current_user_restaurant_id()) = restaurant_id AND
     (select auth.current_user_has_role('manager')))
  );

CREATE POLICY "restaurant_staff_delete_service" ON restaurant_staff
  FOR DELETE USING (
    (select auth.role()) = 'service_role' OR
    ((select auth.get_current_user_restaurant_id()) = restaurant_id AND
     (select auth.current_user_has_role('owner')))
  );

-- ============================================================================
-- ANONYMOUS_SESSIONS TABLE - Update policies to use optimized auth functions
-- ============================================================================

-- Drop existing policies
DROP POLICY IF EXISTS "anonymous_sessions_insert_service" ON anonymous_sessions;
DROP POLICY IF EXISTS "anonymous_sessions_delete_service" ON anonymous_sessions;

-- Create optimized policies
CREATE POLICY "anonymous_sessions_insert_service" ON anonymous_sessions
  FOR INSERT WITH CHECK (
    (select auth.role()) = 'service_role'
  );

CREATE POLICY "anonymous_sessions_delete_service" ON anonymous_sessions
  FOR DELETE USING (
    (select auth.role()) = 'service_role'
  );

-- ============================================================================
-- AUTH_SESSIONS TABLE - Update policies to use optimized auth functions
-- ============================================================================

-- Drop existing policies
DROP POLICY IF EXISTS "auth_sessions_select_own" ON auth_sessions;
DROP POLICY IF EXISTS "auth_sessions_insert_own" ON auth_sessions;
DROP POLICY IF EXISTS "auth_sessions_update_own" ON auth_sessions;
DROP POLICY IF EXISTS "auth_sessions_delete_own" ON auth_sessions;

-- Create optimized policies
CREATE POLICY "auth_sessions_select_own" ON auth_sessions
  FOR SELECT USING (
    (select auth.role()) = 'service_role' OR
    user_id = (select auth.uid())
  );

CREATE POLICY "auth_sessions_insert_own" ON auth_sessions
  FOR INSERT WITH CHECK (
    (select auth.role()) = 'service_role' OR
    user_id = (select auth.uid())
  );

CREATE POLICY "auth_sessions_update_own" ON auth_sessions
  FOR UPDATE USING (
    (select auth.role()) = 'service_role' OR
    user_id = (select auth.uid())
  );

CREATE POLICY "auth_sessions_delete_own" ON auth_sessions
  FOR DELETE USING (
    (select auth.role()) = 'service_role' OR
    user_id = (select auth.uid())
  );

-- ============================================================================
-- CUSTOMERS TABLE - Update policies to use optimized auth functions
-- ============================================================================

-- Drop existing policies
DROP POLICY IF EXISTS "customers_select_own" ON customers;
DROP POLICY IF EXISTS "customers_insert_authenticated" ON customers;
DROP POLICY IF EXISTS "customers_update_own" ON customers;
DROP POLICY IF EXISTS "customers_delete_own" ON customers;
DROP POLICY IF EXISTS "customers_anonymous_service_only" ON customers;

-- Create optimized policies
CREATE POLICY "customers_select_own" ON customers
  FOR SELECT USING (
    (select auth.role()) = 'service_role' OR
    user_id = (select auth.uid())
  );

CREATE POLICY "customers_insert_authenticated" ON customers
  FOR INSERT WITH CHECK (
    (select auth.role()) = 'service_role' OR
    (user_id = (select auth.uid()) AND (select auth.uid()) IS NOT NULL)
  );

CREATE POLICY "customers_update_own" ON customers
  FOR UPDATE USING (
    (select auth.role()) = 'service_role' OR
    user_id = (select auth.uid())
  );

CREATE POLICY "customers_delete_own" ON customers
  FOR DELETE USING (
    (select auth.role()) = 'service_role' OR
    user_id = (select auth.uid())
  );

-- Policy for anonymous customers (user_id IS NULL)
CREATE POLICY "customers_anonymous_service_only" ON customers
  FOR ALL USING (
    (user_id IS NULL AND (select auth.role()) = 'service_role') OR
    (user_id IS NOT NULL AND user_id = (select auth.uid()))
  );

COMMIT;
