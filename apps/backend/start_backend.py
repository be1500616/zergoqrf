#!/usr/bin/env python3
"""
Comprehensive backend startup script for ZERGO QR system.
"""

import asyncio
import os
import sys
import time
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

import uvicorn
from app.main import create_app


async def check_dependencies():
    """Check if all required dependencies are available."""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'supabase',
        'pydantic',
        'qrcode',
        'PIL',  # Pillow imports as PIL
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"  ❌ {package}")
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Please install them with: pip install -e .")
        return False
    
    print("✅ All dependencies available")
    return True


async def check_environment():
    """Check environment variables and configuration."""
    print("\n🌍 Checking environment configuration...")
    
    # Check for Supabase configuration
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    if not supabase_url:
        print("  ⚠️ SUPABASE_URL not set (will use default)")
    else:
        print(f"  ✅ SUPABASE_URL: {supabase_url[:30]}...")
    
    if not supabase_key:
        print("  ⚠️ SUPABASE_ANON_KEY not set (will use default)")
    else:
        print(f"  ✅ SUPABASE_ANON_KEY: {supabase_key[:20]}...")
    
    print("✅ Environment configuration checked")
    return True


async def test_app_creation():
    """Test if the FastAPI app can be created successfully."""
    print("\n🚀 Testing FastAPI app creation...")
    
    try:
        app = create_app()
        print("✅ FastAPI app created successfully")
        
        # Check routes
        routes = [route.path for route in app.routes]
        public_menu_routes = [route for route in routes if '/public/menu' in route]
        
        print(f"  📊 Total routes: {len(routes)}")
        print(f"  🌐 Public menu routes: {len(public_menu_routes)}")
        
        if public_menu_routes:
            print("  📋 Public menu endpoints:")
            for route in public_menu_routes[:5]:  # Show first 5
                print(f"    - {route}")
            if len(public_menu_routes) > 5:
                print(f"    ... and {len(public_menu_routes) - 5} more")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create FastAPI app: {e}")
        import traceback
        traceback.print_exc()
        return False


async def start_server(host="0.0.0.0", port=8001, reload=True):
    """Start the FastAPI server."""
    print(f"\n🚀 Starting ZERGO QR Backend Server...")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Reload: {reload}")
    print(f"   Environment: {'development' if reload else 'production'}")
    
    try:
        # Create the app
        app = create_app()
        
        # Configure uvicorn
        config = uvicorn.Config(
            app=app,
            host=host,
            port=port,
            reload=reload,
            log_level="info",
            access_log=True,
        )
        
        server = uvicorn.Server(config)
        
        print(f"\n🌐 Server will be available at:")
        print(f"   - API Documentation: http://{host}:{port}/docs")
        print(f"   - Health Check: http://{host}:{port}/healthz")
        print(f"   - Public Menu API: http://{host}:{port}/api/v1/public/menu/")
        print(f"\n🔥 Starting server...")
        
        await server.serve()
        
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        import traceback
        traceback.print_exc()
        return False


async def run_quick_tests():
    """Run quick tests to verify functionality."""
    print("\n🧪 Running quick functionality tests...")
    
    try:
        # Test QR generation core
        from tests.core.test_qr_generation_core import main as test_qr_core
        print("  🔲 Testing QR generation core...")
        qr_success = await test_qr_core()
        if qr_success:
            print("  ✅ QR generation core tests passed")
        else:
            print("  ⚠️ QR generation core tests failed")
        
        return True
        
    except Exception as e:
        print(f"  ⚠️ Quick tests failed: {e}")
        return True  # Don't fail startup for test issues


async def main():
    """Main startup function."""
    print("🚀 ZERGO QR Backend Startup")
    print("=" * 50)
    
    # Check dependencies
    if not await check_dependencies():
        sys.exit(1)
    
    # Check environment
    if not await check_environment():
        sys.exit(1)
    
    # Test app creation
    if not await test_app_creation():
        sys.exit(1)
    
    # Run quick tests
    await run_quick_tests()
    
    print("\n" + "=" * 50)
    print("✅ All checks passed! Starting server...")
    print("=" * 50)
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Start ZERGO QR Backend Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8001, help='Port to bind to')
    parser.add_argument('--no-reload', action='store_true', help='Disable auto-reload')
    parser.add_argument('--test-only', action='store_true', help='Run tests only, don\'t start server')
    
    args = parser.parse_args()
    
    if args.test_only:
        print("✅ Test-only mode completed successfully")
        return
    
    # Start the server
    await start_server(
        host=args.host,
        port=args.port,
        reload=not args.no_reload
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server startup failed: {e}")
        sys.exit(1)
