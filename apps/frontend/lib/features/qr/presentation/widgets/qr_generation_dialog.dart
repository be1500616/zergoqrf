import 'package:flutter/material.dart';

class QRGenerationDialog extends StatefulWidget {
  const QRGenerationDialog({super.key});

  @override
  State<QRGenerationDialog> createState() => _QRGenerationDialogState();
}

class _QRGenerationDialogState extends State<QRGenerationDialog> {
  final _formKey = GlobalKey<FormState>();
  int _size = 256;
  String _format = 'png';
  int _border = 4;

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('QR Generation Options'),
      content: Form(
        key: _formKey,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            DropdownButtonFormField<String>(
              value: _format,
              decoration: const InputDecoration(labelText: 'Format'),
              items: const [
                DropdownMenuItem(value: 'png', child: Text('PNG')),
                DropdownMenuItem(value: 'svg', child: Text('SVG')),
              ],
              onChanged: (v) => setState(() => _format = v ?? _format),
            ),
            const SizedBox(height: 12),
            TextFormField(
              initialValue: _size.toString(),
              decoration: const InputDecoration(labelText: 'Size (px)'),
              keyboardType: TextInputType.number,
              onChanged: (v) => _size = int.tryParse(v) ?? 256,
            ),
            const SizedBox(height: 12),
            TextFormField(
              initialValue: _border.toString(),
              decoration: const InputDecoration(labelText: 'Border'),
              keyboardType: TextInputType.number,
              onChanged: (v) => _border = int.tryParse(v) ?? 4,
            ),
          ],
        ),
      ),
      actions: [
        TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
        FilledButton(
          onPressed: () {
            Navigator.pop(context, {
              'format': _format,
              'size': _size,
              'border': _border,
            });
          },
          child: const Text('Apply'),
        ),
      ],
    );
  }
}

