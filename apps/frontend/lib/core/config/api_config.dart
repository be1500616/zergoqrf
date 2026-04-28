class ApiConfig {
  ApiConfig({String? baseUrl}) : baseUrl = baseUrl ?? _defaultBaseUrl;

  final String baseUrl;

  static const String _defaultBaseUrl = 'http://localhost:8000';

  // For production, this would be set via environment variables
  static const String _productionBaseUrl = 'https://api.zergoqrf.com';
}
