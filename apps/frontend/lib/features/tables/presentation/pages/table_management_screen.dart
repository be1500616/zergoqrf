import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../application/controllers/table_controllers.dart';
import '../../domain/entities/table_entities.dart' as domain;
import '../widgets/table_card.dart';
import '../widgets/table_form_dialog.dart';

class TableManagementScreen extends GetView<TableManagementController> {
  const TableManagementScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Table Management'),
        actions: [
          IconButton(
            tooltip: 'Refresh',
            onPressed: controller.refreshList,
            icon: const Icon(Icons.refresh),
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Row(
              children: [
                Expanded(
                  child: TextField(
                    decoration: const InputDecoration(
                      hintText: 'Search tables by number, notes, category...',
                      prefixIcon: Icon(Icons.search),
                    ),
                    onChanged: controller.setQuery,
                  ),
                ),
                const SizedBox(width: 12),
                PopupMenuButton<domain.TableStatus?>(
                  tooltip: 'Filter by status',
                  onSelected: (s) {
                    controller.setStatus(s);
                    controller.loadTables();
                  },
                  itemBuilder: (context) => [
                    const PopupMenuItem(value: null, child: Text('All')),
                    ...domain.TableStatus.values
                        .map((s) => PopupMenuItem(value: s, child: Text(s.value)))
                        .toList(),
                  ],
                  icon: const Icon(Icons.filter_list),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Expanded(
              child: Obx(() {
                if (controller.isLoading) {
                  return const Center(child: CircularProgressIndicator());
                }
                if (controller.error != null) {
                  return Center(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text('Error: ${controller.error}', style: theme.textTheme.bodyLarge),
                        const SizedBox(height: 12),
                        FilledButton.icon(
                          onPressed: controller.loadTables,
                          icon: const Icon(Icons.refresh),
                          label: const Text('Retry'),
                        ),
                      ],
                    ),
                  );
                }
                final tables = controller.tables;
                if (tables.isEmpty) {
                  return const Center(child: Text('No tables yet. Tap + to add.'));
                }
                return LayoutBuilder(builder: (context, c) {
                  final crossAxisCount = c.maxWidth > 1200 ? 4 : c.maxWidth > 800 ? 3 : c.maxWidth > 600 ? 2 : 1;
                  return GridView.builder(
                    gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                      crossAxisCount: crossAxisCount,
                      crossAxisSpacing: 12,
                      mainAxisSpacing: 12,
                      childAspectRatio: 1.6,
                    ),
                    itemCount: tables.length,
                    itemBuilder: (ctx, i) {
                      final t = tables[i];
                      return TableCard(
                        table: t,
                        onEdit: () async {
                          final result = await showDialog<Map<String, dynamic>?>(
                            context: context,
                            builder: (_) => TableFormDialog(initial: t),
                          );
                          if (result != null) {
                            await controller.updateTable(t.id, result);
                          }
                        },
                        onDelete: () async {
                          final yes = await showDialog<bool>(
                            context: context,
                            builder: (_) => AlertDialog(
                              title: const Text('Delete Table'),
                              content: Text('Are you sure you want to delete table ${t.tableNumber}?'),
                              actions: [
                                TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancel')),
                                FilledButton(onPressed: () => Navigator.pop(context, true), child: const Text('Delete')),
                              ],
                            ),
                          );
                          if (yes == true) {
                            await controller.deleteTable(t.id);
                          }
                        },
                        onChangeStatus: (s) => controller.updateStatus(t.id, s),
                      );
                    },
                  );
                });
              }),
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () async {
          final result = await showDialog<Map<String, dynamic>?>(
            context: context,
            builder: (_) => const TableFormDialog(),
          );
          if (result != null) {
            await controller.createTable(
              tableNumber: result['table_number'] as String,
              capacity: result['capacity'] as int,
              category: result['category'] as domain.TableCategory,
              shape: result['shape'] as domain.TableShape,
              minPartySize: result['min_party_size'] as int,
              maxPartySize: result['max_party_size'] as int?,
            );
          }
        },
        icon: const Icon(Icons.add),
        label: const Text('Add Table'),
      ),
    );
  }
}

