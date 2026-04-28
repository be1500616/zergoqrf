#!/usr/bin/env python3
"""
Script to organize scattered test files into proper test structure.
"""

import os
import shutil
from pathlib import Path

def organize_test_files():
    """Organize test files into proper structure."""
    backend_dir = Path(__file__).parent
    tests_dir = backend_dir / "tests"
    
    # Create test directories if they don't exist
    test_dirs = [
        tests_dir / "integration",
        tests_dir / "api",
        tests_dir / "core",
        tests_dir / "migration",
        tests_dir / "utils",
    ]
    
    for test_dir in test_dirs:
        test_dir.mkdir(parents=True, exist_ok=True)
    
    # Files to move and their destinations
    files_to_move = [
        # Integration tests
        ("test_integration_public_menu.py", "integration/test_public_menu_integration.py"),
        ("test_restaurant_api_simple.py", "integration/test_restaurant_api_simple.py"),
        ("run_restaurant_api_tests.py", "integration/run_restaurant_api_tests.py"),
        
        # API tests
        ("test_public_menu_api.py", "api/test_public_menu_api.py"),
        ("test_qr_generation_api.py", "api/test_qr_generation_api.py"),
        ("test_table_management_api.py", "api/test_table_management_api.py"),
        ("test_endpoints.py", "api/test_endpoints.py"),
        
        # Core tests
        ("test_qr_generation_core.py", "core/test_qr_generation_core.py"),
        
        # Migration scripts
        ("apply_qr_migration.py", "migration/apply_qr_migration.py"),
        ("apply_table_migration_direct.py", "migration/apply_table_migration_direct.py"),
        ("run_migration.py", "migration/run_migration.py"),
        ("run_table_management_migration.py", "migration/run_table_management_migration.py"),
        
        # Utility scripts
        ("check_created_user.py", "utils/check_created_user.py"),
        ("check_customers_schema.py", "utils/check_customers_schema.py"),
        ("check_supabase_schema.py", "utils/check_supabase_schema.py"),
        ("debug_email.py", "utils/debug_email.py"),
        ("debug_supabase.py", "utils/debug_supabase.py"),
        ("fix_tests.py", "utils/fix_tests.py"),
        ("start_server_for_testing.py", "utils/start_server_for_testing.py"),
        
        # Auth-related scripts
        ("create_auth_sessions_table.py", "migration/create_auth_sessions_table.py"),
        ("create_auth_sessions_table_v2.py", "migration/create_auth_sessions_table_v2.py"),
        ("create_exec_sql_function.py", "migration/create_exec_sql_function.py"),
    ]
    
    moved_files = []
    skipped_files = []
    
    for source_file, dest_path in files_to_move:
        source_path = backend_dir / source_file
        dest_full_path = tests_dir / dest_path
        
        if source_path.exists():
            try:
                # Create destination directory if it doesn't exist
                dest_full_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Move the file
                shutil.move(str(source_path), str(dest_full_path))
                moved_files.append((source_file, dest_path))
                print(f"✅ Moved {source_file} -> tests/{dest_path}")
            except Exception as e:
                print(f"❌ Failed to move {source_file}: {e}")
                skipped_files.append(source_file)
        else:
            skipped_files.append(source_file)
    
    # Create __init__.py files in test directories
    for test_dir in test_dirs:
        init_file = test_dir / "__init__.py"
        if not init_file.exists():
            init_file.write_text("")
    
    print(f"\n📊 Summary:")
    print(f"✅ Moved {len(moved_files)} files")
    print(f"⚠️ Skipped {len(skipped_files)} files (not found)")
    
    if moved_files:
        print(f"\n📁 Organized test structure:")
        for test_dir in test_dirs:
            if any(test_dir.iterdir()):
                print(f"  tests/{test_dir.name}/")
                for file in test_dir.iterdir():
                    if file.is_file() and file.name != "__init__.py":
                        print(f"    - {file.name}")

if __name__ == "__main__":
    organize_test_files()
