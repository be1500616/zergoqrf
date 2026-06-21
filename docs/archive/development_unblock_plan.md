# Final Plan: Unblocking Feature Development with Parallel Auth Overhaul

This document outlines the final, approved plan. The primary goal is to immediately unblock feature development by implementing a temporary "Development Mode" for authentication, while simultaneously building the robust, production-ready authentication system in a parallel track.

## The Two Tracks

### Track 1: Unblocking Feature Development (Your Focus)

This track is designed to be implemented quickly, giving you the freedom to build and test features without being blocked by authentication.

**Step 1.1: Implement "Dev Auth" Middleware in FastAPI**
*   **Action:** Create a new middleware that activates only in a "development" environment.
*   **Logic:**
    *   It will check for `X-Dev-User-Id` and `X-Dev-Restaurant-Id` headers.
    *   If present, it will bypass all real authentication and create a mock user context from these headers.
    *   If absent, it will fall back to the existing (or future) real authentication logic.

**Step 1.2: Implement Header Injection in Flutter**
*   **Action:** Modify the central HTTP client in the Flutter app.
*   **Logic:**
    *   Create a simple configuration file or class where you can easily set a `devUserId` and `devRestaurantId`.
    *   When the app is in "development" mode, it will automatically add these IDs as `X-Dev-User-Id` and `X-Dev-Restaurant-Id` headers to every outgoing API request.

### Track 2: Building Production-Ready Auth (My Focus)

This track will be executed in the background, following the incremental and secure approach we've discussed.

**Step 2.1: Implement RLS Policies (Immediate Security)**
*   **Action:** Create and apply the foundational Row-Level Security policies to all data tables (`customers`, `orders`, `menu_items`, etc.).
*   **Goal:** Ensure data is protected at the database level, regardless of the authentication method used.

**Step 2.2: Refactor Backend for Supabase JWT Validation**
*   **Action:** Update the FastAPI security dependencies to validate JWTs directly with Supabase.
*   **Goal:** Transition the backend to a stateless, secure token validation model, preparing for the full migration.

**Step 2.3: Migrate Frontend to Direct Supabase Auth**
*   **Action:** Refactor the Flutter `AuthController` to use the `supabase-flutter` library for all authentication actions (login, signup, anonymous sign-in, logout).
*   **Goal:** Fully leverage the official SDK for a secure and seamless user experience.

**Step 2.4: Decommission Old System**
*   **Action:** Once the new system is fully tested and in place, we will:
    *   Turn off the "Development Mode" middleware.
    *   Remove the old custom session tables (`auth_sessions`, `anonymous_sessions`) from the database.
    *   Delete the now-redundant custom session logic from the backend.

---

This two-track plan provides the best of both worlds: immediate development velocity for you, and a clear, secure, and strategic path toward a robust production system for the platform.

I am now ready to begin the implementation. I will start with **Track 2, Step 2.1** (implementing RLS policies) as this provides an immediate and critical security enhancement. I will then proceed to **Track 1** to unblock your development.

I will now switch to "Code" mode.