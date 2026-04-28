# Git Organization Strategy for ZergoQRF

**Generated:** 2025-12-10T07:06:55+05:30

## Executive Summary

The repository currently has:
- **218 changed/untracked files** (74 modified, 144 untracked)
- **Build artifacts and cache files tracked in Git** (should be ignored)
- **Multiple feature branches** that need organization
- **Documentation files** at root level that should be organized

---

## 1. `.gitignore` Analysis & Improvements

### Current Issues Found

#### ✅ **CRITICAL: Build Artifacts Being Tracked**
The following files are currently tracked in Git but should be ignored:

**Python Cache Files:**
- `apps/backend/app/__pycache__/*.pyc`
- `apps/backend/app/common/__pycache__/*.pyc`
- `apps/backend/app/core/__pycache__/*.pyc`
- Multiple other `__pycache__` directories

**Flutter Build Artifacts:**
- `apps/frontend/.dart_tool/` (entire directory)
- `apps/frontend/build/` (entire directory including cache.dill.track.dill)

**Generated Plugin Files:**
- `apps/frontend/ios/Runner/GeneratedPluginRegistrant.m`
- `apps/frontend/linux/flutter/generated_plugin_registrant.cc`
- `apps/frontend/macos/Flutter/GeneratedPluginRegistrant.swift`
- `apps/frontend/windows/flutter/generated_plugin_registrant.cc`

### Recommended `.gitignore` Improvements

```gitignore
# Add these entries to strengthen the .gitignore:

# Python - More comprehensive
*.pyc
*.pyo
*.pyd
__pycache__/
**/__pycache__/
*.so
.Python

# Flutter - Ensure these are properly ignored
.dart_tool/
**/.dart_tool/
build/
**/build/
.flutter-plugins
.flutter-plugins-dependencies
**/.flutter-plugins
**/.flutter-plugins-dependencies

# Generated files that should NEVER be committed
**/GeneratedPluginRegistrant.*
**/generated_plugin_registrant.*
**/.dart_tool/package_config.json
**/.dart_tool/package_config_subset
**/cache.dill.track.dill

# Documentation (temporary/generated)
*_REPORT.md
*_STATUS.md
*_SUMMARY.md
*_PLAN.md
ROUTER_COMPARISON.md
INTEGRATION_*.md

# Test artifacts
**/.pytest_cache/
**/htmlcov/
**/.coverage
coverage.xml
*.cover

# IDE specific
.vscode/settings.json
.vscode/launch.json
.idea/workspace.xml
.idea/tasks.xml
```

---

## 2. Current Repository State Analysis

### Modified Files (74 files)
**Categories:**
1. **Backend Auth System** (13 files)
   - Core auth implementation
   - Supabase integration
   - Security updates

2. **Frontend Restaurant Features** (25 files)
   - Restaurant registration
   - Dashboard
   - Staff management
   - Business verification

3. **Build/Config Files** (36 files)
   - Generated plugin registrants
   - Package configs
   - Build artifacts (should be removed)

### Untracked Files (144 files)
**Categories:**
1. **Documentation** (8 root-level MD files)
2. **Backend Features** (80+ files)
   - Auth system
   - Menu management
   - Orders
   - Cart
   - QR codes
   - Tables
   - Transaction management
3. **Frontend Features** (40+ files)
   - Auth
   - Diner features
   - Menu
   - Order tracking
   - QR
   - Tables
4. **Infrastructure** (15+ files)
   - Supabase migrations
   - Functions
   - Documentation
5. **Testing** (20+ files)
   - Backend tests
   - Frontend tests
   - Integration tests

---

## 3. Proposed Branch & Commit Strategy

### Phase 1: Cleanup (IMMEDIATE)

#### Step 1.1: Remove Tracked Build Artifacts
```bash
# Remove build artifacts from Git tracking
git rm -r --cached apps/backend/app/__pycache__
git rm -r --cached apps/frontend/.dart_tool
git rm -r --cached apps/frontend/build
git rm --cached apps/frontend/ios/Runner/GeneratedPluginRegistrant.m
git rm --cached apps/frontend/linux/flutter/generated_plugin_registrant.cc
git rm --cached apps/frontend/macos/Flutter/GeneratedPluginRegistrant.swift
git rm --cached apps/frontend/windows/flutter/generated_plugin_registrant.cc
git rm --cached apps/frontend/linux/flutter/generated_plugins.cmake
git rm --cached apps/frontend/windows/flutter/generated_plugins.cmake

# Commit the cleanup
git commit -m "chore: remove build artifacts and cache files from git tracking"
```

