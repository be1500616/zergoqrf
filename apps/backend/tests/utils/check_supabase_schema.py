#!/usr/bin/env python3
"""Script to check Supabase database schema and available tables."""

import asyncio

from app.common.supabase_client import get_supabase


async def check_schema():
    """Check what tables exist in the Supabase database."""
    print("=" * 60)
    print("CHECKING SUPABASE DATABASE SCHEMA")
    print("=" * 60)

    try:
        client = get_supabase()
        print(f"✅ Connected to Supabase: {type(client)}")

        # Try to list all tables by attempting to query them
        tables_to_check = [
            "auth_sessions",
            "anonymous_sessions",
            "users",
            "customers",  # Hint suggested this exists instead of users
            "restaurants",
            "tables",
        ]

        existing_tables = []

        for table_name in tables_to_check:
            try:
                print(f"\n🔍 Checking table: {table_name}")
                result = client.table(table_name).select("*").limit(1).execute()
                print(f"✅ Table '{table_name}' exists")

                if result.data:
                    columns = list(result.data[0].keys())
                    print(f"   Columns: {columns}")
                    if table_name == "customers":
                        print(f"   Sample data: {result.data[0]}")
                else:
                    # Try to get schema info by inserting empty data (will fail but show expected columns)
                    try:
                        client.table(table_name).insert({}).execute()
                    except Exception as schema_error:
                        print(
                            f"   Schema error (shows expected columns): {str(schema_error)}"
                        )
                    print("   No data to show columns")

                existing_tables.append(table_name)
            except Exception as e:
                print(f"❌ Table '{table_name}' error: {str(e)}")

        print(f"\n📊 SUMMARY:")
        print(f"Existing tables: {existing_tables}")
        print(f"Missing tables: {set(tables_to_check) - set(existing_tables)}")

        # Check if we can create a simple test table
        print(f"\n🧪 Testing table creation permissions...")
        try:
            # Try to create a simple test table
            test_result = client.rpc("exec", {"sql": "SELECT 1 as test"}).execute()
            print(f"✅ RPC exec function available: {test_result.data}")
        except Exception as e:
            print(f"❌ RPC exec not available: {str(e)}")

        # Check what RPC functions are available
        print(f"\n🔧 Checking available RPC functions...")
        try:
            # This might fail but let's see what we get
            rpc_result = client.rpc("version").execute()
            print(f"✅ Version RPC works: {rpc_result.data}")
        except Exception as e:
            print(f"❌ Version RPC failed: {str(e)}")

    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(check_schema())
