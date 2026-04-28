import 'package:get/get.dart';
import 'package:zergo_frontend/features/menu/application/controllers/availability_controller.dart';
import 'package:zergo_frontend/features/menu/application/controllers/menu_items_controller.dart';
import 'package:zergo_frontend/features/menu/application/controllers/menu_management_controller.dart';
import 'package:zergo_frontend/features/menu/application/controllers/menu_preview_controller.dart';
import 'package:zergo_frontend/features/menu/application/controllers/menu_tab_controller.dart';
import 'package:zergo_frontend/features/menu/domain/repositories/menu_repository.dart';
import 'package:zergo_frontend/features/menu/infrastructure/menu_repository_impl.dart';

class MenuBinding extends Bindings {
  @override
  void dependencies() {
    // Repository
    Get.lazyPut<MenuRepository>(() => MenuRepositoryImpl(
          apiConfig: Get.find(),
          authService: Get.find(),
        ));

    // Main controller
    Get.lazyPut(() => MenuManagementController(menuRepository: Get.find()));

    // UI controllers for StatefulWidget migration
    Get.lazyPut(() => MenuTabController(), fenix: true);
    Get.lazyPut(() => MenuPreviewController(), fenix: true);
    Get.lazyPut(() => AvailabilityController(), fenix: true);
    Get.lazyPut(() => MenuItemsController(), fenix: true);
  }
}
