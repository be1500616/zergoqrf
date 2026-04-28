#!/usr/bin/env python3
"""Script to apply QR generation database migration."""

import asyncio
import os
from pathlib import Path
from app.common.supabase_client import get_supabase

async def apply_qr_migration():
    """Apply the QR generation database migration."""
    print("🚀 Applying QR generation database migration...")
    
    try:
        # Get Supabase client
        client = get_supabase()
        print(f"✅ Connected to Supabase")
        
        # Get the migration file path
        migration_file = Path(__file__).parent.parent.parent / "infra" / "supabase" / "migrations" / "20250926000003_qr_generation_setup.sql"
        
        if not migration_file.exists():
            print(f"❌ Migration file not found: {migration_file}")
            return False
        
        # Read the migration SQL
        with open(migration_file, 'r') as f:
            migration_sql = f.read()
        
        print("📄 QR generation migration SQL loaded")
        
        # For Supabase, we need to apply this migration through the dashboard
        # or using the Supabase CLI. For now, let's provide instructions.
        
        print("\n" + "="*60)
        print("MANUAL MIGRATION REQUIRED")
        print("="*60)
        print("Please apply the QR generation migration manually:")
        print()
        print("1. Go to your Supabase project dashboard")
        print("2. Navigate to SQL Editor")
        print("3. Copy and paste the contents of:")
        print(f"   {migration_file}")
        print("4. Execute the SQL")
        print()
        print("The migration includes:")
        print("- QR codes storage bucket setup")
        print("- RLS policies for QR code access")
        print("- QR generation logs table")
        print("- Helper functions for QR statistics")
        print()
        
        # Test basic connectivity
        try:
            result = client.table("restaurants").select("id").limit(1).execute()
            print("✅ Database connectivity verified")
        except Exception as e:
            print(f"❌ Database connectivity test failed: {str(e)}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Migration preparation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(apply_qr_migration())
    if success:
        print("\n🎉 QR generation migration preparation completed!")
        print("📝 Please apply the migration manually as instructed above.")
    else:
        print("\n❌ QR generation migration preparation failed!")
    
    exit(0 if success else 1)
