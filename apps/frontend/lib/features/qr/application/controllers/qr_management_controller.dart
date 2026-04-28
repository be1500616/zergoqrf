import 'package:get/get.dart';
import '../../domain/entities/qr_entities.dart';
import '../../domain/repositories/qr_repositories.dart';

class QRManagementController extends GetxController {
  QRManagementController({required this.repository});
  final QRRepository repository;

  final RxBool _loading = false.obs;
  final RxnString _error = RxnString();
  final Rx<QRManagementGrid?> _grid = Rx<QRManagementGrid?>(null);
  final RxList<QRManagementTableInfo> _selection = <QRManagementTableInfo>[].obs;

  bool get isLoading => _loading.value;
  String? get error => _error.value;
  QRManagementGrid? get grid => _grid.value;
  List<QRManagementTableInfo> get selected => _selection;

  @override
  void onInit() {
    super.onInit();
    loadGrid();
  }

  void toggleSelected(QRManagementTableInfo info) {
    if (_selection.any((e) => e.id == info.id)) {
      _selection.removeWhere((e) => e.id == info.id);
    } else {
      _selection.add(info);
    }
  }

  Future<void> loadGrid() async {
    try {
      _loading.value = true;
      _error.value = null;
      _grid.value = await repository.managementGrid();
    } catch (e) {
      _error.value = e.toString();
    } finally {
      _loading.value = false;
    }
  }

  Future<QRResponse?> generateForTable(String tableId) async {
    try {
      _loading.value = true;
      final res = await repository.generate(tableId: tableId);
      await loadGrid();
      return res;
    } catch (e) {
      _error.value = e.toString();
      return null;
    } finally {
      _loading.value = false;
    }
  }

  Future<BulkQRResponse?> generateBulk() async {
    try {
      if (_selection.isEmpty) return null;
      _loading.value = true;
      final resp = await repository.generateBulk(tableIds: _selection.map((e) => e.id).toList());
      await loadGrid();
      _selection.clear();
      return resp;
    } catch (e) {
      _error.value = e.toString();
      return null;
    } finally {
      _loading.value = false;
    }
  }

  Future<QRPreviewData?> preview(Map<String, dynamic> payload) async {
    try {
      _loading.value = true;
      final data = await repository.preview(payload: payload);
      return data;
    } catch (e) {
      _error.value = e.toString();
      return null;
    } finally {
      _loading.value = false;
    }
  }
}