#### Step 1.2: Update .gitignore
```bash
# Update .gitignore with improvements
# (Apply the recommended improvements above)
git add .gitignore
git commit -m "chore: strengthen .gitignore to prevent build artifacts"
```

### Phase 2: Organize Documentation

#### Step 2.1: Create docs/reports directory
```bash
# Move all status/report files to organized location
mkdir -p docs/reports
git mv AUTH_INTEGRATION_PLAN.md docs/reports/
git mv FINAL_IMPLEMENTATION_REPORT.md docs/reports/
git mv IMPLEMENTATION_STATUS.md docs/reports/
git mv INTEGRATION_QUICK_REFERENCE.md docs/reports/
git mv INTEGRATION_SUMMARY.md docs/reports/
git mv REVISED_IMPLEMENTATION_PLAN.md docs/reports/
git mv ROUTER_COMPARISON.md docs/reports/
git mv TASK_COMPLETION_SUMMARY.md docs/reports/

git commit -m "docs: organize implementation reports into docs/reports/"
```

### Phase 3: Feature-Based Commits

Create separate branches for each major feature area and commit logically grouped changes.

#### Branch 3.1: `feature/backend-auth-complete`
**Purpose:** Complete backend authentication system

**Files to commit:**
- `apps/backend/app/features/auth/` (all new files)
- `apps/backend/app/security.py`
- `apps/backend/app/main.py` (auth-related changes)
- `apps/backend/tests/test_auth*.py`
- `apps/backend/test_auth_endpoints.py`

**Commit sequence:**
```bash
git checkout -b feature/backend-auth-complete
git add apps/backend/app/features/auth/
git commit -m "feat(auth): implement complete authentication system with use cases"

git add apps/backend/app/security.py
git commit -m "feat(auth): add security utilities and token handling"

git add apps/backend/tests/test_auth*.py apps/backend/test_auth_endpoints.py
git commit -m "test(auth): add comprehensive auth test suite"

git add apps/backend/app/main.py
git commit -m "feat(auth): integrate auth router into main application"
```

#### Branch 3.2: `feature/backend-restaurant-api`
**Purpose:** Restaurant management API

**Files to commit:**
- `apps/backend/app/features/restaurants/`
- Related tests

```bash
git checkout main
git checkout -b feature/backend-restaurant-api
git add apps/backend/app/features/restaurants/
git commit -m "feat(restaurants): implement restaurant management API"

git add apps/backend/tests/test_restaurant*.py
git commit -m "test(restaurants): add restaurant API tests"
```

#### Branch 3.3: `feature/backend-menu-orders`
**Purpose:** Menu and order management

**Files to commit:**
- `apps/backend/app/features/menu/`
- `apps/backend/app/features/orders/`
- `apps/backend/app/features/cart/`
- Related tests

```bash
git checkout main
git checkout -b feature/backend-menu-orders
git add apps/backend/app/features/menu/
git commit -m "feat(menu): implement menu management system"

git add apps/backend/app/features/orders/
git commit -m "feat(orders): implement order management system"

git add apps/backend/app/features/cart/
git commit -m "feat(cart): implement shopping cart functionality"
```

#### Branch 3.4: `feature/backend-qr-tables`
**Purpose:** QR code and table management

**Files to commit:**
- `apps/backend/app/features/qr/`
- `apps/backend/app/features/tables/`
- Related tests

```bash
git checkout main
git checkout -b feature/backend-qr-tables
git add apps/backend/app/features/qr/
git commit -m "feat(qr): implement QR code generation and management"

git add apps/backend/app/features/tables/
git commit -m "feat(tables): implement table management system"
```

#### Branch 3.5: `feature/backend-transactions`
**Purpose:** Transaction and order tracking

**Files to commit:**
- `apps/backend/app/features/transaction_management/`
- `apps/backend/app/features/order_tracking/`
- `apps/backend/app/features/public_menu/`

```bash
git checkout main
git checkout -b feature/backend-transactions
git add apps/backend/app/features/transaction_management/
git commit -m "feat(transactions): implement transaction management"

git add apps/backend/app/features/order_tracking/
git commit -m "feat(tracking): implement order tracking system"

git add apps/backend/app/features/public_menu/
git commit -m "feat(menu): implement public menu access"
```

#### Branch 3.6: `feature/frontend-restaurant-dashboard`
**Purpose:** Restaurant owner dashboard and management

**Files to commit:**
- `apps/frontend/lib/features/restaurants/` (all changes)
- `apps/frontend/lib/core/` (new files)
- `apps/frontend/lib/shared/`

