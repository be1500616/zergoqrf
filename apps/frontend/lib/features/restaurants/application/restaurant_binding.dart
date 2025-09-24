/// Restaurant binding for dependency injection.
///
/// This module contains the GetX binding for restaurant dependencies.

import 'package:get/get.dart';

import 'restaurant_controller.dart';

class RestaurantBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut<RestaurantController>(() => RestaurantController());
  }
}
