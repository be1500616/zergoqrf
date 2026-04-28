#!/usr/bin/env python3
"""Script to create auth_sessions table using direct SQL execution."""

import asyncio
from app.common.supabase_client import get_supabase

async def create_auth_sessions_table():
    """Create the auth_sessions table."""
    print("Creating auth_sessions table...")
    
    try:
        # Get Supabase client with service role
        client = get_supabase()
        print(f"✅ Connected to Supabase: {type(client)}")
        
        # Simple table creation SQL
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS auth_sessions (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID,
            restaurant_id UUID,
            table_id UUID,
            session_token TEXT UNIQUE NOT NULL,
            access_token TEXT,
            refresh_token TEXT,
            expires_at TIMESTAMPTZ NOT NULL,
            is_anonymous BOOLEAN DEFAULT false,
            is_active BOOLEAN DEFAULT true,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            last_accessed_at TIMESTAMPTZ DEFAULT NOW()
        );
        """
        
        print("🔧 Creating auth_sessions table...")
        
        # Try to execute using a stored procedure approach
        try:
            # First, let's try to create a simple function to execute SQL
            create_function_sql = """
            CREATE OR REPLACE FUNCTION create_auth_sessions_table()
            RETURNS TEXT AS $$
            BEGIN
                CREATE TABLE IF NOT EXISTS auth_sessions (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id UUID,
                    restaurant_id UUID,
                    table_id UUID,
                    session_token TEXT UNIQUE NOT NULL,
                    access_token TEXT,
                    refresh_token TEXT,
                    expires_at TIMESTAMPTZ NOT NULL,
                    is_anonymous BOOLEAN DEFAULT false,
                    is_active BOOLEAN DEFAULT true,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    last_accessed_at TIMESTAMPTZ DEFAULT NOW()
                );
                RETURN 'Table created successfully';
            END;
            $$ LANGUAGE plpgsql SECURITY DEFINER;
            """
            
            # Create the function
            result = client.rpc('exec', {'sql': create_function_sql}).execute()
            print("✅ Function created")
            
            # Execute the function
            result = client.rpc('create_auth_sessions_table').execute()
            print(f"✅ Table creation result: {result.data}")
            
        except Exception as e:
            print(f"❌ Function approach failed: {str(e)}")
            
            # Try direct table access approach
            print("🔄 Trying direct table creation...")
            
            # Let's try to create the table by inserting a dummy record and letting it fail
            # This will at least tell us if the table exists
            try:
                result = client.table('auth_sessions').select('*').limit(1).execute()
                print("✅ auth_sessions table already exists!")
                return
            except Exception as table_error:
                if "Could not find the table" in str(table_error):
                    print("❌ Table doesn't exist, need to create it manually")
                    print("Please create the auth_sessions table manually in Supabase dashboard")
                    print("SQL to execute:")
                    print(create_table_sql)
                else:
                    print(f"❌ Unexpected error: {str(table_error)}")
        
    except Exception as e:
        print(f"❌ Script failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(create_auth_sessions_table())
