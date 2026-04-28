import 'package:get/get.dart';
import 'package:zergo_frontend/core/config/api_config.dart';
import 'package:zergo_frontend/core/services/auth_service.dart';
import '../domain/repositories/table_repositories.dart';
import '../infrastructure/repositories/table_repositories_impl.dart';
import 'controllers/table_controllers.dart';

class TableBinding extends Bindings {
  @override
  void dependencies() {
    // Ensure core dependencies exist
    if (!Get.isRegistered<ApiConfig>()) {
      Get.put(ApiConfig());
    }
    if (!Get.isRegistered<AuthService>()) {
      Get.put(AuthService());
    }

    Get.lazyPut<TableRepository>(() => TableRepositoryImpl(
          apiConfig: Get.find<ApiConfig>(),
          authService: Get.find<AuthService>(),
        ));
    Get.lazyPut(() => TableManagementController(repository: Get.find<TableRepository>()));
  }
}

