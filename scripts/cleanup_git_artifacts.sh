#!/bin/bash

# Git Cleanup Script - Remove Build Artifacts from Tracking
# This script removes build artifacts and cache files from Git tracking
# without deleting them from your filesystem

set -e  # Exit on error

echo "🧹 Git Cleanup: Removing build artifacts from tracking..."
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to safely remove from git tracking
remove_from_git() {
    local path=$1
    if git ls-files --error-unmatch "$path" > /dev/null 2>&1; then
        echo -e "${YELLOW}Removing from tracking: $path${NC}"
        git rm -r --cached "$path" 2>/dev/null || true
    else
        echo -e "${GREEN}Already untracked: $path${NC}"
    fi
}

echo "📦 Removing Python cache files..."
remove_from_git "apps/backend/app/__pycache__"
remove_from_git "apps/backend/app/common/__pycache__"
remove_from_git "apps/backend/app/core/__pycache__"
remove_from_git "apps/backend/app/features/admin/presentation/__pycache__"
remove_from_git "apps/backend/app/features/auth/presentation/__pycache__"
remove_from_git "apps/backend/app/features/menu/presentation/__pycache__"
remove_from_git "apps/backend/app/features/orders/presentation/__pycache__"

# Remove all .pyc files
find apps/backend -name "*.pyc" -type f | while read file; do
    if git ls-files --error-unmatch "$file" > /dev/null 2>&1; then
        remove_from_git "$file"
    fi
done

echo ""
echo "🎯 Removing Flutter build artifacts..."
remove_from_git "apps/frontend/.dart_tool"
remove_from_git "apps/frontend/build"

echo ""
echo "🔧 Removing generated plugin files..."
remove_from_git "apps/frontend/ios/Runner/GeneratedPluginRegistrant.m"
remove_from_git "apps/frontend/linux/flutter/generated_plugin_registrant.cc"
remove_from_git "apps/frontend/linux/flutter/generated_plugins.cmake"
remove_from_git "apps/frontend/macos/Flutter/GeneratedPluginRegistrant.swift"
remove_from_git "apps/frontend/windows/flutter/generated_plugin_registrant.cc"
remove_from_git "apps/frontend/windows/flutter/generated_plugins.cmake"

echo ""
echo "📝 Checking git status..."
git status --short

echo ""
echo -e "${GREEN}✅ Cleanup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Review the changes with: git status"
echo "2. Commit the cleanup: git commit -m 'chore: remove build artifacts from git tracking'"
echo "3. The improved .gitignore will prevent these files from being tracked again"
echo ""
