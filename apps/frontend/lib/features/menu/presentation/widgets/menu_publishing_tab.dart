/// Menu publishing tab widget.
/// 
/// This widget provides version control and publishing functionality
/// for menu management.

import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../application/controllers/menu_management_controller.dart';
import '../../domain/entities/menu_entities.dart';

class MenuPublishingTab extends StatelessWidget {
  const MenuPublishingTab({super.key});

  @override
  Widget build(BuildContext context) {
    final MenuManagementController controller = Get.find<MenuManagementController>();

    return Obx(() {
      return RefreshIndicator(
        onRefresh: () => controller.loadMenuVersions(),
        child: CustomScrollView(
          slivers: [
            // Current live version section
            SliverToBoxAdapter(
              child: _CurrentVersionSection(controller: controller),
            ),
            
            // Version history section
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Text(
                  'Version History',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                ),
              ),
            ),
            
            // Versions list
            if (controller.menuVersions.isEmpty)
              SliverToBoxAdapter(child: _EmptyVersionsState())
            else
              SliverPadding(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                sliver: SliverList(
                  delegate: SliverChildBuilderDelegate(
                    (context, index) {
                      final version = controller.menuVersions[index];
                      return _VersionCard(
                        version: version,
                        controller: controller,
                      );
                    },
                    childCount: controller.menuVersions.length,
                  ),
                ),
              ),
          ],
        ),
      );
    });
  }
}

class _CurrentVersionSection extends StatelessWidget {
  const _CurrentVersionSection({required this.controller});

  final MenuManagementController controller;

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            Theme.of(context).colorScheme.primaryContainer,
            Theme.of(context).colorScheme.primaryContainer.withOpacity(0.7),
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: Theme.of(context).colorScheme.primary.withOpacity(0.3),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.public,
                color: Theme.of(context).colorScheme.onPrimaryContainer,
              ),
              const SizedBox(width: 8),
              Text(
                'Currently Live',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      color: Theme.of(context).colorScheme.onPrimaryContainer,
                      fontWeight: FontWeight.w600,
                    ),
              ),
              const Spacer(),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: Colors.green,
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  'LIVE',
                  style: Theme.of(context).textTheme.labelSmall?.copyWith(
                        color: Colors.white,
                        fontWeight: FontWeight.w600,
                      ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          if (controller.currentVersion != null) ...[
            Text(
              controller.currentVersion!.versionName,
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    color: Theme.of(context).colorScheme.onPrimaryContainer,
                    fontWeight: FontWeight.w700,
                  ),
            ),
            if (controller.currentVersion!.description != null) ...[
              const SizedBox(height: 4),
              Text(
                controller.currentVersion!.description!,
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: Theme.of(context).colorScheme.onPrimaryContainer.withOpacity(0.8),
                    ),
              ),
            ],
            const SizedBox(height: 12),
            Row(
              children: [
                Icon(
                  Icons.schedule,
                  size: 16,
                  color: Theme.of(context).colorScheme.onPrimaryContainer.withOpacity(0.7),
                ),
                const SizedBox(width: 4),
                Text(
                  'Published ${_formatDate(controller.currentVersion!.publishedAt)}',
                  style: Theme.of(context).textTheme.labelMedium?.copyWith(
                        color: Theme.of(context).colorScheme.onPrimaryContainer.withOpacity(0.7),
                      ),
                ),
              ],
            ),
          ] else ...[
            Text(
              'No Live Version',
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    color: Theme.of(context).colorScheme.onPrimaryContainer,
                    fontWeight: FontWeight.w700,
                  ),
            ),
            const SizedBox(height: 4),
            Text(
              'Create and publish your first menu version',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Theme.of(context).colorScheme.onPrimaryContainer.withOpacity(0.8),
                  ),
            ),
          ],
        ],
      ),
    );
  }

  String _formatDate(DateTime? date) {
    if (date == null) return 'Unknown';
    final now = DateTime.now();
    final difference = now.difference(date);
    
    if (difference.inDays > 0) {
      return '${difference.inDays} days ago';
    } else if (difference.inHours > 0) {
      return '${difference.inHours} hours ago';
    } else if (difference.inMinutes > 0) {
      return '${difference.inMinutes} minutes ago';
    } else {
      return 'Just now';
    }
  }
}

