import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../application/controllers/qr_management_controller.dart';
import '../../domain/entities/qr_entities.dart';
import '../widgets/qr_generation_dialog.dart';
import '../widgets/qr_preview_dialog.dart';

class QRManagementScreen extends GetView<QRManagementController> {
  const QRManagementScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(
        title: const Text('QR Code Management'),
        actions: [
          IconButton(onPressed: controller.loadGrid, icon: const Icon(Icons.refresh)),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Obx(() {
          if (controller.isLoading) return const Center(child: CircularProgressIndicator());
          if (controller.error != null) {
            return Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text('Error: ${controller.error}', style: theme.textTheme.bodyLarge),
                  const SizedBox(height: 12),
                  FilledButton.icon(onPressed: controller.loadGrid, icon: const Icon(Icons.refresh), label: const Text('Retry')),
                ],
              ),
            );
          }
          final grid = controller.grid;
          if (grid == null) return const SizedBox.shrink();
          return Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Text('Generated ${grid.generated}/${grid.total}'),
                  const Spacer(),
                  FilledButton.icon(
                    onPressed: controller.selected.isEmpty
                        ? null
                        : () async {
                            final res = await controller.generateBulk();
                            if (res != null) {
                              if (context.mounted) {
                                ScaffoldMessenger.of(context).showSnackBar(
                                  SnackBar(content: Text('Bulk generated: ${res.count}')),
                                );
                              }
                            }
                          },
                    icon: const Icon(Icons.qr_code_2),
                    label: Text('Generate for ${controller.selected.length} selected'),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Expanded(
                child: LayoutBuilder(builder: (context, c) {
                  final crossAxisCount = c.maxWidth > 1200 ? 4 : c.maxWidth > 900 ? 3 : c.maxWidth > 600 ? 2 : 1;
                  return GridView.builder(
                    gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                      crossAxisCount: crossAxisCount,
                      crossAxisSpacing: 12,
                      mainAxisSpacing: 12,
                      childAspectRatio: 1.8,
                    ),
                    itemCount: grid.tables.length,
                    itemBuilder: (ctx, i) {
                      final t = grid.tables[i];
                      final isSelected = controller.selected.any((e) => e.id == t.id);
                      return Card(
                        child: Padding(
                          padding: const EdgeInsets.all(12),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(children: [
                                Checkbox(
                                  value: isSelected,
                                  onChanged: (_) => controller.toggleSelected(t),
                                ),
                                const SizedBox(width: 8),
                                Text('Table ${t.tableNumber}', style: theme.textTheme.titleMedium),
                                const Spacer(),
                                Icon(t.hasQr ? Icons.check_circle : Icons.info_outline,
                                    color: t.hasQr ? Colors.green : Colors.orange),
                              ]),
                              const Spacer(),
                              Row(children: [
                                TextButton.icon(
                                  onPressed: () async {
                                    final res = await controller.generateForTable(t.id);
                                    if (res != null && context.mounted) {
                                      ScaffoldMessenger.of(context).showSnackBar(
                                        const SnackBar(content: Text('QR generated for table')),
                                      );
                                    }
                                  },
                                  icon: const Icon(Icons.qr_code),
                                  label: Text(t.hasQr ? 'Regenerate' : 'Generate'),
                                ),
                                const SizedBox(width: 8),
                                TextButton.icon(
                                  onPressed: t.hasQr
                                      ? () async {
                                          final preview = await controller.preview({'table_id': t.id});
                                          if (preview != null && context.mounted) {
                                            await showDialog(context: context, builder: (_) => QRPreviewDialog(data: preview));
                                          }
                                        }
                                      : null,
                                  icon: const Icon(Icons.visibility),
                                  label: const Text('Preview'),
                                ),
                              ])
                            ],
                          ),
                        ),
                      );
                    },
                  );
                }),
              )
            ],
          );
        }),
      ),
    );
  }
}

