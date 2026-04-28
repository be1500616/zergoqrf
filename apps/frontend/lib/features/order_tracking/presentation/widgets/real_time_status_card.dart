/// Real-time status card widget.
/// 
/// This widget displays real-time order information with connection status,
/// last update time, and key order metrics in an attractive card format.
import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';

import '../../../../shared/utils/app_spacing.dart';
import '../../../../shared/widgets/enhanced_card.dart';
import '../../domain/entities/order_tracking.dart';

/// Real-time status card showing live order information.
class RealTimeStatusCard extends StatefulWidget {
  /// Creates a real-time status card.
  /// 
  /// Args:
  ///   orderTracking: Order tracking information
  ///   isConnected: Whether real-time connection is active
  ///   lastUpdateTime: Last update timestamp
  ///   showMetrics: Whether to show detailed metrics
  ///   compact: Whether to use compact layout
  const RealTimeStatusCard({
    super.key,
    required this.orderTracking,
    required this.isConnected,
    this.lastUpdateTime,
    this.showMetrics = true,
    this.compact = false,
  });

  /// Order tracking information
  final OrderTracking orderTracking;

  /// Whether real-time connection is active
  final bool isConnected;

  /// Last update timestamp
  final DateTime? lastUpdateTime;

  /// Whether to show detailed metrics
  final bool showMetrics;

  /// Whether to use compact layout
  final bool compact;

  @override
  State<RealTimeStatusCard> createState() => _RealTimeStatusCardState();
}

