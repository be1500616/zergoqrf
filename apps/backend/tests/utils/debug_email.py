#!/usr/bin/env python3
"""Debug script to test email validation."""

import sys
import traceback

try:
    from app.features.auth.domain.auth_vos import Email
    from app.features.auth.domain.auth_exceptions import InvalidEmailFormatError
    
    print("Testing email validation...")
    
    # Test valid email
    test_email = "test@example.com"
    print(f"Testing email: {test_email}")
    
    try:
        email_obj = Email(test_email)
        print(f"✅ Email validation successful: {email_obj.value}")
    except InvalidEmailFormatError as e:
        print(f"❌ Email validation failed: {str(e)}")
        print(f"Exception type: {type(e)}")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        print(f"Exception type: {type(e)}")
        traceback.print_exc()
        
    # Test the regex directly
    import re
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    match = re.match(pattern, test_email.strip())
    print(f"Direct regex test: {match is not None}")
    
except ImportError as e:
    print(f"Import error: {str(e)}")
    traceback.print_exc()
except Exception as e:
    print(f"Unexpected error: {str(e)}")
    traceback.print_exc()
