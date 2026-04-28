#!/usr/bin/env python3
"""Script to apply table management migration directly using Supabase client."""

import asyncio
from app.common.supabase_client import get_supabase

async def apply_migration_direct():
    """Apply the table management migration directly."""
    print("Applying table management migration directly...")
    
    try:
        client = get_supabase()
        print(f"✅ Connected to Supabase: {type(client)}")
        
        # Since we can't execute arbitrary SQL, let's check what we can do
        # First, let's see the current tables schema
        print("🔍 Checking current tables schema...")
        
        try:
            result = client.table('tables').select('*').limit(1).execute()
            if result.data:
                print(f"✅ Current tables columns: {list(result.data[0].keys())}")
            else:
                print("⚠️  No data in tables, but table exists")
        except Exception as e:
            print(f"❌ Error checking tables: {str(e)}")
        
        # Check if floors table exists
        try:
            result = client.table('floors').select('*').limit(1).execute()
            print("✅ floors table already exists")
        except Exception as e:
            print(f"❌ floors table doesn't exist: {str(e)}")
        
        # Since we can't execute DDL directly, let's provide instructions
        print("\n" + "="*60)
        print("MANUAL MIGRATION REQUIRED")
        print("="*60)
        print("The Supabase client doesn't allow direct DDL execution.")
        print("Please apply the migration manually in the Supabase dashboard:")
        print()
        print("1. Go to your Supabase project dashboard")
        print("2. Navigate to SQL Editor")
        print("3. Copy and paste the contents of:")
        print("   infra/supabase/migrations/20250926000001_enhance_table_management.sql")
        print("4. Execute the SQL")
        print("5. Then copy and paste the contents of:")
        print("   infra/supabase/migrations/20250926000002_sample_table_data.sql")
        print("6. Execute the sample data SQL")
        print()
        print("Alternatively, if you have direct database access:")
        print("psql -h <host> -U <user> -d <database> -f infra/supabase/migrations/20250926000001_enhance_table_management.sql")
        print()
        
        return False
        
    except Exception as e:
        print(f"❌ Migration check failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(apply_migration_direct())