class _RealTimeStatusCardState extends State<RealTimeStatusCard>
    with TickerProviderStateMixin {
  late AnimationController _connectionController;
  late AnimationController _updateController;
  late Animation<Color?> _connectionColorAnimation;

  @override
  void initState() {
    super.initState();
    
    _connectionController = AnimationController(
      duration: const Duration(milliseconds: 500),
      vsync: this,
    );
    
    _updateController = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );

    _connectionColorAnimation = ColorTween(
      begin: Colors.red,
      end: Colors.green,
    ).animate(CurvedAnimation(
      parent: _connectionController,
      curve: Curves.easeInOut,
    ));

    // Set initial connection state
    if (widget.isConnected) {
      _connectionController.forward();
    }
  }

  @override
  void didUpdateWidget(RealTimeStatusCard oldWidget) {
    super.didUpdateWidget(oldWidget);
    
    // Update connection animation
    if (oldWidget.isConnected != widget.isConnected) {
      if (widget.isConnected) {
        _connectionController.forward();
      } else {
        _connectionController.reverse();
      }
    }

    // Trigger update animation when data changes
    if (oldWidget.lastUpdateTime != widget.lastUpdateTime) {
      _updateController.forward().then((_) {
        _updateController.reverse();
      });
    }
  }

  @override
  void dispose() {
    _connectionController.dispose();
    _updateController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _updateController,
      builder: (context, child) {
        return Transform.scale(
          scale: 1.0 + (_updateController.value * 0.02),
          child: EnhancedCard(
            gradient: _buildCardGradient(context),
            child: Padding(
              padding: EdgeInsets.all(
                widget.compact ? AppSpacing.md : AppSpacing.lg,
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Header with connection status
                  _buildHeader(context),
                  
                  SizedBox(height: widget.compact ? AppSpacing.sm : AppSpacing.md),
                  
                  // Order summary
                  _buildOrderSummary(context),
                  
                  if (widget.showMetrics) ...[
                    SizedBox(height: widget.compact ? AppSpacing.md : AppSpacing.lg),
                    
                    // Metrics row
                    _buildMetricsRow(context),
                  ],
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildHeader(BuildContext context) {
    return Row(
      children: [
        // Live indicator
        AnimatedBuilder(
          animation: _connectionColorAnimation,
          builder: (context, child) {
            return Container(
              width: 12,
              height: 12,
              decoration: BoxDecoration(
                color: _connectionColorAnimation.value,
                shape: BoxShape.circle,
                boxShadow: widget.isConnected
                    ? [
                        BoxShadow(
                          color: Colors.green.withValues(alpha: 0.3),
                          blurRadius: 8,
                          spreadRadius: 2,
                        ),
                      ]
                    : null,
              ),
            );
          },
        ).animate(
          onPlay: (controller) => controller.repeat(reverse: true),
        ).scale(
          begin: const Offset(1.0, 1.0),
          end: const Offset(1.2, 1.2),
          duration: const Duration(milliseconds: 1000),
        ),
        
        const SizedBox(width: AppSpacing.sm),
        
        // Status text
        Text(
          widget.isConnected ? 'Live Updates' : 'Offline',
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.w600,
            color: widget.isConnected ? Colors.green : Colors.red,
          ),
        ),
        
        const Spacer(),
        
        // Last update time
        if (widget.lastUpdateTime != null)
          Text(
            _formatLastUpdateTime(widget.lastUpdateTime!),
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
              color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.6),
            ),
          ),
      ],
    );
  }

  Widget _buildOrderSummary(BuildContext context) {
    return Row(
      children: [
        // Order number
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Order Number',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7),
                ),
              ),
              const SizedBox(height: AppSpacing.xs),
              Text(
                widget.orderTracking.orderNumber,
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.w700,
                ),
              ),
            ],
          ),
        ),
        
        // Status badge
        Container(
          padding: const EdgeInsets.symmetric(
            horizontal: AppSpacing.md,
            vertical: AppSpacing.sm,
          ),
          decoration: BoxDecoration(
            color: _getStatusColor().withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(20),
            border: Border.all(
              color: _getStatusColor().withValues(alpha: 0.3),
            ),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 8,
                height: 8,
                decoration: BoxDecoration(
                  color: _getStatusColor(),
                  shape: BoxShape.circle,
                ),
              ),
              const SizedBox(width: AppSpacing.sm),
              Text(
                widget.orderTracking.currentStatus.displayName,
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  fontWeight: FontWeight.w600,
                  color: _getStatusColor(),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildMetricsRow(BuildContext context) {
    return Row(
      children: [
        // Progress metric
        Expanded(
          child: _buildMetricItem(
            context,
            'Progress',
            '${(widget.orderTracking.overallProgress * 100).round()}%',
            Icons.trending_up,
            _getStatusColor(),
          ),
        ),
        
        // Items metric
        if (widget.orderTracking.itemTracking.isNotEmpty) ...[
          const SizedBox(width: AppSpacing.lg),
          Expanded(
            child: _buildMetricItem(
              context,
              'Items',
              '${widget.orderTracking.servedItemsCount}/${widget.orderTracking.itemTracking.length}',
              Icons.restaurant_menu,
              Theme.of(context).colorScheme.primary,
            ),
          ),
        ],
        
        // ETA metric
        if (widget.orderTracking.estimatedTimeRemainingMinutes != null) ...[
          const SizedBox(width: AppSpacing.lg),
          Expanded(
            child: _buildMetricItem(
              context,
              'ETA',
              _formatETA(widget.orderTracking.estimatedTimeRemainingMinutes!),
              Icons.schedule,
              widget.orderTracking.isOverdue ? Colors.red : Colors.orange,
            ),
          ),
        ],
      ],
    );
  }

  Widget _buildMetricItem(
    BuildContext context,
    String label,
    String value,
    IconData icon,
    Color color,
  ) {
    return Container(
      padding: const EdgeInsets.all(AppSpacing.md),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.05),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: color.withValues(alpha: 0.1),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                icon,
                size: 16,
                color: color,
              ),
              const SizedBox(width: AppSpacing.xs),
              Text(
                label,
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: color,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
          const SizedBox(height: AppSpacing.xs),
          Text(
            value,
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.w700,
              color: color,
            ),
          ),
        ],
      ),
    );
  }

  LinearGradient? _buildCardGradient(BuildContext context) {
    if (!widget.isConnected) return null;
    
    final statusColor = _getStatusColor();
    return LinearGradient(
      begin: Alignment.topLeft,
      end: Alignment.bottomRight,
      colors: [
        statusColor.withValues(alpha: 0.02),
        statusColor.withValues(alpha: 0.05),
      ],
    );
  }

  Color _getStatusColor() {
    return Color(
      int.parse(widget.orderTracking.currentStatus.colorHex.substring(1), radix: 16) + 0xFF000000,
    );
  }

  String _formatLastUpdateTime(DateTime lastUpdate) {
    final now = DateTime.now();
    final difference = now.difference(lastUpdate);
    
    if (difference.inSeconds < 30) {
      return 'Just now';
    } else if (difference.inMinutes < 1) {
      return '${difference.inSeconds}s ago';
    } else if (difference.inMinutes < 60) {
      return '${difference.inMinutes}m ago';
    } else {
      return '${difference.inHours}h ago';
    }
  }

  String _formatETA(int minutes) {
    if (minutes <= 0) {
      return 'Ready';
    } else if (minutes < 60) {
      return '${minutes}m';
    } else {
      final hours = minutes ~/ 60;
      final remainingMinutes = minutes % 60;
      return '${hours}h ${remainingMinutes}m';
    }
  }
}

