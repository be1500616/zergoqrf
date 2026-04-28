-- Add default permissions and role configurations

-- Create a function to set default permissions for roles
CREATE OR REPLACE FUNCTION get_default_permissions(role_name TEXT)
RETURNS JSONB AS $$
BEGIN
  CASE role_name
    WHEN 'owner' THEN
      RETURN '{
        "create_restaurant": true,
        "manage_restaurant": true,
        "manage_tables": true,
        "manage_menu": true,
        "manage_orders": true,
        "manage_staff": true,
        "view_analytics": true,
        "manage_payments": true
      }'::JSONB;
    WHEN 'manager' THEN
      RETURN '{
        "manage_restaurant": true,
        "manage_tables": true,
        "manage_menu": true,
        "manage_orders": true,
        "manage_staff": true,
        "view_analytics": true
      }'::JSONB;
    WHEN 'kitchen' THEN
      RETURN '{
        "manage_orders": true,
        "view_menu": true
      }'::JSONB;
    WHEN 'service' THEN
      RETURN '{
        "manage_orders": true,
        "view_menu": true,
        "manage_tables": true
      }'::JSONB;
    ELSE
      RETURN '{}'::JSONB;
  END CASE;
END;
$$ LANGUAGE plpgsql;

-- Trigger to set default permissions when staff is created
CREATE OR REPLACE FUNCTION set_default_staff_permissions()
RETURNS TRIGGER AS $$
BEGIN
  -- Set default permissions if none provided
  IF NEW.permissions IS NULL OR NEW.permissions = '{}'::JSONB THEN
    NEW.permissions := get_default_permissions(NEW.role);
  END IF;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_staff_permissions
  BEFORE INSERT OR UPDATE ON restaurant_staff
  FOR EACH ROW
  EXECUTE FUNCTION set_default_staff_permissions();

-- Function to create anonymous session
CREATE OR REPLACE FUNCTION create_anonymous_session(
  p_restaurant_id UUID,
  p_table_id UUID
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
  new_expires_at := NOW() + INTERVAL '24 hours';
  
  -- Insert the session
  INSERT INTO anonymous_sessions (id, restaurant_id, table_id, session_token, expires_at)
  VALUES (new_session_id, p_restaurant_id, p_table_id, new_session_token, new_expires_at);
  
  -- Return the session details
  RETURN QUERY SELECT new_session_id, new_session_token, new_expires_at;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to validate anonymous session
CREATE OR REPLACE FUNCTION validate_anonymous_session(p_session_token TEXT)
RETURNS TABLE (
  session_id UUID,
  restaurant_id UUID,
  table_id UUID,
  is_valid BOOLEAN
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    a.id,
    a.restaurant_id,
    a.table_id,
    (a.expires_at > NOW()) as is_valid
  FROM anonymous_sessions a
  WHERE a.session_token = p_session_token;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to clean up expired sessions
CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
RETURNS INTEGER AS $$
DECLARE
  deleted_count INTEGER;
BEGIN
  DELETE FROM anonymous_sessions 
  WHERE expires_at < NOW();
  
  GET DIAGNOSTICS deleted_count = ROW_COUNT;
  RETURN deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create a scheduled job to clean up expired sessions (if pg_cron is available)
-- This would typically be set up separately in Supabase dashboard
-- SELECT cron.schedule('cleanup-expired-sessions', '0 * * * *', 'SELECT cleanup_expired_sessions();');
