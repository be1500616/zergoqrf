"""Pre-flight validation script for authentication system.

This script validates that all required configuration and connectivity
is in place before running end-to-end tests.
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.common.supabase_client import get_supabase
from supabase import Client


def check_environment_variables():
    """Check that all required environment variables are set."""
    print("=" * 60)
    print("CHECKING ENVIRONMENT VARIABLES")
    print("=" * 60)
    
    required_vars = {
        "SUPABASE_URL": settings.supabase_url,
        "SUPABASE_ANON_KEY": settings.supabase_anon_key,
        "SUPABASE_SERVICE_ROLE_KEY": settings.supabase_service_role_key,
        "SUPABASE_JWT_SECRET": settings.supabase_jwt_secret,
    }
    
    all_present = True
    for var_name, var_value in required_vars.items():
        if var_value:
            print(f"✓ {var_name}: {'*' * 20} (set)")
        else:
            print(f"✗ {var_name}: NOT SET")
            all_present = False
    
    print()
    return all_present


def check_supabase_connectivity():
    """Check that we can connect to Supabase."""
    print("=" * 60)
    print("CHECKING SUPABASE CONNECTIVITY")
    print("=" * 60)
    
    try:
        client: Client = get_supabase()
        print(f"✓ Supabase client created successfully")
        print(f"  URL: {settings.supabase_url}")
        
        # Try a simple query to verify connectivity
        try:
            # Query the auth.users table (should work with service role key)
            result = client.table("users").select("id").limit(1).execute()
            print(f"✓ Successfully queried users table")
            print(f"  Found {len(result.data)} users (limited to 1)")
            return True
        except Exception as e:
            print(f"✗ Failed to query users table: {str(e)}")
            print(f"  This might be okay if the table doesn't exist yet")
            # Try to check if we can at least access the database
            try:
                # Try to list tables
                result = client.rpc("get_schema_version").execute()
                print(f"✓ Can execute RPC functions")
                return True
            except Exception as e2:
                print(f"✗ Cannot execute RPC functions: {str(e2)}")
                return False
    except Exception as e:
        print(f"✗ Failed to create Supabase client: {str(e)}")
        return False


def check_database_tables():
    """Check that required database tables exist."""
    print("=" * 60)
    print("CHECKING DATABASE TABLES")
    print("=" * 60)
    
    try:
        client: Client = get_supabase()
        
        # List of tables we expect to exist
        expected_tables = [
            "users",
            "auth_sessions",
            "restaurants",
        ]
        
        all_exist = True
        for table_name in expected_tables:
            try:
                result = client.table(table_name).select("*").limit(0).execute()
                print(f"✓ Table '{table_name}' exists")
            except Exception as e:
                print(f"✗ Table '{table_name}' not found or not accessible: {str(e)}")
                all_exist = False
        
        print()
        return all_exist
    except Exception as e:
        print(f"✗ Failed to check database tables: {str(e)}")
        print()
        return False


def main():
    """Run all pre-flight checks."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "AUTHENTICATION SYSTEM PRE-FLIGHT CHECK" + " " * 10 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    checks = [
        ("Environment Variables", check_environment_variables),
        ("Supabase Connectivity", check_supabase_connectivity),
        ("Database Tables", check_database_tables),
    ]
    
    results = {}
    for check_name, check_func in checks:
        try:
            results[check_name] = check_func()
        except Exception as e:
            print(f"✗ {check_name} check failed with exception: {str(e)}")
            results[check_name] = False
    
    # Print summary
    print("=" * 60)
    print("PRE-FLIGHT CHECK SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for check_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {check_name}")
        if not passed:
            all_passed = False
    
    print()
    
    if all_passed:
        print("✓ All pre-flight checks passed! Ready to test.")
        return 0
    else:
        print("✗ Some pre-flight checks failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