/// Compact version of the real-time status card for smaller spaces.
class CompactRealTimeStatusCard extends StatelessWidget {
  /// Creates a compact real-time status card.
  /// 
  /// Args:
  ///   orderTracking: Order tracking information
  ///   isConnected: Whether real-time connection is active
  ///   lastUpdateTime: Last update timestamp
  const CompactRealTimeStatusCard({
    super.key,
    required this.orderTracking,
    required this.isConnected,
    this.lastUpdateTime,
  });

  /// Order tracking information
  final OrderTracking orderTracking;

  /// Whether real-time connection is active
  final bool isConnected;

  /// Last update timestamp
  final DateTime? lastUpdateTime;

  @override
  Widget build(BuildContext context) {
    return RealTimeStatusCard(
      orderTracking: orderTracking,
      isConnected: isConnected,
      lastUpdateTime: lastUpdateTime,
      showMetrics: false,
      compact: true,
    );
  }
}

/// Connection status indicator widget.
class ConnectionStatusIndicator extends StatefulWidget {
  /// Creates a connection status indicator.
  /// 
  /// Args:
  ///   isConnected: Whether connection is active
  ///   showLabel: Whether to show text label
  ///   size: Indicator size
  const ConnectionStatusIndicator({
    super.key,
    required this.isConnected,
    this.showLabel = true,
    this.size = 12,
  });

  /// Whether connection is active
  final bool isConnected;

  /// Whether to show text label
  final bool showLabel;

  /// Indicator size
  final double size;

  @override
  State<ConnectionStatusIndicator> createState() => _ConnectionStatusIndicatorState();
}

class _ConnectionStatusIndicatorState extends State<ConnectionStatusIndicator>
    with SingleTickerProviderStateMixin {
  late AnimationController _animationController;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 1000),
      vsync: this,
    );
    
    if (widget.isConnected) {
      _animationController.repeat(reverse: true);
    }
  }

  @override
  void didUpdateWidget(ConnectionStatusIndicator oldWidget) {
    super.didUpdateWidget(oldWidget);
    
    if (oldWidget.isConnected != widget.isConnected) {
      if (widget.isConnected) {
        _animationController.repeat(reverse: true);
      } else {
        _animationController.stop();
        _animationController.reset();
      }
    }
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final color = widget.isConnected ? Colors.green : Colors.red;
    
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        AnimatedBuilder(
          animation: _animationController,
          builder: (context, child) {
            return Container(
              width: widget.size,
              height: widget.size,
              decoration: BoxDecoration(
                color: color,
                shape: BoxShape.circle,
                boxShadow: widget.isConnected
                    ? [
                        BoxShadow(
                          color: color.withValues(alpha: 0.3 + (_animationController.value * 0.3)),
                          blurRadius: 4 + (_animationController.value * 4),
                          spreadRadius: 1 + (_animationController.value * 2),
                        ),
                      ]
                    : null,
              ),
            );
          },
        ),
        
        if (widget.showLabel) ...[
          const SizedBox(width: AppSpacing.sm),
          Text(
            widget.isConnected ? 'Live' : 'Offline',
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
              color: color,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ],
    );
  }
}
