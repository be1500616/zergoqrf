import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

Future<void> initSupabase() async {
  const profile = String.fromEnvironment('APP_PROFILE', defaultValue: 'dev');
  final profileFile = '.env.$profile';

  try {
    await dotenv.load(fileName: profileFile);
  } catch (_) {
    await dotenv.load(fileName: '.env');
  }

  final url = dotenv.env['SUPABASE_URL'] ?? dotenv.env['SUPABASE_${profile.toUpperCase()}_URL'] ?? '';
  final anon =
      dotenv.env['SUPABASE_ANON_KEY'] ?? dotenv.env['SUPABASE_${profile.toUpperCase()}_ANON_KEY'] ?? '';

  if (url.isEmpty || anon.isEmpty) {
    throw StateError('Missing Supabase env vars for profile: $profile');
  }

  await Supabase.initialize(
    url: url,
    anonKey: anon,
  );
}