class _EmptyVersionsState extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(32),
      child: Column(
        children: [
          Icon(
            Icons.history_outlined,
            size: 64,
            color: Theme.of(context).colorScheme.outline,
          ),
          const SizedBox(height: 16),
          Text(
            'No Versions Yet',
            style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                  color: Theme.of(context).colorScheme.outline,
                ),
          ),
          const SizedBox(height: 8),
          Text(
            'Create your first menu version to start managing your menu',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: Theme.of(context).colorScheme.outline,
                ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}

class _VersionCard extends StatelessWidget {
  const _VersionCard({
    required this.version,
    required this.controller,
  });

  final MenuVersion version;
  final MenuManagementController controller;

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Version header
            Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        version.versionName,
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                              fontWeight: FontWeight.w600,
                            ),
                      ),
                      if (version.description != null) ...[
                        const SizedBox(height: 4),
                        Text(
                          version.description!,
                          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                color: Theme.of(context).colorScheme.onSurface.withOpacity(0.7),
                              ),
                        ),
                      ],
                    ],
                  ),
                ),
                _StatusChip(status: version.status),
              ],
            ),
            
            const SizedBox(height: 12),
            
            // Version metadata
            Row(
              children: [
                Icon(
                  Icons.schedule,
                  size: 16,
                  color: Theme.of(context).colorScheme.outline,
                ),
                const SizedBox(width: 4),
                Text(
                  'Created ${_formatDate(version.createdAt)}',
                  style: Theme.of(context).textTheme.labelMedium?.copyWith(
                        color: Theme.of(context).colorScheme.outline,
                      ),
                ),
                if (version.publishedAt != null) ...[
                  const SizedBox(width: 16),
                  Icon(
                    Icons.publish,
                    size: 16,
                    color: Theme.of(context).colorScheme.outline,
                  ),
                  const SizedBox(width: 4),
                  Text(
                    'Published ${_formatDate(version.publishedAt)}',
                    style: Theme.of(context).textTheme.labelMedium?.copyWith(
                          color: Theme.of(context).colorScheme.outline,
                        ),
                  ),
                ],
              ],
            ),
            
            const SizedBox(height: 16),
            
            // Actions
            Row(
              children: [
                if (version.status == MenuStatus.draft) ...[
                  ElevatedButton.icon(
                    onPressed: () => _showPublishDialog(context),
                    icon: const Icon(Icons.publish),
                    label: const Text('Publish'),
                  ),
                  const SizedBox(width: 8),
                ],
                if (version.status == MenuStatus.live && !version.isCurrentLive) ...[
                  OutlinedButton.icon(
                    onPressed: () => _showRollbackDialog(context),
                    icon: const Icon(Icons.restore),
                    label: const Text('Rollback'),
                  ),
                  const SizedBox(width: 8),
                ],
                OutlinedButton.icon(
                  onPressed: () => _showPreview(context),
                  icon: const Icon(Icons.preview),
                  label: const Text('Preview'),
                ),
                const Spacer(),
                PopupMenuButton<String>(
                  onSelected: (value) => _handleAction(context, value),
                  itemBuilder: (context) => [
                    const PopupMenuItem(
                      value: 'duplicate',
                      child: ListTile(
                        leading: Icon(Icons.copy_outlined),
                        title: Text('Duplicate'),
                        contentPadding: EdgeInsets.zero,
                      ),
                    ),
                    const PopupMenuItem(
                      value: 'export',
                      child: ListTile(
                        leading: Icon(Icons.download_outlined),
                        title: Text('Export'),
                        contentPadding: EdgeInsets.zero,
                      ),
                    ),
                    if (version.status == MenuStatus.draft) ...[
                      const PopupMenuDivider(),
                      const PopupMenuItem(
                        value: 'delete',
                        child: ListTile(
                          leading: Icon(Icons.delete_outline, color: Colors.red),
                          title: Text('Delete', style: TextStyle(color: Colors.red)),
                          contentPadding: EdgeInsets.zero,
                        ),
                      ),
                    ],
                  ],
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  void _showPublishDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => _PublishDialog(
        version: version,
        controller: controller,
      ),
    );
  }

  void _showRollbackDialog(BuildContext context) {
    Get.dialog(
      AlertDialog(
        title: const Text('Rollback to Version'),
        content: Text(
          'Are you sure you want to rollback to "${version.versionName}"? This will make it the current live version.',
        ),
        actions: [
          TextButton(
            onPressed: () => Get.back(),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () async {
              Get.back();
              await controller.rollbackToVersion(version.id);
            },
            child: const Text('Rollback'),
          ),
        ],
      ),
    );
  }

  void _showPreview(BuildContext context) {
    // TODO: Implement version preview
    Get.snackbar('Coming Soon', 'Version preview will be available soon');
  }

  void _handleAction(BuildContext context, String action) {
    switch (action) {
      case 'duplicate':
        // TODO: Implement duplicate version
        Get.snackbar('Coming Soon', 'Duplicate version will be available soon');
        break;
      case 'export':
        // TODO: Implement export version
        Get.snackbar('Coming Soon', 'Export version will be available soon');
        break;
      case 'delete':
        _showDeleteDialog(context);
        break;
    }
  }

  void _showDeleteDialog(BuildContext context) {
    Get.dialog(
      AlertDialog(
        title: const Text('Delete Version'),
        content: Text(
          'Are you sure you want to delete "${version.versionName}"? This action cannot be undone.',
        ),
        actions: [
          TextButton(
            onPressed: () => Get.back(),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Get.back();
              // TODO: Implement delete version
              Get.snackbar('Coming Soon', 'Delete version will be available soon');
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Theme.of(context).colorScheme.error,
              foregroundColor: Theme.of(context).colorScheme.onError,
            ),
            child: const Text('Delete'),
          ),
        ],
      ),
    );
  }

  String _formatDate(DateTime? date) {
    if (date == null) return 'Unknown';
    final now = DateTime.now();
    final difference = now.difference(date);
    
    if (difference.inDays > 0) {
      return '${difference.inDays} days ago';
    } else if (difference.inHours > 0) {
      return '${difference.inHours} hours ago';
    } else if (difference.inMinutes > 0) {
      return '${difference.inMinutes} minutes ago';
    } else {
      return 'Just now';
    }
  }
}

