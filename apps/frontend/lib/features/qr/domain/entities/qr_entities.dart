/// QR management domain entities.
class QRResponse {
  QRResponse({required this.tableId, required this.qrImageUrl, required this.token});
  final String tableId;
  final String qrImageUrl;
  final String token;

  factory QRResponse.fromJson(Map<String, dynamic> json) => QRResponse(
        tableId: json['table_id'] as String,
        qrImageUrl: json['qr_image_url'] as String,
        token: json['token'] as String,
      );
}

class BulkQRResponse {
  BulkQRResponse({required this.count, required this.downloadUrl});
  final int count;
  final String downloadUrl;

  factory BulkQRResponse.fromJson(Map<String, dynamic> json) => BulkQRResponse(
        count: json['count'] as int? ?? 0,
        downloadUrl: json['download_url'] as String,
      );
}

class QRPreviewData {
  QRPreviewData({required this.svg, required this.pngBase64});
  final String svg;
  final String pngBase64;

  factory QRPreviewData.fromJson(Map<String, dynamic> json) => QRPreviewData(
        svg: json['svg'] as String,
        pngBase64: json['png_base64'] as String,
      );
}

class QRManagementTableInfo {
  QRManagementTableInfo({
    required this.id,
    required this.tableNumber,
    required this.hasQr,
    this.qrImageUrl,
  });
  final String id;
  final String tableNumber;
  final bool hasQr;
  final String? qrImageUrl;

  factory QRManagementTableInfo.fromJson(Map<String, dynamic> json) => QRManagementTableInfo(
        id: json['id'] as String,
        tableNumber: json['table_number'] as String,
        hasQr: json['has_qr'] as bool? ?? false,
        qrImageUrl: json['qr_image_url'] as String?,
      );
}

class QRManagementGrid {
  QRManagementGrid({required this.tables, required this.total, required this.generated});
  final List<QRManagementTableInfo> tables;
  final int total;
  final int generated;

  factory QRManagementGrid.fromJson(Map<String, dynamic> json) => QRManagementGrid(
        tables: ((json['tables'] as List?) ?? [])
            .map((e) => QRManagementTableInfo.fromJson(e as Map<String, dynamic>))
            .toList(),
        total: json['total'] as int? ?? 0,
        generated: json['generated'] as int? ?? 0,
      );
}

