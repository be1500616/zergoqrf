import 'package:flutter/material.dart';
import '../../domain/entities/table_entities.dart' as domain;
import 'table_status_chip.dart';

class TableCard extends StatelessWidget {
  const TableCard({super.key, required this.table, this.onEdit, this.onDelete, this.onChangeStatus});

  final domain.Table table;
  final VoidCallback? onEdit;
  final VoidCallback? onDelete;
  final void Function(domain.TableStatus)? onChangeStatus;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Card(
      elevation: 0,
      clipBehavior: Clip.antiAlias,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12), side: BorderSide(color: theme.dividerColor)),
      child: InkWell(
        onTap: onEdit,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(Icons.table_bar, color: theme.colorScheme.primary),
                  const SizedBox(width: 8),
                  Text('Table ${table.tableNumber}', style: theme.textTheme.titleMedium),
                  const Spacer(),
                  TableStatusChip(status: table.status),
                ],
              ),
              const SizedBox(height: 8),
              Wrap(
                spacing: 12,
                runSpacing: 8,
                children: [
                  _info(Icons.people, '${table.minPartySize}-${table.maxPartySize ?? table.capacity} ppl'),
                  _info(Icons.category, table.category.value),
                  _info(Icons.chair, table.shape.value),
                  if (table.isAccessible) _info(Icons.accessible, 'Accessible'),
                  if (table.hasPowerOutlet) _info(Icons.power, 'Power'),
                  if (table.hasWindowView) _info(Icons.window, 'Window'),
                ],
              ),
              const Spacer(),
              Row(
                children: [
                  TextButton.icon(onPressed: onEdit, icon: const Icon(Icons.edit), label: const Text('Edit')),
                  const SizedBox(width: 8),
                  TextButton.icon(onPressed: onDelete, icon: const Icon(Icons.delete_outline), label: const Text('Delete')),
                  const Spacer(),
                  PopupMenuButton<domain.TableStatus>(
                    icon: const Icon(Icons.sync_alt),
                    tooltip: 'Change Status',
                    onSelected: onChangeStatus,
                    itemBuilder: (context) => domain.TableStatus.values
                        .map((s) => PopupMenuItem(value: s, child: Text('Set ${s.value}')))
                        .toList(),
                  )
                ],
              )
            ],
          ),
        ),
      ),
    );
  }

  Widget _info(IconData icon, String text) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 18),
        const SizedBox(width: 6),
        Text(text),
      ],
    );
  }
}

