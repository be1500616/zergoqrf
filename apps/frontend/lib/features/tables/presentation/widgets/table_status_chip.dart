import 'package:flutter/material.dart';
import '../../domain/entities/table_entities.dart';

class TableStatusChip extends StatelessWidget {
  const TableStatusChip({super.key, required this.status});
  final TableStatus status;

  Color _color(BuildContext context) {
    switch (status) {
      case TableStatus.available:
        return Colors.green;
      case TableStatus.occupied:
        return Colors.red;
      case TableStatus.reserved:
        return Colors.orange;
      case TableStatus.cleaning:
        return Colors.blueGrey;
      case TableStatus.maintenance:
        return Colors.purple;
      case TableStatus.outOfOrder:
        return Colors.grey;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Chip(
      label: Text(status.value),
      backgroundColor: _color(context).withOpacity(0.1),
      labelStyle: TextStyle(color: _color(context)),
      shape: StadiumBorder(side: BorderSide(color: _color(context))),
    );
  }
}

