import 'package:supabase_flutter/supabase_flutter.dart';

class AuthService {
  Future<String?> getAccessToken() async {
    final session = Supabase.instance.client.auth.currentSession;
    return session?.accessToken;
  }
}