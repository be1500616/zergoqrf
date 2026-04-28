/// Order status indicator widget.
/// 
/// This widget displays the current order status with a visual progress
/// indicator, estimated time, and status-specific styling.
import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';

import '../../../../shared/utils/app_spacing.dart';
import '../../../../shared/widgets/enhanced_card.dart';
import '../../domain/entities/order_tracking.dart';

/// Visual indicator for order status with progress and timing information.
class OrderStatusIndicator extends StatefulWidget {
  /// Creates an order status indicator.
  /// 
  /// Args:
  ///   currentStatus: Current order status
  ///   progress: Overall progress (0.0 to 1.0)
  ///   estimatedTimeRemaining: Estimated time remaining in minutes
  ///   isOverdue: Whether the order is overdue
  ///   showDetails: Whether to show detailed information
  ///   compact: Whether to use compact layout
  const OrderStatusIndicator({
    super.key,
    required this.currentStatus,
    required this.progress,
    this.estimatedTimeRemaining,
    this.isOverdue = false,
    this.showDetails = true,
    this.compact = false,
  });

  /// Current order status
  final OrderStatus currentStatus;

  /// Overall progress (0.0 to 1.0)
  final double progress;

  /// Estimated time remaining in minutes
  final int? estimatedTimeRemaining;

  /// Whether the order is overdue
  final bool isOverdue;

  /// Whether to show detailed information
  final bool showDetails;

  /// Whether to use compact layout
  final bool compact;

  @override
  State<OrderStatusIndicator> createState() => _OrderStatusIndicatorState();
}

