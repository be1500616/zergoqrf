/// Order timeline widget.
/// 
/// This widget displays the order timeline with events, timestamps,
/// and visual indicators in a clean, chronological format.
import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';

import '../../../../shared/utils/app_spacing.dart';
import '../../domain/entities/order_timeline.dart';

/// Visual timeline widget showing order events chronologically.
class OrderTimelineWidget extends StatefulWidget {
  /// Creates an order timeline widget.
  /// 
  /// Args:
  ///   timeline: Order timeline data
  ///   maxEvents: Maximum number of events to show
  ///   compact: Whether to use compact layout
  ///   showAllEvents: Whether to show all events initially
  const OrderTimelineWidget({
    super.key,
    required this.timeline,
    this.maxEvents = 10,
    this.compact = false,
    this.showAllEvents = false,
  });

  /// Order timeline data
  final OrderTimeline timeline;

  /// Maximum number of events to show initially
  final int maxEvents;

  /// Whether to use compact layout
  final bool compact;

  /// Whether to show all events initially
  final bool showAllEvents;

  @override
  State<OrderTimelineWidget> createState() => _OrderTimelineWidgetState();
}

class _OrderTimelineWidgetState extends State<OrderTimelineWidget> {
  bool _showAllEvents = false;

  @override
  void initState() {
    super.initState();
    _showAllEvents = widget.showAllEvents;
  }

