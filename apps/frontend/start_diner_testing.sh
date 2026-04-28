#!/bin/bash

# ZERGO QR - Diner Experience Quick Start Script
# This script sets up and runs the Flutter web app for diner experience testing

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_header() {
    echo ""
    echo -e "${PURPLE}================================${NC}"
    echo -e "${PURPLE} ZERGO QR - Diner Experience${NC}"
    echo -e "${PURPLE}================================${NC}"
    echo ""
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "pubspec.yaml" ]; then
    print_error "Please run this script from the apps/frontend directory"
    echo "Usage: cd apps/frontend && ./start_diner_testing.sh"
    exit 1
fi

print_header

print_info "Setting up ZERGO QR Diner Experience for testing..."

# Check Flutter installation
if ! command -v flutter &> /dev/null; then
    print_error "Flutter is not installed or not in PATH"
    echo "Please install Flutter from https://flutter.dev/docs/get-started/install"
    exit 1
fi

print_success "Flutter installation found"

# Check if Chrome is available
if ! command -v google-chrome &> /dev/null && ! command -v chromium &> /dev/null && ! command -v chrome &> /dev/null; then
    print_warning "Chrome browser not found. Please ensure Chrome is installed for web testing."
fi

print_info "Checking Flutter doctor..."
flutter doctor --disable-analytics > /tmp/flutter_doctor.log 2>&1
if [ $? -eq 0 ]; then
    print_success "Flutter environment is ready"
else
    print_warning "Flutter doctor reported some issues. Check with: flutter doctor"
fi

print_info "Getting Flutter dependencies..."
flutter pub get

if [ $? -ne 0 ]; then
    print_error "Failed to get Flutter dependencies"
    exit 1
fi

print_success "Dependencies installed successfully"

print_info "Enabling web support..."
flutter config --enable-web &> /dev/null

print_success "Web support enabled"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    print_info "Creating .env file for development..."
    cat > .env << EOF
# ZERGO QR Frontend Environment Configuration
FLUTTER_WEB_PORT=3000
ENVIRONMENT=development
USE_MOCK_DATA=true
API_BASE_URL=http://localhost:8000
ENABLE_DEBUG_LOGGING=true
EOF
    print_success ".env file created"
fi

clear

print_header

echo -e "${CYAN}🚀 Starting Flutter Web Application for Diner Testing...${NC}"
echo ""
print_info "Configuration:"
echo "   🎭 Mock Data: ENABLED (no backend required)"
echo "   🌐 Web Port: 3000"
echo "   📱 Target: Chrome browser"
echo "   🔧 Environment: Development"
echo ""

print_info "Available Test URLs:"
echo "   🏠 Home Page: http://localhost:3000/home"
echo "   🍽️ Main Diner: http://localhost:3000/diner/TEST123"
echo "   🪑 Table View: http://localhost:3000/diner/TEST123/table/5"
echo "   🧪 Demo Restaurant: http://localhost:3000/diner/DEMO"
echo ""

print_info "Testing Features Available:"
echo "   ✅ Complete restaurant menu with 20+ items"
echo "   ✅ Category navigation and filtering"
echo "   ✅ Real-time search functionality"
echo "   ✅ Shopping cart with item management"
echo "   ✅ Responsive design testing"
echo "   ✅ Dietary information and allergen display"
echo "   ✅ Mock network delays for realistic UX"
echo ""

print_warning "Starting application... This may take 30-60 seconds..."
echo ""

# Start Flutter web with custom port and open browser
flutter run -d chrome --web-port 3000 --web-browser-flag="--disable-web-security" --web-browser-flag="--user-data-dir=/tmp/chrome_dev_session"

# The script will continue running until the Flutter app is stopped

echo ""
print_info "Application stopped."
print_success "Thanks for testing ZERGO QR Diner Experience!"
echo ""