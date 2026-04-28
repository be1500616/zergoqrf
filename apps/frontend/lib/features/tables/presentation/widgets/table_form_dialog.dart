import 'package:flutter/material.dart';
import '../../domain/entities/table_entities.dart' as domain;

class TableFormDialog extends StatefulWidget {
  const TableFormDialog({super.key, this.initial});
  final domain.Table? initial;

  @override
  State<TableFormDialog> createState() => _TableFormDialogState();
}

class _TableFormDialogState extends State<TableFormDialog> {
  final _formKey = GlobalKey<FormState>();
  late final TextEditingController _number;
  late final TextEditingController _capacity;
  domain.TableCategory _category = domain.TableCategory.regular;
  domain.TableShape _shape = domain.TableShape.round;
  int _minParty = 1;
  int? _maxParty;

  @override
  void initState() {
    super.initState();
    _number = TextEditingController(text: widget.initial?.tableNumber ?? '');
    _capacity = TextEditingController(text: widget.initial?.capacity.toString() ?? '4');
    _category = widget.initial?.category ?? domain.TableCategory.regular;
    _shape = widget.initial?.shape ?? domain.TableShape.round;
    _minParty = widget.initial?.minPartySize ?? 1;
    _maxParty = widget.initial?.maxPartySize;
  }

  @override
  void dispose() {
    _number.dispose();
    _capacity.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text(widget.initial == null ? 'Create Table' : 'Edit Table'),
      content: Form(
        key: _formKey,
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextFormField(
                controller: _number,
                decoration: const InputDecoration(labelText: 'Table Number'),
                validator: (v) => (v == null || v.trim().isEmpty) ? 'Required' : null,
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _capacity,
                decoration: const InputDecoration(labelText: 'Capacity'),
                keyboardType: TextInputType.number,
                validator: (v) => (int.tryParse(v ?? '') == null) ? 'Enter a number' : null,
              ),
              const SizedBox(height: 12),
              DropdownButtonFormField<domain.TableCategory>(
                value: _category,
                decoration: const InputDecoration(labelText: 'Category'),
                items: domain.TableCategory.values
                    .map((c) => DropdownMenuItem(value: c, child: Text(c.value)))
                    .toList(),
                onChanged: (v) => setState(() => _category = v ?? _category),
              ),
              const SizedBox(height: 12),
              DropdownButtonFormField<domain.TableShape>(
                value: _shape,
                decoration: const InputDecoration(labelText: 'Shape'),
                items: domain.TableShape.values
                    .map((c) => DropdownMenuItem(value: c, child: Text(c.value)))
                    .toList(),
                onChanged: (v) => setState(() => _shape = v ?? _shape),
              ),
              const SizedBox(height: 12),
              Row(children: [
                Expanded(
                  child: TextFormField(
                    initialValue: _minParty.toString(),
                    decoration: const InputDecoration(labelText: 'Min Party'),
                    keyboardType: TextInputType.number,
                    onChanged: (v) => _minParty = int.tryParse(v) ?? 1,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: TextFormField(
                    initialValue: _maxParty?.toString() ?? '',
                    decoration: const InputDecoration(labelText: 'Max Party (optional)'),
                    keyboardType: TextInputType.number,
                    onChanged: (v) => _maxParty = int.tryParse(v),
                  ),
                ),
              ]),
            ],
          ),
        ),
      ),
      actions: [
        TextButton(onPressed: () => Navigator.of(context).pop(), child: const Text('Cancel')),
        FilledButton(
          onPressed: () {
            if (_formKey.currentState!.validate()) {
              Navigator.of(context).pop({
                'table_number': _number.text.trim(),
                'capacity': int.parse(_capacity.text),
                'category': _category,
                'shape': _shape,
                'min_party_size': _minParty,
                'max_party_size': _maxParty,
              });
            }
          },
          child: const Text('Save'),
        )
      ],
    );
  }
}