  @override
  Widget build(BuildContext context) {
    final events = widget.timeline.events;
    final visibleEvents = _showAllEvents || events.length <= widget.maxEvents
        ? events
        : events.take(widget.maxEvents).toList();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Timeline events
        ...visibleEvents.asMap().entries.map((entry) {
          final index = entry.key;
          final event = entry.value;
          final isLast = index == visibleEvents.length - 1;
          
          return _buildTimelineEvent(
            context,
            event,
            isLast,
            index,
          );
        }),
        
        // Show more/less button
        if (events.length > widget.maxEvents)
          _buildShowMoreButton(context, events.length),
      ],
    );
  }

  Widget _buildTimelineEvent(
    BuildContext context,
    TimelineEvent event,
    bool isLast,
    int index,
  ) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Timeline indicator
        _buildTimelineIndicator(context, event, isLast),
        
        SizedBox(width: widget.compact ? AppSpacing.sm : AppSpacing.md),
        
        // Event content
        Expanded(
          child: _buildEventContent(context, event, index),
        ),
      ],
    ).animate(delay: (index * 100).ms)
     .slideX(begin: -0.2, duration: 400.ms)
     .fadeIn(duration: 400.ms);
  }

  Widget _buildTimelineIndicator(
    BuildContext context,
    TimelineEvent event,
    bool isLast,
  ) {
    final eventColor = _getEventColor(event.type);
    final indicatorSize = widget.compact ? 32.0 : 40.0;
    final iconSize = widget.compact ? 16.0 : 20.0;
    
    return Column(
      children: [
        // Event icon
        Container(
          width: indicatorSize,
          height: indicatorSize,
          decoration: BoxDecoration(
            color: eventColor.withValues(alpha: 0.1),
            shape: BoxShape.circle,
            border: Border.all(
              color: eventColor,
              width: 2,
            ),
          ),
          child: Icon(
            _getEventIcon(event),
            size: iconSize,
            color: eventColor,
          ),
        ),
        
        // Connecting line
        if (!isLast)
          Container(
            width: 2,
            height: widget.compact ? 40 : 50,
            margin: const EdgeInsets.symmetric(vertical: AppSpacing.xs),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
                colors: [
                  eventColor.withValues(alpha: 0.3),
                  eventColor.withValues(alpha: 0.1),
                ],
              ),
            ),
          ),
      ],
    );
  }

  Widget _buildEventContent(
    BuildContext context,
    TimelineEvent event,
    int index,
  ) {
    return Container(
      margin: EdgeInsets.only(
        bottom: widget.compact ? AppSpacing.md : AppSpacing.lg,
      ),
      padding: EdgeInsets.all(
        widget.compact ? AppSpacing.sm : AppSpacing.md,
      ),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: Theme.of(context).colorScheme.outline.withValues(alpha: 0.1),
        ),
        boxShadow: [
          BoxShadow(
            color: Theme.of(context).shadowColor.withValues(alpha: 0.05),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Event header
          Row(
            children: [
              Expanded(
                child: Text(
                  event.title,
                  style: (widget.compact
                      ? Theme.of(context).textTheme.bodyMedium
                      : Theme.of(context).textTheme.titleSmall)?.copyWith(
                    fontWeight: FontWeight.w600,
                    color: _getEventColor(event.type),
                  ),
                ),
              ),
              
              // Timestamp
              Text(
                event.formattedTimestamp,
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.6),
                ),
              ),
            ],
          ),
          
          // Event description
          if (event.description.isNotEmpty) ...[
            SizedBox(height: widget.compact ? AppSpacing.xs : AppSpacing.sm),
            Text(
              event.description,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.8),
                height: 1.4,
              ),
            ),
          ],
          
          // Important event indicator
          if (event.isImportant)
            Container(
              margin: const EdgeInsets.only(top: AppSpacing.sm),
              padding: const EdgeInsets.symmetric(
                horizontal: AppSpacing.sm,
                vertical: AppSpacing.xs,
              ),
              decoration: BoxDecoration(
                color: Colors.amber.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(
                  color: Colors.amber.withValues(alpha: 0.3),
                ),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    Icons.star,
                    size: 14,
                    color: Colors.amber.shade700,
                  ),
                  const SizedBox(width: AppSpacing.xs),
                  Text(
                    'Important',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: Colors.amber.shade700,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildShowMoreButton(BuildContext context, int totalEvents) {
    final remainingEvents = totalEvents - widget.maxEvents;
    
    return Padding(
      padding: const EdgeInsets.only(top: AppSpacing.md),
      child: Center(
        child: TextButton.icon(
          onPressed: () {
            setState(() {
              _showAllEvents = !_showAllEvents;
            });
          },
          icon: Icon(
            _showAllEvents ? Icons.expand_less : Icons.expand_more,
          ),
          label: Text(
            _showAllEvents
                ? 'Show Less'
                : 'Show $remainingEvents More Events',
          ),
          style: TextButton.styleFrom(
            foregroundColor: Theme.of(context).colorScheme.primary,
          ),
        ),
      ),
    );
  }

  Color _getEventColor(TimelineEventType type) {
    return Color(
      int.parse(type.colorHex.substring(1), radix: 16) + 0xFF000000,
    );
  }

  IconData _getEventIcon(TimelineEvent event) {
    // Use custom icon if available, otherwise use type default
    final iconMap = {
      'receipt': Icons.receipt_long,
      'check_circle': Icons.check_circle,
      'restaurant': Icons.restaurant,
      'done_all': Icons.done_all,
      'celebration': Icons.celebration,
      'cancel': Icons.cancel,
      'notifications': Icons.notifications,
      'payment': Icons.payment,
      'info': Icons.info,
      'update': Icons.update,
    };

    return iconMap[event.icon] ?? Icons.circle;
  }
}

/// Compact timeline widget for smaller spaces.
class CompactOrderTimelineWidget extends StatelessWidget {
  /// Creates a compact order timeline widget.
  /// 
  /// Args:
  ///   timeline: Order timeline data
  ///   maxEvents: Maximum number of events to show
  const CompactOrderTimelineWidget({
    super.key,
    required this.timeline,
    this.maxEvents = 5,
  });

  /// Order timeline data
  final OrderTimeline timeline;

  /// Maximum number of events to show
  final int maxEvents;

  @override
  Widget build(BuildContext context) {
    return OrderTimelineWidget(
      timeline: timeline,
      maxEvents: maxEvents,
      compact: true,
    );
  }
}

/// Timeline summary widget showing key milestones.
class TimelineSummaryWidget extends StatelessWidget {
  /// Creates a timeline summary widget.
  /// 
  /// Args:
  ///   timeline: Order timeline data
  ///   showProgress: Whether to show progress indicator
  const TimelineSummaryWidget({
    super.key,
    required this.timeline,
    this.showProgress = true,
  });

  /// Order timeline data
  final OrderTimeline timeline;

  /// Whether to show progress indicator
  final bool showProgress;

  @override
  Widget build(BuildContext context) {
    final importantEvents = timeline.events
        .where((event) => event.isImportant)
        .take(4)
        .toList();

    return Container(
      padding: const EdgeInsets.all(AppSpacing.md),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surfaceContainerLow,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: Theme.of(context).colorScheme.outline.withValues(alpha: 0.1),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Row(
            children: [
              Icon(
                Icons.timeline,
                size: 20,
                color: Theme.of(context).colorScheme.primary,
              ),
              const SizedBox(width: AppSpacing.sm),
              Text(
                'Key Milestones',
                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.w600,
                ),
              ),
              const Spacer(),
              Text(
                '${timeline.totalEvents} events',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.6),
                ),
              ),
            ],
          ),
          
          const SizedBox(height: AppSpacing.md),
          
          // Progress indicator
          if (showProgress && importantEvents.isNotEmpty)
            _buildProgressIndicator(context, importantEvents),
          
          const SizedBox(height: AppSpacing.md),
          
          // Important events
          ...importantEvents.map((event) => _buildSummaryEvent(context, event)),
        ],
      ),
    );
  }

  Widget _buildProgressIndicator(BuildContext context, List<TimelineEvent> events) {
    return Row(
      children: events.asMap().entries.map((entry) {
        final index = entry.key;
        final isLast = index == events.length - 1;
        
        return Expanded(
          child: Row(
            children: [
              Expanded(
                child: Container(
                  height: 4,
                  decoration: BoxDecoration(
                    color: Theme.of(context).colorScheme.primary,
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              ),
              if (!isLast)
                Container(
                  width: 8,
                  height: 8,
                  margin: const EdgeInsets.symmetric(horizontal: AppSpacing.xs),
                  decoration: BoxDecoration(
                    color: Theme.of(context).colorScheme.primary,
                    shape: BoxShape.circle,
                  ),
                ),
            ],
          ),
        );
      }).toList(),
    );
  }

  Widget _buildSummaryEvent(BuildContext context, TimelineEvent event) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: AppSpacing.xs),
      child: Row(
        children: [
          Container(
            width: 6,
            height: 6,
            decoration: BoxDecoration(
              color: Color(
                int.parse(event.type.colorHex.substring(1), radix: 16) + 0xFF000000,
              ),
              shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: AppSpacing.sm),
          Expanded(
            child: Text(
              event.title,
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ),
          Text(
            event.relativeTime,
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
              color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.6),
            ),
          ),
        ],
      ),
    );
  }
}
