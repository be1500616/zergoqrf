#!/bin/bash

# ZERGO QR Frontend Startup Script
# Comprehensive Flutter web app startup with checks and optimizations

set -e

echo "🚀 ZERGO QR Frontend Startup"
echo "============================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if Flutter is installed
echo "🔍 Checking Flutter installation..."
if ! command -v flutter &> /dev/null; then
    print_error "Flutter is not installed or not in PATH"
    echo "Please install Flutter from https://flutter.dev/docs/get-started/install"
    exit 1
fi

FLUTTER_VERSION=$(flutter --version | head -n 1)
print_status "Flutter found: $FLUTTER_VERSION"

# Check Flutter doctor
echo ""
echo "🏥 Running Flutter doctor..."
flutter doctor --verbose

# Check if we're in the correct directory
if [ ! -f "pubspec.yaml" ]; then
    print_error "pubspec.yaml not found. Please run this script from the Flutter project root."
    exit 1
fi

print_status "Found pubspec.yaml"

# Clean previous builds
echo ""
echo "🧹 Cleaning previous builds..."
flutter clean
print_status "Clean completed"

# Get dependencies
echo ""
echo "📦 Getting Flutter dependencies..."
flutter pub get
if [ $? -eq 0 ]; then
    print_status "Dependencies installed successfully"
else
    print_error "Failed to install dependencies"
    exit 1
fi

# Check for web support
echo ""
echo "🌐 Checking web support..."
if flutter devices | grep -q "Chrome"; then
    print_status "Web support available"
else
    print_warning "Web support not detected, enabling..."
    flutter config --enable-web
fi

# Build for web (development)
echo ""
echo "🔨 Building for web (development mode)..."
flutter build web --debug
if [ $? -eq 0 ]; then
    print_status "Web build completed successfully"
else
    print_error "Web build failed"
    exit 1
fi

# Check backend connectivity
echo ""
echo "🔗 Checking backend connectivity..."
BACKEND_URL="http://localhost:8000"
if curl -s "$BACKEND_URL/healthz" > /dev/null; then
    print_status "Backend is accessible at $BACKEND_URL"
else
    print_warning "Backend not accessible at $BACKEND_URL"
    print_info "Make sure to start the backend server first:"
    print_info "  cd /path/to/repo && make backend-local"
fi

# Parse command line arguments
PORT=3000
OPEN_BROWSER=true
DEVICE="chrome"

while [[ $# -gt 0 ]]; do
    case $1 in
        --port)
            PORT="$2"
            shift 2
            ;;
        --no-browser)
            OPEN_BROWSER=false
            shift
            ;;
        --device)
            DEVICE="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --port PORT        Port to run on (default: 3000)"
            echo "  --no-browser       Don't open browser automatically"
            echo "  --device DEVICE    Device to run on (default: chrome)"
            echo "  --help             Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Start the development server
echo ""
echo "🚀 Starting Flutter web development server..."
echo "   Port: $PORT"
echo "   Device: $DEVICE"
echo "   Auto-open browser: $OPEN_BROWSER"
echo ""
print_info "🌐 App will be available at: http://localhost:$PORT"
print_info "📱 Diner experience: http://localhost:$PORT/diner/TEST123"
print_info "🏠 Admin dashboard: http://localhost:$PORT/dashboard"
echo ""
print_info "Press Ctrl+C to stop the server"
echo ""

# Build the flutter run command
FLUTTER_CMD="flutter run -d $DEVICE --web-port $PORT"

if [ "$OPEN_BROWSER" = false ]; then
    FLUTTER_CMD="$FLUTTER_CMD --no-web-browser-launch"
fi

# Execute the command
exec $FLUTTER_CMD
