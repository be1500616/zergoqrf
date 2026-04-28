#!/usr/bin/env python3
"""Script to create exec_sql function in Supabase for running migrations."""

import asyncio
from app.common.supabase_client import get_supabase

async def create_exec_sql_function():
    """Create the exec_sql function in Supabase."""
    print("Creating exec_sql function in Supabase...")
    
    try:
        client = get_supabase()
        print(f"✅ Connected to Supabase: {type(client)}")
        
        # Create the exec_sql function using a direct SQL query
        # We'll use the Supabase REST API to execute this
        function_sql = """
        CREATE OR REPLACE FUNCTION public.exec_sql(sql text)
        RETURNS text AS $$
        BEGIN
            EXECUTE sql;
            RETURN 'OK';
        EXCEPTION
            WHEN OTHERS THEN
                RETURN SQLERRM;
        END;
        $$ LANGUAGE plpgsql SECURITY DEFINER;
        """
        
        # Try to create the function using a different approach
        # Let's use the raw SQL execution through the client
        try:
            # Use the SQL query endpoint directly
            result = client.postgrest.rpc('exec_sql', {'sql': function_sql}).execute()
            print("✅ exec_sql function created successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to create exec_sql function via RPC: {str(e)}")
            
            # Alternative: Try using the SQL endpoint directly
            try:
                # This might work if we have direct SQL access
                response = client.supabase_client.sql(function_sql)
                print("✅ exec_sql function created successfully via SQL endpoint")
                return True
            except Exception as e2:
                print(f"❌ Failed to create exec_sql function via SQL endpoint: {str(e2)}")
                
                # Let's try a different approach - check what functions are available
                print("🔍 Checking available RPC functions...")
                try:
                    # Try to list available functions
                    result = client.table('pg_proc').select('proname').limit(10).execute()
                    print(f"Available functions sample: {result.data}")
                except Exception as e3:
                    print(f"❌ Could not list functions: {str(e3)}")
                
                return False
                
    except Exception as e:
        print(f"❌ Failed to create exec_sql function: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(create_exec_sql_function())
