import '../entities/qr_entities.dart';

abstract class QRRepository {
  Future<QRResponse> generate({required String tableId, Map<String, dynamic>? config});
  Future<BulkQRResponse> generateBulk({required List<String> tableIds, Map<String, dynamic>? config});
  Future<QRPreviewData> preview({required Map<String, dynamic> payload});
  Future<QRManagementGrid> managementGrid();
}

