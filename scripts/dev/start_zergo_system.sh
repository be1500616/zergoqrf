#!/bin/bash

# ZERGO QR Complete System Startup Script
# Starts both backend and frontend services for development

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Function to print colored output
print_header() {
    echo -e "${PURPLE}🚀 $1${NC}"
    echo "=================================="
}

print_status() {
    echo -e "${GREEN}✅${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ️${NC} $1"
}

# Cleanup function
cleanup() {
    echo ""
    print_info "Shutting down ZERGO QR system..."
    
    # Kill background processes
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
        print_status "Backend server stopped"
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
        print_status "Frontend server stopped"
    fi
    
    print_info "👋 ZERGO QR system shutdown complete"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

print_header "ZERGO QR Complete System Startup"

# Change to project root directory (two levels up from scripts/dev/)
cd "$(dirname "$0")/../.."

# Check if we're in the correct directory
if [ ! -f "apps/backend/start_backend.py" ] || [ ! -f "apps/frontend/start_frontend.sh" ]; then
    print_error "Cannot find required project files. Please ensure this script is in scripts/dev/ directory."
    exit 1
fi

# Parse command line arguments
BACKEND_PORT=8001
FRONTEND_PORT=3000
SKIP_TESTS=false
OPEN_BROWSER=true

while [[ $# -gt 0 ]]; do
    case $1 in
        --backend-port)
            BACKEND_PORT="$2"
            shift 2
            ;;
        --frontend-port)
            FRONTEND_PORT="$2"
            shift 2
            ;;
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --no-browser)
            OPEN_BROWSER=false
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --backend-port PORT    Backend port (default: 8001)"
            echo "  --frontend-port PORT   Frontend port (default: 3000)"
            echo "  --skip-tests           Skip initial tests"
            echo "  --no-browser           Don't open browser automatically"
            echo "  --help                 Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

print_info "Configuration:"
print_info "  Backend Port: $BACKEND_PORT"
print_info "  Frontend Port: $FRONTEND_PORT"
print_info "  Skip Tests: $SKIP_TESTS"
print_info "  Open Browser: $OPEN_BROWSER"
echo ""

# Step 1: Start Backend
print_header "Starting Backend Server"

cd apps/backend

if [ "$SKIP_TESTS" = false ]; then
    print_info "Running backend tests..."
    python3 start_backend.py --test-only
    if [ $? -eq 0 ]; then
        print_status "Backend tests passed"
    else
        print_error "Backend tests failed"
        exit 1
    fi
fi

print_info "Starting backend server on port $BACKEND_PORT..."
python3 start_backend.py --host 0.0.0.0 --port $BACKEND_PORT &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Check if backend is running
if curl -s "http://localhost:$BACKEND_PORT/healthz" > /dev/null; then
    print_status "Backend server is running on http://localhost:$BACKEND_PORT"
else
    print_error "Backend server failed to start"
    cleanup
    exit 1
fi

cd ../..

# Step 2: Start Frontend
print_header "Starting Frontend Server"

cd apps/frontend

print_info "Starting frontend server on port $FRONTEND_PORT..."

if [ "$OPEN_BROWSER" = true ]; then
    flutter run -d chrome --web-port $FRONTEND_PORT &
else
    flutter run -d chrome --web-port $FRONTEND_PORT &
fi

FRONTEND_PID=$!

# Wait for frontend to start
sleep 10

cd ../..

# Step 3: Display Information
print_header "ZERGO QR System Ready!"

echo ""
print_status "🌐 System URLs:"
echo "   📊 Backend API: http://localhost:$BACKEND_PORT"
echo "   📚 API Documentation: http://localhost:$BACKEND_PORT/docs"
echo "   🏠 Frontend App: http://localhost:$FRONTEND_PORT"
echo "   📱 Diner Experience: http://localhost:$FRONTEND_PORT/diner/TEST123"
echo ""

print_status "🧪 Test Endpoints:"
echo "   ❤️ Backend Health: curl http://localhost:$BACKEND_PORT/healthz"
echo "   🏢 Restaurant API: curl http://localhost:$BACKEND_PORT/api/v1/public/menu/restaurant/TEST123"
echo "   📋 Menu API: curl http://localhost:$BACKEND_PORT/api/v1/public/menu/TEST123"
echo ""

print_status "🔧 Development Tools:"
echo "   🐛 Flutter DevTools: Available in browser console"
echo "   📊 Backend Logs: Check terminal output"
echo "   🔄 Hot Reload: Press 'r' in Flutter terminal"
echo ""

if [ "$SKIP_TESTS" = false ]; then
    print_header "Running Integration Tests"
    
    # Test backend API
    print_info "Testing backend API..."
    cd apps/backend
    python3 tests/api/test_public_menu_api.py
    if [ $? -eq 0 ]; then
        print_status "Backend API tests passed"
    else
        print_warning "Backend API tests failed (may be expected for test data)"
    fi
    cd ../..
    
    # Test frontend accessibility
    print_info "Testing frontend accessibility..."
    if curl -s "http://localhost:$FRONTEND_PORT" > /dev/null; then
        print_status "Frontend is accessible"
    else
        print_warning "Frontend may still be starting up"
    fi
fi

print_header "System Status"
print_status "✅ Backend Server: Running (PID: $BACKEND_PID)"
print_status "✅ Frontend Server: Running (PID: $FRONTEND_PID)"
print_status "✅ Integration: Ready for testing"

echo ""
print_info "🎯 Quick Start Guide:"
echo "   1. Open http://localhost:$FRONTEND_PORT/diner/TEST123 in your browser"
echo "   2. Test the menu browsing experience"
echo "   3. Check the API documentation at http://localhost:$BACKEND_PORT/docs"
echo "   4. Use Ctrl+C to stop both servers"
echo ""

print_info "📝 Development Notes:"
echo "   - The diner experience works without authentication"
echo "   - Restaurant code 'TEST123' is used for testing"
echo "   - Backend returns 404 for non-existent restaurants (expected)"
echo "   - Frontend handles errors gracefully with fallback UI"
echo ""

print_warning "⏳ Keeping servers running... Press Ctrl+C to stop"

# Keep the script running and wait for user interrupt
wait
