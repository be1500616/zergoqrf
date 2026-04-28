import 'dart:convert';
import 'package:flutter/material.dart';
import '../../domain/entities/qr_entities.dart';

class QRPreviewDialog extends StatelessWidget {
  const QRPreviewDialog({super.key, required this.data});
  final QRPreviewData data;

  @override
  Widget build(BuildContext context) {
    final bytes = base64Decode(data.pngBase64);
    return AlertDialog(
      title: const Text('QR Preview'),
      content: Image.memory(bytes, width: 240, height: 240, fit: BoxFit.contain),
      actions: [
        TextButton(onPressed: () => Navigator.pop(context), child: const Text('Close')),
      ],
    );
  }
}