```bash
git checkout main
git checkout -b feature/frontend-restaurant-dashboard
git add apps/frontend/lib/features/restaurants/
git commit -m "feat(restaurants): implement restaurant dashboard and onboarding"

git add apps/frontend/lib/core/
git commit -m "feat(core): add core app infrastructure and services"

git add apps/frontend/lib/shared/
git commit -m "feat(shared): add shared widgets and utilities"
```

#### Branch 3.7: `feature/frontend-auth`
**Purpose:** Frontend authentication

**Files to commit:**
- `apps/frontend/lib/features/auth/`
- Related auth services

```bash
git checkout main
git checkout -b feature/frontend-auth
git add apps/frontend/lib/features/auth/
git commit -m "feat(auth): implement frontend authentication flow"
```

#### Branch 3.8: `feature/frontend-diner-experience`
**Purpose:** Diner/customer features

**Files to commit:**
- `apps/frontend/lib/features/diner/`
- `apps/frontend/lib/features/menu/`
- `apps/frontend/lib/features/order_tracking/`
- `apps/frontend/lib/features/qr/`

```bash
git checkout main
git checkout -b feature/frontend-diner-experience
git add apps/frontend/lib/features/diner/
git commit -m "feat(diner): implement diner experience features"

git add apps/frontend/lib/features/menu/
git commit -m "feat(menu): implement menu browsing for diners"

git add apps/frontend/lib/features/order_tracking/
git commit -m "feat(tracking): implement order tracking for diners"

git add apps/frontend/lib/features/qr/
git commit -m "feat(qr): implement QR code scanning"
```

#### Branch 3.9: `feature/infrastructure-migrations`
**Purpose:** Database migrations and infrastructure

**Files to commit:**
- `infra/supabase/migrations/` (all new migrations)
- `infra/supabase/functions/`
- `infra/supabase/seeds/seed.sql`

```bash
git checkout main
git checkout -b feature/infrastructure-migrations
git add infra/supabase/migrations/
git commit -m "feat(db): add comprehensive database migrations"

git add infra/supabase/functions/
git commit -m "feat(infra): add Supabase edge functions"

git add infra/supabase/seeds/seed.sql
git commit -m "feat(db): update seed data"
```

#### Branch 3.10: `feature/testing-infrastructure`
**Purpose:** Testing setup and configuration

**Files to commit:**
- `apps/backend/pytest.ini`
- `apps/backend/conftest.py`
- `apps/frontend/test/` (new structure)
- `.github/workflows/test.yml`
- `.codecov.yml`

```bash
git checkout main
git checkout -b feature/testing-infrastructure
git add apps/backend/pytest.ini apps/backend/conftest.py
git commit -m "test: configure pytest for backend testing"

git add apps/frontend/test/
git commit -m "test: add frontend test infrastructure"

git add .github/workflows/test.yml .codecov.yml
git commit -m "ci: add automated testing workflow"
```

#### Branch 3.11: `feature/dev-tooling`
**Purpose:** Development tools and scripts

**Files to commit:**
- `apps/backend/Makefile`
- `apps/frontend/Makefile`
- `apps/backend/start_backend.py`
- `apps/frontend/start_frontend.sh`
- `apps/frontend/start_diner_testing.sh`
- `scripts/`
- Root `Makefile` updates

```bash
git checkout main
git checkout -b feature/dev-tooling
git add apps/backend/Makefile apps/backend/start_backend.py
git commit -m "chore: add backend development tooling"

git add apps/frontend/Makefile apps/frontend/start_frontend.sh apps/frontend/start_diner_testing.sh
git commit -m "chore: add frontend development scripts"

git add scripts/
git commit -m "chore: add project-wide development scripts"

git add Makefile
git commit -m "chore: update root Makefile with new commands"
```

#### Branch 3.12: `feature/config-updates`
**Purpose:** Configuration and dependency updates

**Files to commit:**
- `apps/backend/pyproject.toml`
- `apps/frontend/pubspec.yaml`
- `apps/frontend/pubspec.lock`
- `docker-compose.yml`
- Environment files

```bash
git checkout main
git checkout -b feature/config-updates
git add apps/backend/pyproject.toml
git commit -m "chore(deps): update backend dependencies"

git add apps/frontend/pubspec.yaml apps/frontend/pubspec.lock
git commit -m "chore(deps): update frontend dependencies"

git add docker-compose.yml
git commit -m "chore(docker): update docker-compose configuration"
```

---

## 4. Testing Strategy

### Before Each Branch Merge

#### Backend Testing
```bash
cd apps/backend
# Run tests
pytest tests/ -v

# Check code quality
ruff check .
mypy .

# Ensure server starts
python start_backend.py
```

