-- Add auth_sessions table for authenticated user sessions
-- This table is separate from anonymous_sessions and handles email/phone authentication

-- Auth Sessions Table (for authenticated users)
CREATE TABLE auth_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    restaurant_id UUID REFERENCES restaurants(id) ON DELETE CASCADE,
    table_id UUID REFERENCES tables(id) ON DELETE SET NULL,
    session_token TEXT UNIQUE NOT NULL,
    access_token TEXT,
    refresh_token TEXT,
    expires_at TIMESTAMPTZ NOT NULL,
    is_anonymous BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_accessed_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS on auth_sessions
ALTER TABLE auth_sessions ENABLE ROW LEVEL SECURITY;

-- RLS Policies for auth_sessions
-- Users can only access their own sessions
CREATE POLICY "auth_sessions_select_own" ON auth_sessions
  FOR SELECT USING (
    auth.uid()::TEXT = user_id::TEXT OR
    auth.role() = 'service_role'
  );

-- Users can only create their own sessions (or service role)
CREATE POLICY "auth_sessions_insert_own" ON auth_sessions
  FOR INSERT WITH CHECK (
    auth.uid()::TEXT = user_id::TEXT OR
    auth.role() = 'service_role'
  );

-- Users can only update their own sessions
CREATE POLICY "auth_sessions_update_own" ON auth_sessions
  FOR UPDATE USING (
    auth.uid()::TEXT = user_id::TEXT OR
    auth.role() = 'service_role'
  );

-- Users can only delete their own sessions
CREATE POLICY "auth_sessions_delete_own" ON auth_sessions
  FOR DELETE USING (
    auth.uid()::TEXT = user_id::TEXT OR
    auth.role() = 'service_role'
  );

-- Create indexes for performance
CREATE INDEX idx_auth_sessions_user_id ON auth_sessions(user_id);
CREATE INDEX idx_auth_sessions_session_token ON auth_sessions(session_token);
CREATE INDEX idx_auth_sessions_expires_at ON auth_sessions(expires_at);
CREATE INDEX idx_auth_sessions_active ON auth_sessions(is_active) WHERE is_active = true;

-- Function to clean up expired auth sessions
CREATE OR REPLACE FUNCTION cleanup_expired_auth_sessions()
RETURNS INTEGER AS $$
DECLARE
  deleted_count INTEGER;
BEGIN
  DELETE FROM auth_sessions 
  WHERE expires_at < NOW();
  
  GET DIAGNOSTICS deleted_count = ROW_COUNT;
  RETURN deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to create auth session
CREATE OR REPLACE FUNCTION create_auth_session(
  p_user_id UUID,
  p_restaurant_id UUID DEFAULT NULL,
  p_table_id UUID DEFAULT NULL,
  p_access_token TEXT DEFAULT NULL,
  p_refresh_token TEXT DEFAULT NULL,
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
  
  -- Insert the session
  INSERT INTO auth_sessions (
    id, 
    user_id, 
    restaurant_id, 
    table_id, 
    session_token, 
    access_token,
    refresh_token,
    expires_at
  )
  VALUES (
    new_session_id, 
    p_user_id, 
    p_restaurant_id, 
    p_table_id, 
    new_session_token, 
    p_access_token,
    p_refresh_token,
    new_expires_at
  );
  
  -- Return the session details
  RETURN QUERY SELECT new_session_id, new_session_token, new_expires_at;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
