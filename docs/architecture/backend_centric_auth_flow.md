# Backend-Centric Authentication Flow

This document outlines an alternative authentication architecture where the FastAPI backend acts as a gateway, managing all interactions with Supabase Auth.

## Authentication Flow Diagram

```mermaid
sequenceDiagram
    participant FlutterApp as Flutter App
    participant FastAPI as FastAPI Backend
    participant Supabase as Supabase Auth

    Note over FlutterApp, FastAPI: 1. User Authentication
    FlutterApp->>FastAPI: User sends credentials (email/pass) to /login endpoint
    FastAPI->>Supabase: Backend uses Admin SDK to sign user in
    Supabase-->>FastAPI: Returns JWT [Access & Refresh Tokens]
    Note over FastAPI: Backend must manage these tokens.
    FastAPI-->>FlutterApp: Returns JWT to the Flutter App

    Note over FlutterApp, FastAPI: 2. Authenticated API Request
    FlutterApp->>FastAPI: Makes API request with JWT in Authorization header

    alt Token is Valid
        Note over FastAPI, Supabase: 3a. Backend Validates Token
        FastAPI->>Supabase: Sends JWT to Supabase for validation
        Supabase-->>FastAPI: Confirms token is valid, returns user data
        FastAPI-->>FlutterApp: Returns API response
    else Token is Expired
        Note over FastAPI, Supabase: 3b. Backend Refreshes Token
        FastAPI->>Supabase: Uses stored Refresh Token to get a new JWT
        Supabase-->>FastAPI: Returns a new, valid JWT
        Note over FastAPI: Backend updates its stored tokens.
        FastAPI-->>FlutterApp: Returns API response (using new token's context)
    else Refresh Fails
        Note over FastAPI: 3c. Backend Rejects Request
        FastAPI-->>FlutterApp: Returns 401 Unauthorized error
        Note over FlutterApp: App must redirect user to login screen.
    end
```

## Summary

While this backend-centric approach is definitely possible, my professional recommendation is to **stick with the direct-to-Supabase model**. It is more secure (credentials are never sent to your backend), more robust (leveraging the official SDKs), and requires significantly less custom code to write and maintain.

However, the final decision is yours. I am equipped to help you plan and implement either architecture.

Given this comparison, which approach would you prefer to move forward with?