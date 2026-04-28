#!/usr/bin/env python3
"""Script to check the customers table schema."""

import asyncio
from app.common.supabase_client import get_supabase

async def check_customers_schema():
    """Check the customers table schema by attempting operations."""
    print("=" * 60)
    print("CHECKING CUSTOMERS TABLE SCHEMA")
    print("=" * 60)
    
    try:
        client = get_supabase()
        print(f"✅ Connected to Supabase")
        
        # Try to insert empty data to see what columns are required
        print(f"\n🔍 Testing empty insert to see required columns...")
        try:
            result = client.table("customers").insert({}).execute()
            print(f"✅ Empty insert succeeded: {result.data}")
        except Exception as e:
            print(f"❌ Empty insert failed (shows required columns): {str(e)}")
        
        # Try to insert minimal data
        print(f"\n🔍 Testing minimal insert...")
        try:
            result = client.table("customers").insert({"name": "Test User"}).execute()
            print(f"✅ Minimal insert succeeded: {result.data}")
            
            # If successful, delete the test record
            if result.data:
                delete_result = client.table("customers").delete().eq("name", "Test User").execute()
                print(f"✅ Test record deleted: {delete_result.data}")
        except Exception as e:
            print(f"❌ Minimal insert failed: {str(e)}")
        
        # Try different field combinations
        test_fields = [
            {"email": "test@example.com"},
            {"phone": "+1234567890"},
            {"id": "123e4567-e89b-12d3-a456-426614174000"},
            {"email": "test@example.com", "name": "Test User"},
            {"phone": "+1234567890", "name": "Test User"},
            {"email": "test@example.com", "phone": "+1234567890", "name": "Test User"},
        ]
        
        for i, fields in enumerate(test_fields):
            print(f"\n🔍 Testing insert with fields {fields}...")
            try:
                result = client.table("customers").insert(fields).execute()
                print(f"✅ Insert succeeded: {result.data}")
                
                # Clean up
                if result.data and result.data[0].get('id'):
                    delete_result = client.table("customers").delete().eq("id", result.data[0]['id']).execute()
                    print(f"✅ Test record deleted")
                break  # If one succeeds, we know the schema
            except Exception as e:
                print(f"❌ Insert failed: {str(e)}")
        
        # Try to select with specific columns to understand the schema
        print(f"\n🔍 Testing select with common column names...")
        common_columns = ["id", "email", "phone", "name", "created_at", "updated_at", "role", "is_active"]
        
        for column in common_columns:
            try:
                result = client.table("customers").select(column).limit(1).execute()
                print(f"✅ Column '{column}' exists")
            except Exception as e:
                if "does not exist" in str(e).lower():
                    print(f"❌ Column '{column}' does not exist")
                else:
                    print(f"❓ Column '{column}' error: {str(e)}")
                    
    except Exception as e:
        print(f"❌ Failed to check customers schema: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_customers_schema())
