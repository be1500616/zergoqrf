-- Setup authentication hooks and custom claims
-- This migration ensures proper JWT token claims for restaurant staff

-- Create or replace function to handle custom claims
CREATE OR REPLACE FUNCTION public.handle_auth_user_updated()
RETURNS TRIGGER AS $$
DECLARE
    staff_data RECORD;
BEGIN
    -- Get restaurant staff information for this user
    SELECT restaurant_id, role, permissions, is_active
    INTO staff_data
    FROM restaurant_staff
    WHERE user_id = NEW.id AND is_active = true
    LIMIT 1;

    -- Update user metadata with restaurant context
    IF FOUND THEN
        -- User is restaurant staff
        NEW.raw_user_meta_data = COALESCE(NEW.raw_user_meta_data, '{}'::jsonb) || 
            jsonb_build_object(
                'restaurant_id', staff_data.restaurant_id,
                'role', staff_data.role,
                'permissions', COALESCE(staff_data.permissions, '{}'::jsonb)
            );
        
        NEW.raw_app_meta_data = COALESCE(NEW.raw_app_meta_data, '{}'::jsonb) || 
            jsonb_build_object(
                'restaurant_id', staff_data.restaurant_id,
                'role', staff_data.role,
                'permissions', COALESCE(staff_data.permissions, '{}'::jsonb)
            );
    ELSE
        -- User is not restaurant staff (customer)
        NEW.raw_user_meta_data = COALESCE(NEW.raw_user_meta_data, '{}'::jsonb) || 
            jsonb_build_object(
                'role', 'customer',
                'permissions', '{}'::jsonb
            );
        
        NEW.raw_app_meta_data = COALESCE(NEW.raw_app_meta_data, '{}'::jsonb) || 
            jsonb_build_object(
                'role', 'customer',
                'permissions', '{}'::jsonb
            );
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create trigger on auth.users table (if it exists and we have access)
-- Note: This might need to be done manually in Supabase dashboard
-- as we may not have direct access to auth schema

-- Create function to refresh user claims when staff data changes
CREATE OR REPLACE FUNCTION public.refresh_user_claims()
RETURNS TRIGGER AS $$
DECLARE
    user_record RECORD;
BEGIN
    -- This function would ideally trigger a refresh of the user's JWT
    -- In practice, this might require the user to re-authenticate
    -- or we need to use Supabase's admin API to update the user
    
    -- For now, we'll just log the change
    RAISE NOTICE 'Staff data changed for user %, restaurant %', 
        COALESCE(NEW.user_id, OLD.user_id), 
        COALESCE(NEW.restaurant_id, OLD.restaurant_id);
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Create trigger on restaurant_staff table
DROP TRIGGER IF EXISTS refresh_user_claims_trigger ON restaurant_staff;
CREATE TRIGGER refresh_user_claims_trigger
    AFTER INSERT OR UPDATE OR DELETE ON restaurant_staff
    FOR EACH ROW
    EXECUTE FUNCTION refresh_user_claims();

-- Create function to get user context (for use in RLS policies)
CREATE OR REPLACE FUNCTION public.get_user_restaurant_id(user_id UUID)
RETURNS UUID AS $$
DECLARE
    restaurant_id UUID;
BEGIN
    SELECT rs.restaurant_id
    INTO restaurant_id
    FROM restaurant_staff rs
    WHERE rs.user_id = $1 AND rs.is_active = true
    LIMIT 1;
    
    RETURN restaurant_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to check if user has role
CREATE OR REPLACE FUNCTION public.user_has_role(user_id UUID, required_role TEXT)
RETURNS BOOLEAN AS $$
DECLARE
    user_role TEXT;
BEGIN
    SELECT rs.role
    INTO user_role
    FROM restaurant_staff rs
    WHERE rs.user_id = $1 AND rs.is_active = true
    LIMIT 1;
    
    RETURN user_role = required_role;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to check if user has permission
CREATE OR REPLACE FUNCTION public.user_has_permission(user_id UUID, permission_key TEXT)
RETURNS BOOLEAN AS $$
DECLARE
    user_permissions JSONB;
BEGIN
    SELECT rs.permissions
    INTO user_permissions
    FROM restaurant_staff rs
    WHERE rs.user_id = $1 AND rs.is_active = true
    LIMIT 1;
    
    RETURN COALESCE((user_permissions ->> permission_key)::BOOLEAN, false);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant necessary permissions
GRANT EXECUTE ON FUNCTION public.get_user_restaurant_id(UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION public.user_has_role(UUID, TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION public.user_has_permission(UUID, TEXT) TO authenticated;

-- Add comments for documentation
COMMENT ON FUNCTION public.handle_auth_user_updated() IS 'Updates user metadata with restaurant context when user record changes';
COMMENT ON FUNCTION public.refresh_user_claims() IS 'Triggers when restaurant staff data changes to refresh user claims';
COMMENT ON FUNCTION public.get_user_restaurant_id(UUID) IS 'Gets the restaurant ID for a user from restaurant_staff table';
COMMENT ON FUNCTION public.user_has_role(UUID, TEXT) IS 'Checks if a user has a specific role';
COMMENT ON FUNCTION public.user_has_permission(UUID, TEXT) IS 'Checks if a user has a specific permission';
