import 'package:get/get.dart';
import 'package:zergo_frontend/core/config/api_config.dart';
import 'package:zergo_frontend/core/services/auth_service.dart';
import 'package:zergo_frontend/core/theme/theme_controller.dart';

class CoreBinding extends Bindings {
  @override
  void dependencies() {
    // Initialize theme controller first for app-wide theme management
    Get.put(ThemeController(), permanent: true);

    Get.lazyPut(() => ApiConfig(baseUrl: 'http://localhost:8000'), fenix: true);
    Get.lazyPut(() => AuthService(), fenix: true);
  }
}
