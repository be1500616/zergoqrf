/// Mock services using mocktail for advanced testing scenarios.
///
/// This module provides mock implementations using mocktail for
/// more sophisticated testing scenarios with verification capabilities.
library;

import 'package:mocktail/mocktail.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

// Mock classes for external services
class MockSupabaseClient extends Mock implements SupabaseClient {}

class MockSupabaseAuthClient extends Mock implements GoTrueClient {}

class MockUser extends Mock implements User {}

class MockSession extends Mock implements Session {}

class MockSupabaseQueryBuilder extends Mock implements SupabaseQueryBuilder {}

class MockPostgrestQueryBuilder extends Mock
    implements PostgrestFilterBuilder<PostgrestList> {}

/// Setup helpers for mock services
class MockServiceSetup {
  /// Setup authenticated Supabase client
  static MockSupabaseClient setupAuthenticatedClient({
    String userId = 'test-user-id',
    String userEmail = 'test@example.com',
  }) {
    final mockClient = MockSupabaseClient();
    final mockAuth = MockSupabaseAuthClient();
    final mockUser = MockUser();
    final mockSession = MockSession();

    // Setup user mock
    when(() => mockUser.id).thenReturn(userId);
    when(() => mockUser.email).thenReturn(userEmail);

    // Setup session mock
    when(() => mockSession.user).thenReturn(mockUser);
    when(() => mockSession.accessToken).thenReturn('mock-access-token');

    // Setup auth mock
    when(() => mockAuth.currentSession).thenReturn(mockSession);
    when(() => mockAuth.currentUser).thenReturn(mockUser);

    // Setup client mock
    when(() => mockClient.auth).thenReturn(mockAuth);

    return mockClient;
  }

  /// Setup unauthenticated Supabase client
  static MockSupabaseClient setupUnauthenticatedClient() {
    final mockClient = MockSupabaseClient();
    final mockAuth = MockSupabaseAuthClient();

    // Setup auth mock for unauthenticated state
    when(() => mockAuth.currentSession).thenReturn(null);
    when(() => mockAuth.currentUser).thenReturn(null);

    // Setup client mock
    when(() => mockClient.auth).thenReturn(mockAuth);

    return mockClient;
  }

  /// Setup Supabase client with sign in capability
  static MockSupabaseClient setupClientWithSignIn({
    bool shouldSucceed = true,
    String? errorMessage,
  }) {
    final mockClient = setupUnauthenticatedClient();
    final mockAuth = mockClient.auth as MockSupabaseAuthClient;

    if (shouldSucceed) {
      final mockUser = MockUser();
      final mockSession = MockSession();

      when(() => mockUser.id).thenReturn('signed-in-user-id');
      when(() => mockUser.email).thenReturn('user@example.com');
      when(() => mockSession.user).thenReturn(mockUser);

      when(() => mockAuth.signInWithPassword(
            email: any(named: 'email'),
            password: any(named: 'password'),
          )).thenAnswer((_) async => AuthResponse(
            session: mockSession,
            user: mockUser,
          ));
    } else {
      when(() => mockAuth.signInWithPassword(
            email: any(named: 'email'),
            password: any(named: 'password'),
          )).thenThrow(AuthException(
        errorMessage ?? 'Invalid credentials',
      ));
    }

    return mockClient;
  }

  /// Setup Supabase client with database operations
  static MockSupabaseClient setupClientWithDatabase({
    List<Map<String, dynamic>>? mockData,
  }) {
    final mockClient = MockSupabaseClient();
    final mockAuth = MockSupabaseAuthClient();
    final mockQuery = MockPostgrestQueryBuilder();

    // Setup auth
    when(() => mockClient.auth).thenReturn(mockAuth);
    when(() => mockAuth.currentSession).thenReturn(null);

    // Setup database operations
    final mockSupabaseQueryBuilder = MockSupabaseQueryBuilder();
    when(() => mockClient.from(any())).thenReturn(mockSupabaseQueryBuilder);
    when(() => mockSupabaseQueryBuilder.select(any())).thenReturn(mockQuery);

    // Setup query operations
    when(() => mockQuery.eq(any(), any())).thenReturn(mockQuery);
    when(() => mockQuery.order(any(), ascending: any(named: 'ascending')))
        .thenReturn(mockQuery);

    // Setup data return
    final dataToReturn = mockData ??
        [
          {'id': '1', 'name': 'Test Item 1'},
          {'id': '2', 'name': 'Test Item 2'},
        ];

    when(() => mockQuery.then((_) async => dataToReturn));

    return mockClient;
  }
}

/// Mock response builders
class MockResponseBuilder {
  /// Build successful auth response
  static AuthResponse buildSuccessfulAuthResponse({
    String userId = 'test-user',
    String email = 'test@example.com',
  }) {
    final mockUser = MockUser();
    final mockSession = MockSession();

    when(() => mockUser.id).thenReturn(userId);
    when(() => mockUser.email).thenReturn(email);
    when(() => mockSession.user).thenReturn(mockUser);
    when(() => mockSession.accessToken).thenReturn('mock-token');

    return AuthResponse(
      session: mockSession,
      user: mockUser,
    );
  }

  /// Build error auth response
  static AuthException buildAuthError(String message) {
    return AuthException(message);
  }
}
