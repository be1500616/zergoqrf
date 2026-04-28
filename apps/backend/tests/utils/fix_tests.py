#!/usr/bin/env python3
"""Script to fix import paths in test files."""

import re
import os

def fix_test_file(file_path):
    """Fix import paths and AsyncClient usage in test file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix import paths
    content = re.sub(
        r'"apps\.backend\.app\.common\.supabase_client\.get_supabase"',
        '"app.common.supabase_client.get_supabase"',
        content
    )
    
    # Fix AsyncClient usage
    content = re.sub(
        r'AsyncClient\(app=app, base_url="http://test"\)',
        'AsyncClient(app=app, base_url="http://test")',
        content
    )
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Fixed {file_path}")

if __name__ == "__main__":
    test_file = "tests/test_auth.py"
    if os.path.exists(test_file):
        fix_test_file(test_file)
    else:
        print(f"Test file {test_file} not found")