class _OrderStatusIndicatorState extends State<OrderStatusIndicator>
    with TickerProviderStateMixin {
  late AnimationController _progressController;
  late AnimationController _pulseController;
  late Animation<double> _progressAnimation;
  late Animation<double> _pulseAnimation;

  @override
  void initState() {
    super.initState();
    
    _progressController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    );
    
    _pulseController = AnimationController(
      duration: const Duration(milliseconds: 2000),
      vsync: this,
    );

    _progressAnimation = Tween<double>(
      begin: 0.0,
      end: widget.progress,
    ).animate(CurvedAnimation(
      parent: _progressController,
      curve: Curves.easeOutCubic,
    ));

    _pulseAnimation = Tween<double>(
      begin: 1.0,
      end: 1.1,
    ).animate(CurvedAnimation(
      parent: _pulseController,
      curve: Curves.easeInOut,
    ));

    // Start animations
    _progressController.forward();
    
    // Pulse animation for active orders
    if (!widget.currentStatus.isTerminal) {
      _pulseController.repeat(reverse: true);
    }
  }

  @override
  void didUpdateWidget(OrderStatusIndicator oldWidget) {
    super.didUpdateWidget(oldWidget);
    
    // Update progress animation if progress changed
    if (oldWidget.progress != widget.progress) {
      _progressAnimation = Tween<double>(
        begin: oldWidget.progress,
        end: widget.progress,
      ).animate(CurvedAnimation(
        parent: _progressController,
        curve: Curves.easeOutCubic,
      ));
      _progressController.reset();
      _progressController.forward();
    }

    // Update pulse animation based on status
    if (oldWidget.currentStatus.isTerminal != widget.currentStatus.isTerminal) {
      if (widget.currentStatus.isTerminal) {
        _pulseController.stop();
        _pulseController.reset();
      } else {
        _pulseController.repeat(reverse: true);
      }
    }
  }

  @override
  void dispose() {
    _progressController.dispose();
    _pulseController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return EnhancedCard(
      child: Padding(
        padding: EdgeInsets.all(
          widget.compact ? AppSpacing.md : AppSpacing.lg,
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Status header
            _buildStatusHeader(context),
            
            if (widget.showDetails) ...[
              SizedBox(height: widget.compact ? AppSpacing.md : AppSpacing.lg),
              
              // Progress indicator
              _buildProgressIndicator(context),
              
              SizedBox(height: widget.compact ? AppSpacing.md : AppSpacing.lg),
              
              // Status details
              _buildStatusDetails(context),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildStatusHeader(BuildContext context) {
    final statusColor = _getStatusColor();
    
    return Row(
      children: [
        // Status icon with pulse animation
        AnimatedBuilder(
          animation: _pulseAnimation,
          builder: (context, child) {
            return Transform.scale(
              scale: widget.currentStatus.isTerminal ? 1.0 : _pulseAnimation.value,
              child: Container(
                width: widget.compact ? 40 : 48,
                height: widget.compact ? 40 : 48,
                decoration: BoxDecoration(
                  color: statusColor.withValues(alpha: 0.1),
                  shape: BoxShape.circle,
                  border: Border.all(
                    color: statusColor,
                    width: 2,
                  ),
                ),
                child: Icon(
                  _getStatusIcon(),
                  color: statusColor,
                  size: widget.compact ? 20 : 24,
                ),
              ),
            );
          },
        ),
        
        SizedBox(width: widget.compact ? AppSpacing.sm : AppSpacing.md),
        
        // Status text
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                widget.currentStatus.displayName,
                style: (widget.compact 
                    ? Theme.of(context).textTheme.titleMedium
                    : Theme.of(context).textTheme.titleLarge)?.copyWith(
                  fontWeight: FontWeight.w600,
                  color: statusColor,
                ),
              ),
              
              if (widget.showDetails) ...[
                const SizedBox(height: AppSpacing.xs),
                Text(
                  _getStatusDescription(),
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7),
                  ),
                ),
              ],
            ],
          ),
        ),
        
        // Overdue indicator
        if (widget.isOverdue)
          Container(
            padding: const EdgeInsets.symmetric(
              horizontal: AppSpacing.sm,
              vertical: AppSpacing.xs,
            ),
            decoration: BoxDecoration(
              color: Colors.red.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: Colors.red.withValues(alpha: 0.3)),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(
                  Icons.schedule,
                  size: 16,
                  color: Colors.red,
                ),
                const SizedBox(width: AppSpacing.xs),
                Text(
                  'Overdue',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Colors.red,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
          ),
      ],
    );
  }

  Widget _buildProgressIndicator(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Progress bar
        AnimatedBuilder(
          animation: _progressAnimation,
          builder: (context, child) {
            return LinearProgressIndicator(
              value: _progressAnimation.value,
              backgroundColor: Theme.of(context).colorScheme.surfaceContainerHighest,
              valueColor: AlwaysStoppedAnimation<Color>(_getStatusColor()),
              minHeight: widget.compact ? 6 : 8,
            );
          },
        ),
        
        const SizedBox(height: AppSpacing.sm),
        
        // Progress text
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              '${(widget.progress * 100).round()}% Complete',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                fontWeight: FontWeight.w600,
                color: _getStatusColor(),
              ),
            ),
            
            if (widget.estimatedTimeRemaining != null && !widget.isOverdue)
              Text(
                _formatTimeRemaining(widget.estimatedTimeRemaining!),
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7),
                ),
              ),
          ],
        ),
      ],
    );
  }

  Widget _buildStatusDetails(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(AppSpacing.md),
      decoration: BoxDecoration(
        color: _getStatusColor().withValues(alpha: 0.05),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: _getStatusColor().withValues(alpha: 0.1),
        ),
      ),
      child: Row(
        children: [
          Icon(
            Icons.info_outline,
            size: 20,
            color: _getStatusColor(),
          ),
          const SizedBox(width: AppSpacing.sm),
          Expanded(
            child: Text(
              _getDetailedStatusMessage(),
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.8),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Color _getStatusColor() {
    return Color(
      int.parse(widget.currentStatus.colorHex.substring(1), radix: 16) + 0xFF000000,
    );
  }

  IconData _getStatusIcon() {
    switch (widget.currentStatus) {
      case OrderStatus.placed:
        return Icons.receipt_long;
      case OrderStatus.confirmed:
        return Icons.check_circle_outline;
      case OrderStatus.preparing:
        return Icons.restaurant;
      case OrderStatus.ready:
        return Icons.done_all;
      case OrderStatus.completed:
        return Icons.celebration;
      case OrderStatus.cancelled:
        return Icons.cancel_outlined;
    }
  }

  String _getStatusDescription() {
    switch (widget.currentStatus) {
      case OrderStatus.placed:
        return 'Your order has been placed';
      case OrderStatus.confirmed:
        return 'Order confirmed and queued';
      case OrderStatus.preparing:
        return 'Kitchen is preparing your order';
      case OrderStatus.ready:
        return 'Order is ready for pickup';
      case OrderStatus.completed:
        return 'Order completed successfully';
      case OrderStatus.cancelled:
        return 'Order has been cancelled';
    }
  }

  String _getDetailedStatusMessage() {
    switch (widget.currentStatus) {
      case OrderStatus.placed:
        return 'We\'ve received your order and it\'s being reviewed by the restaurant.';
      case OrderStatus.confirmed:
        return 'Your order has been confirmed and will be prepared shortly.';
      case OrderStatus.preparing:
        return 'Our kitchen team is working on your order right now.';
      case OrderStatus.ready:
        return 'Your order is ready! Please come to the counter to collect it.';
      case OrderStatus.completed:
        return 'Thank you for your order! We hope you enjoyed your meal.';
      case OrderStatus.cancelled:
        return 'Your order has been cancelled. Please contact us if you need assistance.';
    }
  }

  String _formatTimeRemaining(int minutes) {
    if (minutes <= 0) return 'Ready soon';
    
    if (minutes < 60) {
      return '~$minutes min remaining';
    } else {
      final hours = minutes ~/ 60;
      final remainingMinutes = minutes % 60;
      return '~${hours}h ${remainingMinutes}m remaining';
    }
  }
}

/// Compact version of the order status indicator for lists.
class CompactOrderStatusIndicator extends StatelessWidget {
  /// Creates a compact order status indicator.
  /// 
  /// Args:
  ///   currentStatus: Current order status
  ///   progress: Overall progress (0.0 to 1.0)
  ///   isOverdue: Whether the order is overdue
  const CompactOrderStatusIndicator({
    super.key,
    required this.currentStatus,
    required this.progress,
    this.isOverdue = false,
  });

  /// Current order status
  final OrderStatus currentStatus;

  /// Overall progress (0.0 to 1.0)
  final double progress;

  /// Whether the order is overdue
  final bool isOverdue;

  @override
  Widget build(BuildContext context) {
    return OrderStatusIndicator(
      currentStatus: currentStatus,
      progress: progress,
      isOverdue: isOverdue,
      showDetails: false,
      compact: true,
    );
  }
}

/// Status badge for minimal space usage.
class OrderStatusBadge extends StatelessWidget {
  /// Creates an order status badge.
  /// 
  /// Args:
  ///   status: Order status
  ///   size: Badge size
  const OrderStatusBadge({
    super.key,
    required this.status,
    this.size = OrderStatusBadgeSize.medium,
  });

  /// Order status
  final OrderStatus status;

  /// Badge size
  final OrderStatusBadgeSize size;

  @override
  Widget build(BuildContext context) {
    final statusColor = Color(
      int.parse(status.colorHex.substring(1), radix: 16) + 0xFF000000,
    );

    final dimensions = _getBadgeDimensions();
    
    return Container(
      padding: EdgeInsets.symmetric(
        horizontal: dimensions.padding,
        vertical: dimensions.padding * 0.5,
      ),
      decoration: BoxDecoration(
        color: statusColor.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(dimensions.borderRadius),
        border: Border.all(
          color: statusColor.withValues(alpha: 0.3),
          width: 1,
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: dimensions.dotSize,
            height: dimensions.dotSize,
            decoration: BoxDecoration(
              color: statusColor,
              shape: BoxShape.circle,
            ),
          ),
          SizedBox(width: dimensions.spacing),
          Text(
            status.displayName,
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
              fontSize: dimensions.fontSize,
              fontWeight: FontWeight.w600,
              color: statusColor,
            ),
          ),
        ],
      ),
    );
  }

  _BadgeDimensions _getBadgeDimensions() {
    switch (size) {
      case OrderStatusBadgeSize.small:
        return const _BadgeDimensions(
          padding: 6,
          borderRadius: 8,
          dotSize: 6,
          spacing: 4,
          fontSize: 10,
        );
      case OrderStatusBadgeSize.medium:
        return const _BadgeDimensions(
          padding: 8,
          borderRadius: 10,
          dotSize: 8,
          spacing: 6,
          fontSize: 12,
        );
      case OrderStatusBadgeSize.large:
        return const _BadgeDimensions(
          padding: 10,
          borderRadius: 12,
          dotSize: 10,
          spacing: 8,
          fontSize: 14,
        );
    }
  }
}

/// Order status badge size enumeration.
enum OrderStatusBadgeSize {
  small,
  medium,
  large,
}

/// Badge dimensions helper class.
class _BadgeDimensions {
  const _BadgeDimensions({
    required this.padding,
    required this.borderRadius,
    required this.dotSize,
    required this.spacing,
    required this.fontSize,
  });

  final double padding;
  final double borderRadius;
  final double dotSize;
  final double spacing;
  final double fontSize;
}