#### Frontend Testing
```bash
cd apps/frontend
# Run tests
flutter test

# Check for issues
flutter analyze

# Ensure app builds
flutter build web --release
```

### Integration Testing
```bash
# Start all services
docker-compose up -d

# Run integration tests
cd apps/backend
pytest tests/integration/ -v

cd ../frontend
flutter test integration_test/
```

---

## 5. Merge Strategy

### Recommended Order

1. **Phase 1 (Cleanup)** → Merge to `main` immediately
2. **Phase 2 (Documentation)** → Merge to `main` immediately
3. **Infrastructure** → Merge first (database foundation)
4. **Backend Auth** → Critical for all other features
5. **Backend Restaurant API** → Core business logic
6. **Backend Menu/Orders** → Depends on restaurants
7. **Backend QR/Tables** → Depends on restaurants
8. **Backend Transactions** → Depends on orders
9. **Frontend Auth** → Parallel with backend features
10. **Frontend Restaurant Dashboard** → After backend restaurant API
11. **Frontend Diner Experience** → After menu/orders backend
12. **Testing Infrastructure** → Can be parallel
13. **Dev Tooling** → Can be parallel
14. **Config Updates** → Last (ensures all deps are correct)

### Merge Commands
```bash
# For each feature branch:
git checkout main
git pull origin main
git merge --no-ff feature/branch-name
git push origin main

# Or use Pull Requests for review
git push origin feature/branch-name
# Then create PR on GitHub
```

---

## 6. Post-Merge Cleanup

```bash
# Delete merged branches locally
git branch -d feature/backend-auth-complete
git branch -d feature/backend-restaurant-api
# ... etc

# Delete remote branches
git push origin --delete feature/backend-auth-complete
# ... etc

# Clean up
git gc
git prune
```

---

## 7. Quick Reference Commands

### Check what's changed
```bash
git status
git diff --stat
git diff --name-only
```

### See what's tracked that shouldn't be
```bash
git ls-files | grep -E "(\.pyc$|__pycache__|build/|\.dart_tool/)"
```

### Remove from tracking without deleting
```bash
git rm -r --cached <file-or-directory>
```

### Create and switch to new branch
```bash
git checkout -b feature/my-feature
```

### Stage specific files
```bash
git add <file1> <file2>
```

### Commit with message
```bash
git commit -m "type(scope): description"
```

### Push branch to remote
```bash
git push origin feature/my-feature
```

---

## 8. Commit Message Convention

Use conventional commits format:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting, missing semicolons, etc
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `test`: Adding missing tests
- `chore`: Maintenance tasks
- `ci`: CI/CD changes

**Scopes:**
- `auth`, `restaurants`, `menu`, `orders`, `cart`, `qr`, `tables`, `tracking`, `transactions`
- `frontend`, `backend`, `infra`, `db`
- `deps`, `config`, `docker`

**Examples:**
```
feat(auth): implement JWT token refresh mechanism
fix(restaurants): correct validation for business hours
docs(api): add OpenAPI documentation for menu endpoints
test(orders): add integration tests for order creation
chore(deps): update Flutter to 3.16.0
```

---

## 9. Risk Mitigation

### Backup Before Starting
```bash
# Create a backup branch
git checkout -b backup-before-reorganization
git push origin backup-before-reorganization
git checkout main
```

### If Something Goes Wrong
```bash
# Reset to backup
git reset --hard backup-before-reorganization

# Or reset specific files
git checkout HEAD -- <file>
```

### Verify Each Step
```bash
# After each commit, verify:
git log --oneline -5
git diff HEAD~1
git show HEAD
```

---

## 10. Timeline Estimate

- **Phase 1 (Cleanup):** 30 minutes
- **Phase 2 (Documentation):** 15 minutes
- **Phase 3 (Feature Branches):** 4-6 hours
  - Each branch: 20-40 minutes
  - Testing between branches: 10-15 minutes each
- **Merging & Cleanup:** 1-2 hours
- **Total:** ~6-9 hours of focused work

**Recommendation:** Spread over 2-3 days, testing thoroughly between phases.

---

## Next Steps

1. ✅ Review this strategy
2. ⬜ Apply `.gitignore` improvements
3. ⬜ Execute Phase 1 (Cleanup)
4. ⬜ Execute Phase 2 (Documentation)
5. ⬜ Create feature branches one by one
6. ⬜ Test each feature independently
7. ⬜ Merge in recommended order
8. ⬜ Clean up merged branches
9. ⬜ Update team/documentation

---

**Note:** This is a comprehensive strategy. Feel free to adjust based on your specific needs and priorities. The key is to keep commits logical, atomic, and well-tested.
