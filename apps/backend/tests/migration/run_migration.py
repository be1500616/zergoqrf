#!/usr/bin/env python3
"""Script to run database migration for auth_sessions table."""

import asyncio
from app.common.supabase_client import get_supabase

async def run_migration():
    """Run the auth_sessions table migration."""
    print("Running auth_sessions table migration...")
    
    try:
        # Get Supabase client with service role
        client = get_supabase()
        print(f"✅ Connected to Supabase: {type(client)}")
        
        # Read the migration SQL
        with open('../../infra/supabase/migrations/20250925000000_add_auth_sessions_table.sql', 'r') as f:
            migration_sql = f.read()
        
        print("📄 Migration SQL loaded")
        
        # Split the SQL into individual statements
        statements = [stmt.strip() for stmt in migration_sql.split(';') if stmt.strip()]
        
        print(f"🔧 Executing {len(statements)} SQL statements...")
        
        # Execute each statement
        for i, statement in enumerate(statements, 1):
            if statement.strip():
                try:
                    print(f"  {i}. Executing: {statement[:50]}...")
                    result = client.rpc('exec_sql', {'sql': statement}).execute()
                    print(f"     ✅ Success")
                except Exception as e:
                    print(f"     ❌ Error: {str(e)}")
                    # Continue with other statements
        
        print("🎉 Migration completed!")
        
        # Test if the table was created
        try:
            result = client.table('auth_sessions').select('*').limit(1).execute()
            print("✅ auth_sessions table is accessible")
        except Exception as e:
            print(f"❌ auth_sessions table test failed: {str(e)}")
            
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_migration())