class _StatusChip extends StatelessWidget {
  const _StatusChip({required this.status});

  final MenuStatus status;

  @override
  Widget build(BuildContext context) {
    Color color;
    String label;

    switch (status) {
      case MenuStatus.draft:
        color = Colors.orange;
        label = 'Draft';
        break;
      case MenuStatus.live:
        color = Colors.green;
        label = 'Live';
        break;
      case MenuStatus.scheduled:
        color = Colors.blue;
        label = 'Scheduled';
        break;
      case MenuStatus.archived:
        color = Colors.grey;
        label = 'Archived';
        break;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(4),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Text(
        label,
        style: Theme.of(context).textTheme.labelSmall?.copyWith(
              color: color,
              fontWeight: FontWeight.w600,
            ),
      ),
    );
  }
}

class _PublishDialog extends StatefulWidget {
  const _PublishDialog({
    required this.version,
    required this.controller,
  });

  final MenuVersion version;
  final MenuManagementController controller;

  @override
  State<_PublishDialog> createState() => _PublishDialogState();
}

class _PublishDialogState extends State<_PublishDialog> {
  bool _publishImmediately = true;
  DateTime? _scheduledDate;
  final _notesController = TextEditingController();

  @override
  void dispose() {
    _notesController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text('Publish "${widget.version.versionName}"'),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Publish options
          RadioListTile<bool>(
            title: const Text('Publish Immediately'),
            subtitle: const Text('Make this version live right now'),
            value: true,
            groupValue: _publishImmediately,
            onChanged: (value) {
              setState(() {
                _publishImmediately = value ?? true;
              });
            },
          ),
          RadioListTile<bool>(
            title: const Text('Schedule for Later'),
            subtitle: const Text('Set a specific date and time'),
            value: false,
            groupValue: _publishImmediately,
            onChanged: (value) {
              setState(() {
                _publishImmediately = value ?? true;
              });
            },
          ),
          
          // Scheduled date picker
          if (!_publishImmediately) ...[
            const SizedBox(height: 16),
            OutlinedButton.icon(
              onPressed: _selectDateTime,
              icon: const Icon(Icons.schedule),
              label: Text(_scheduledDate == null
                  ? 'Select Date & Time'
                  : 'Scheduled for ${_formatDateTime(_scheduledDate!)}'),
            ),
          ],
          
          const SizedBox(height: 16),
          
          // Notes
          TextField(
            controller: _notesController,
            decoration: const InputDecoration(
              labelText: 'Publishing Notes (Optional)',
              hintText: 'Add notes about this publication...',
            ),
            maxLines: 3,
          ),
        ],
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Cancel'),
        ),
        ElevatedButton(
          onPressed: _canPublish() ? _publish : null,
          child: const Text('Publish'),
        ),
      ],
    );
  }

  bool _canPublish() {
    if (_publishImmediately) return true;
    return _scheduledDate != null && _scheduledDate!.isAfter(DateTime.now());
  }

  void _selectDateTime() async {
    final date = await showDatePicker(
      context: context,
      initialDate: DateTime.now().add(const Duration(days: 1)),
      firstDate: DateTime.now(),
      lastDate: DateTime.now().add(const Duration(days: 365)),
    );

    if (date != null) {
      final time = await showTimePicker(
        context: context,
        initialTime: TimeOfDay.now(),
      );

      if (time != null) {
        setState(() {
          _scheduledDate = DateTime(
            date.year,
            date.month,
            date.day,
            time.hour,
            time.minute,
          );
        });
      }
    }
  }

  void _publish() async {
    try {
      await widget.controller.publishMenuVersion(
        widget.version.id,
        publishImmediately: _publishImmediately,
        scheduledPublishAt: _scheduledDate,
        publishNotes: _notesController.text.trim().isEmpty
            ? null
            : _notesController.text.trim(),
      );
      Navigator.of(context).pop();
    } catch (e) {
      // Error handled by controller
    }
  }

  String _formatDateTime(DateTime dateTime) {
    return '${dateTime.day}/${dateTime.month}/${dateTime.year} at ${dateTime.hour}:${dateTime.minute.toString().padLeft(2, '0')}';
  }
}
