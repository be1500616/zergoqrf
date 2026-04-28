# Simplified Authentication Flow with Supabase

This document outlines the proposed, simplified authentication architecture that delegates session management entirely to Supabase.

## Authentication Flow Diagram

Here is a diagram illustrating the end-to-end process:

```mermaid
sequenceDiagram
    participant FlutterApp as Flutter App
    participant FastAPI as FastAPI Backend
    participant Supabase as Supabase Auth

    Note over FlutterApp, Supabase: 1. User Authentication
    FlutterApp->>Supabase: User signs in with email/password or OTP
    Supabase-->>FlutterApp: Returns secure JWT [Access & Refresh Tokens]
    Note over FlutterApp: Supabase client library securely stores tokens on the device.

    Note over FlutterApp, FastAPI: 2. Authenticated API Request
    FlutterApp->>FastAPI: Makes API request with JWT in Authorization header
    Note over FastAPI, Supabase: 3. Backend Token Validation
    FastAPI->>Supabase: Sends JWT to Supabase for validation
    Supabase-->>FastAPI: Confirms token is valid and returns user data [user_id, role, etc.]

    Note over FastAPI: 4. Secure Data Access
    FastAPI->>FastAPI: Processes request using the validated user context
    Note over FastAPI: Applies business logic and prepares response.
    FastAPI-->>FlutterApp: Returns response data

    Note over FlutterApp, Supabase: 5. Automatic Token Refresh
    Note right of FlutterApp: When the access token is about to expire...
    FlutterApp->>Supabase: Supabase client automatically uses the refresh token to get a new JWT
    Supabase-->>FlutterApp: Returns a new, valid JWT
    Note right of FlutterApp: This process is seamless and transparent to the user.
```

## Explanation of the Flow

1.  **User Authentication (Client-Side):**
    *   The user interacts with the Flutter app to sign in or sign up.
    *   The Flutter app communicates **directly with Supabase Auth** using the `supabase-flutter` library. It never sends passwords to your FastAPI backend.
    *   Upon successful authentication, Supabase returns a secure JSON Web Token (JWT). The `supabase-flutter` library automatically and securely stores this token on the user's device.

2.  **Authenticated API Request:**
    *   When the Flutter app needs to access a protected route on your backend (e.g., to fetch orders), it retrieves the stored JWT and includes it in the `Authorization` header of the request.

3.  **Backend Token Validation:**
    *   Your FastAPI backend receives the request and extracts the JWT from the header.
    *   It then uses the `supabase-py` library to communicate with the Supabase server, asking, "Is this token valid?"
    *   Supabase verifies the token's signature and expiration. If it's valid, Supabase confirms this and returns the user's data associated with that token (like their unique ID and role).

4.  **Secure Data Access:**
    *   Now that your backend has securely identified the user, it can proceed with its business logic. It uses the `user_id` from Supabase to fetch the correct data from the database, respecting the RLS policies you have in place.

5.  **Automatic Token Refresh:**
    *   The JWTs issued by Supabase have a short lifespan for security. The `supabase-flutter` library automatically handles refreshing these tokens in the background without any manual intervention needed in your code. This ensures the user stays logged in seamlessly.

This architecture simplifies your backend by removing all custom session management code, making it more secure, stateless, and easier to maintain.

Does this explanation clarify how the simplified session management would work?