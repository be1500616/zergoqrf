#!/usr/bin/env python3
"""Script to run table management enhancement migration."""

import asyncio
import os
from pathlib import Path
from app.common.supabase_client import get_supabase

async def run_migration():
    """Run the table management enhancement migration."""
    print("Running table management enhancement migration...")
    
    try:
        # Get Supabase client with service role
        client = get_supabase()
        print(f"✅ Connected to Supabase: {type(client)}")
        
        # Get the migration file path
        migration_file = Path(__file__).parent.parent.parent / "infra" / "supabase" / "migrations" / "20250926000001_enhance_table_management.sql"
        
        if not migration_file.exists():
            print(f"❌ Migration file not found: {migration_file}")
            return False
        
        # Read the migration SQL
        with open(migration_file, 'r') as f:
            migration_sql = f.read()
        
        print("📄 Migration SQL loaded")
        
        # Split the SQL into individual statements, handling BEGIN/COMMIT blocks
        statements = []
        current_statement = ""
        in_transaction = False
        
        for line in migration_sql.split('\n'):
            line = line.strip()
            if not line or line.startswith('--'):
                continue
                
            if line.upper() == 'BEGIN;':
                in_transaction = True
                current_statement = ""
                continue
            elif line.upper() == 'COMMIT;':
                if current_statement.strip():
                    statements.append(current_statement.strip())
                in_transaction = False
                current_statement = ""
                continue
            
            current_statement += line + "\n"
            
            if not in_transaction and line.endswith(';'):
                if current_statement.strip():
                    statements.append(current_statement.strip())
                current_statement = ""
        
        # Add any remaining statement
        if current_statement.strip():
            statements.append(current_statement.strip())
        
        print(f"🔧 Executing {len(statements)} SQL statements...")
        
        # Execute each statement
        success_count = 0
        for i, statement in enumerate(statements, 1):
            if statement.strip():
                try:
                    # Show first 100 characters of statement
                    preview = statement.replace('\n', ' ')[:100]
                    print(f"  {i}. Executing: {preview}...")
                    
                    # Use the rpc function to execute raw SQL
                    result = client.rpc('exec_sql', {'sql': statement}).execute()
                    print(f"     ✅ Success")
                    success_count += 1
                except Exception as e:
                    error_msg = str(e)
                    if "already exists" in error_msg.lower() or "duplicate" in error_msg.lower():
                        print(f"     ⚠️  Already exists (skipping): {error_msg}")
                        success_count += 1
                    else:
                        print(f"     ❌ Error: {error_msg}")
                        # Continue with other statements for non-critical errors
        
        print(f"🎉 Migration completed! {success_count}/{len(statements)} statements executed successfully")
        
        # Test if the new tables were created
        test_tables = ['floors', 'table_reservations', 'table_sessions', 'table_maintenance_logs']
        for table_name in test_tables:
            try:
                result = client.table(table_name).select('*').limit(1).execute()
                print(f"✅ {table_name} table is accessible")
            except Exception as e:
                print(f"❌ {table_name} table test failed: {str(e)}")
        
        # Test enhanced tables schema
        try:
            result = client.table('tables').select('id,restaurant_id,table_number,capacity,status,shape,category,floor_id').limit(1).execute()
            print("✅ Enhanced tables schema is accessible")
        except Exception as e:
            print(f"❌ Enhanced tables schema test failed: {str(e)}")
            
        return True
            
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def run_sample_data_migration():
    """Run the sample data migration."""
    print("\nRunning sample data migration...")
    
    try:
        client = get_supabase()
        
        # Get the sample data migration file path
        migration_file = Path(__file__).parent.parent.parent / "infra" / "supabase" / "migrations" / "20250926000002_sample_table_data.sql"
        
        if not migration_file.exists():
            print(f"❌ Sample data migration file not found: {migration_file}")
            return False
        
        # Read the migration SQL
        with open(migration_file, 'r') as f:
            migration_sql = f.read()
        
        print("📄 Sample data migration SQL loaded")
        
        # Split the SQL into individual statements
        statements = []
        current_statement = ""
        in_transaction = False
        
        for line in migration_sql.split('\n'):
            line = line.strip()
            if not line or line.startswith('--'):
                continue
                
            if line.upper() == 'BEGIN;':
                in_transaction = True
                current_statement = ""
                continue
            elif line.upper() == 'COMMIT;':
                if current_statement.strip():
                    statements.append(current_statement.strip())
                in_transaction = False
                current_statement = ""
                continue
            
            current_statement += line + "\n"
            
            if not in_transaction and line.endswith(';'):
                if current_statement.strip():
                    statements.append(current_statement.strip())
                current_statement = ""
        
        # Add any remaining statement
        if current_statement.strip():
            statements.append(current_statement.strip())
        
        print(f"🔧 Executing {len(statements)} sample data statements...")
        
        # Execute each statement
        success_count = 0
        for i, statement in enumerate(statements, 1):
            if statement.strip():
                try:
                    preview = statement.replace('\n', ' ')[:100]
                    print(f"  {i}. Executing: {preview}...")
                    
                    result = client.rpc('exec_sql', {'sql': statement}).execute()
                    print(f"     ✅ Success")
                    success_count += 1
                except Exception as e:
                    error_msg = str(e)
                    if "duplicate" in error_msg.lower() or "already exists" in error_msg.lower():
                        print(f"     ⚠️  Data already exists (skipping): {error_msg}")
                        success_count += 1
                    else:
                        print(f"     ❌ Error: {error_msg}")
        
        print(f"🎉 Sample data migration completed! {success_count}/{len(statements)} statements executed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Sample data migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    async def main():
        print("🚀 Table Management Migration Suite")
        print("===================================")
        
        # Run schema migration
        schema_success = await run_migration()
        
        if schema_success:
            # Run sample data migration
            await run_sample_data_migration()
        else:
            print("❌ Schema migration failed, skipping sample data migration")
    
    asyncio.run(main())
