#!/usr/bin/env python3
"""Script to create the auth_sessions table in Supabase."""

import asyncio
from app.common.supabase_client import get_supabase

async def create_auth_sessions_table():
    """Create the auth_sessions table for authenticated user sessions."""
    print("=" * 60)
    print("CREATING AUTH_SESSIONS TABLE")
    print("=" * 60)
    
    try:
        client = get_supabase()
        print("✅ Connected to Supabase")
        
        # Create the auth_sessions table
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS auth_sessions (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
            session_token TEXT UNIQUE NOT NULL,
            expires_at TIMESTAMPTZ,
            restaurant_id UUID REFERENCES restaurants(id) ON DELETE SET NULL,
            table_id UUID REFERENCES tables(id) ON DELETE SET NULL,
            is_anonymous BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            last_accessed_at TIMESTAMPTZ DEFAULT NOW()
        );
        """
        
        print("🔧 Creating auth_sessions table...")
        result = client.rpc('exec_sql', {'sql': create_table_sql}).execute()
        print(f"✅ Table creation result: {result}")
        
        # Create indexes for better performance
        create_indexes_sql = """
        CREATE INDEX IF NOT EXISTS idx_auth_sessions_user_id ON auth_sessions(user_id);
        CREATE INDEX IF NOT EXISTS idx_auth_sessions_token ON auth_sessions(session_token);
        CREATE INDEX IF NOT EXISTS idx_auth_sessions_expires_at ON auth_sessions(expires_at);
        """
        
        print("🔧 Creating indexes...")
        index_result = client.rpc('exec_sql', {'sql': create_indexes_sql}).execute()
        print(f"✅ Index creation result: {index_result}")
        
        # Enable RLS on the table
        enable_rls_sql = """
        ALTER TABLE auth_sessions ENABLE ROW LEVEL SECURITY;
        """
        
        print("🔧 Enabling RLS...")
        rls_result = client.rpc('exec_sql', {'sql': enable_rls_sql}).execute()
        print(f"✅ RLS enabled: {rls_result}")
        
        # Create RLS policies
        create_policies_sql = """
        -- Policy for users to access their own sessions
        CREATE POLICY "Users can access their own sessions" ON auth_sessions
            FOR ALL USING (auth.uid() = user_id);
            
        -- Policy for service role to access all sessions
        CREATE POLICY "Service role can access all sessions" ON auth_sessions
            FOR ALL USING (auth.role() = 'service_role');
        """
        
        print("🔧 Creating RLS policies...")
        policy_result = client.rpc('exec_sql', {'sql': create_policies_sql}).execute()
        print(f"✅ Policies created: {policy_result}")
        
        print("\n🎉 auth_sessions table created successfully!")
        
        # Verify the table was created
        print("\n🔍 Verifying table structure...")
        verify_result = client.rpc('exec_sql', {
            'sql': "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'auth_sessions' ORDER BY ordinal_position;"
        }).execute()
        
        if verify_result.data:
            print("✅ Table structure:")
            for row in verify_result.data:
                print(f"   {row['column_name']}: {row['data_type']}")
        else:
            print("❌ Could not verify table structure")
            
    except Exception as e:
        print(f"❌ Failed to create auth_sessions table: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(create_auth_sessions_table())
