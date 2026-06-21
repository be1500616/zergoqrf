-- Fix restaurant_staff insert policy to allow owner creation during registration
-- This addresses the issue where restaurant registration fails because the RLS policy
-- only allows managers to create staff records, but we need to create owner records too.

-- Drop the existing problematic policy
DROP POLICY IF EXISTS "restaurant_staff_insert_service" ON restaurant_staff;

-- Create the corrected policy that allows both owners and managers to create staff records
CREATE POLICY "restaurant_staff_insert_service" ON restaurant_staff
  FOR INSERT WITH CHECK (
    -- Service role has full access (bypasses RLS)
    (select auth.role()) = 'service_role' OR
    -- Authenticated users can create staff for their restaurant if they are owner or manager
    ((select auth.get_current_user_restaurant_id()) = restaurant_id AND
     (select auth.current_user_has_role('owner') OR auth.current_user_has_role('manager')))
  );

-- Also ensure the auth.current_user_has_role function handles both owner and manager roles correctly
-- This function should already exist from previous migrations, but let's make sure it's robust
CREATE OR REPLACE FUNCTION auth.current_user_has_role(required_role TEXT)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, auth
AS $$
DECLARE
  user_role TEXT;
BEGIN
  -- Service role has all roles
  IF auth.role() = 'service_role' THEN
    RETURN true;
  END IF;

  -- Get role from database
  SELECT rs.role
  INTO user_role
  FROM restaurant_staff rs
  WHERE rs.user_id = auth.uid()
    AND rs.is_active = true
  LIMIT 1;

  -- Check if user has the required role
  RETURN user_role = required_role;
END;
$$;
