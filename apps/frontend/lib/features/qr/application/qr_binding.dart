import 'package:get/get.dart';
import 'package:zergo_frontend/core/config/api_config.dart';
import 'package:zergo_frontend/core/services/auth_service.dart';
import '../domain/repositories/qr_repositories.dart';
import '../infrastructure/repositories/qr_repositories_impl.dart';
import 'controllers/qr_management_controller.dart';

class QRBinding extends Bindings {
  @override
  void dependencies() {
    if (!Get.isRegistered<ApiConfig>()) Get.put(ApiConfig());
    if (!Get.isRegistered<AuthService>()) Get.put(AuthService());

    Get.lazyPut<QRRepository>(() => QRRepositoryImpl(
          apiConfig: Get.find<ApiConfig>(),
          authService: Get.find<AuthService>(),
        ));
    Get.lazyPut(() => QRManagementController(repository: Get.find<QRRepository>()));
  }
}

