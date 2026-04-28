/// Order tracking screen for customers.
/// 
/// This screen provides a comprehensive view of order status with real-time
/// updates, timeline visualization, and modern UI/UX patterns.
import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:get/get.dart';

import '../../../../shared/widgets/enhanced_button.dart';
import '../../../../shared/widgets/enhanced_card.dart';
import '../../../../shared/widgets/enhanced_loading.dart';
import '../../../../shared/utils/app_spacing.dart';
import '../../../../shared/utils/screen_size.dart';
import '../../../../shared/utils/app_animations.dart';
import '../../application/controllers/order_tracking_controller.dart';
import '../widgets/order_status_indicator.dart';
import '../widgets/order_timeline_widget.dart';
import '../widgets/real_time_status_card.dart';

/// Order tracking screen for customer order monitoring.
class OrderTrackingScreen extends StatefulWidget {
  /// Creates an order tracking screen.
  /// 
  /// Args:
  ///   orderId: Order identifier (optional, can be passed via route)
  ///   orderNumber: Order number (optional, alternative to orderId)
  const OrderTrackingScreen({
    super.key,
    this.orderId,
    this.orderNumber,
  });

  /// Order identifier
  final String? orderId;

  /// Order number
  final String? orderNumber;

  @override
  State<OrderTrackingScreen> createState() => _OrderTrackingScreenState();
}

class _OrderTrackingScreenState extends State<OrderTrackingScreen>
    with TickerProviderStateMixin {
  late final OrderTrackingController _controller;
  late final AnimationController _refreshAnimationController;
  late final AnimationController _connectionAnimationController;

  @override
  void initState() {
    super.initState();
    
    // Initialize controllers
    _controller = Get.find<OrderTrackingController>();
    _refreshAnimationController = AnimationController(
      duration: AppAnimations.normal,
      vsync: this,
    );
    _connectionAnimationController = AnimationController(
      duration: AppAnimations.fast,
      vsync: this,
    );

    // Load order tracking data
    _loadOrderTracking();

    // Listen to connection status changes
    ever(_controller.isConnected, (bool isConnected) {
      if (isConnected) {
        _connectionAnimationController.forward();
      } else {
        _connectionAnimationController.reverse();
      }
    });
  }

  @override
  void dispose() {
    _refreshAnimationController.dispose();
    _connectionAnimationController.dispose();
    super.dispose();
  }

  Future<void> _loadOrderTracking() async {
    if (widget.orderId != null) {
      await _controller.fetchOrderTracking(widget.orderId!);
    } else if (widget.orderNumber != null) {
      await _controller.fetchOrderTrackingByNumber(widget.orderNumber!);
    } else {
      // Try to get from route parameters
      final orderId = Get.parameters['orderId'];
      final orderNumber = Get.parameters['orderNumber'];
      
      if (orderId != null) {
        await _controller.fetchOrderTracking(orderId);
      } else if (orderNumber != null) {
        await _controller.fetchOrderTrackingByNumber(orderNumber);
      } else {
        Get.snackbar(
          'Error',
          'No order information provided',
          snackPosition: SnackPosition.TOP,
          backgroundColor: Colors.red.withValues(alpha: 0.1),
          colorText: Colors.red,
        );
        Get.back();
      }
    }
  }

  Future<void> _handleRefresh() async {
    _refreshAnimationController.forward();
    await _controller.refreshOrderTracking();
    _refreshAnimationController.reverse();
  }

  @override
  Widget build(BuildContext context) {
    final screenSize = ScreenSize.of(context);
    
    return Scaffold(
      backgroundColor: Theme.of(context).colorScheme.surface,
      appBar: _buildAppBar(context),
      body: Obx(() => _buildBody(context, screenSize)),
      floatingActionButton: _buildFloatingActionButton(context),
    );
  }

  PreferredSizeWidget _buildAppBar(BuildContext context) {
    return AppBar(
      title: Obx(() {
        final orderNumber = _controller.orderTracking?.orderNumber ?? 'Order';
        return Text(
          orderNumber,
          style: Theme.of(context).textTheme.titleLarge?.copyWith(
            fontWeight: FontWeight.w600,
          ),
        );
      }),
      backgroundColor: Theme.of(context).colorScheme.surface,
      elevation: 0,
      scrolledUnderElevation: 1,
      actions: [
        // Connection status indicator
        Obx(() => AnimatedBuilder(
          animation: _connectionAnimationController,
          builder: (context, child) {
            return Container(
              margin: const EdgeInsets.only(right: AppSpacing.md),
              child: Icon(
                _controller.isConnected ? Icons.wifi : Icons.wifi_off,
                color: _controller.isConnected 
                    ? Colors.green
                    : Colors.red.withValues(alpha: 0.7),
                size: 20,
              ),
            ).animate(controller: _connectionAnimationController)
             .scale(begin: const Offset(0.8, 0.8), end: const Offset(1.0, 1.0))
             .fadeIn();
          },
        )),
        
        // Refresh button
        AnimatedBuilder(
          animation: _refreshAnimationController,
          builder: (context, child) {
            return IconButton(
              onPressed: _controller.isLoading ? null : _handleRefresh,
              icon: Transform.rotate(
                angle: _refreshAnimationController.value * 2 * 3.14159,
                child: const Icon(Icons.refresh),
              ),
            );
          },
        ),
      ],
    );
  }

  Widget _buildBody(BuildContext context, ScreenSize screenSize) {
    if (_controller.isLoading && !_controller.hasData) {
      return _buildLoadingState(context);
    }

    if (_controller.hasError && !_controller.hasData) {
      return _buildErrorState(context);
    }

    if (!_controller.hasData) {
      return _buildEmptyState(context);
    }

    return RefreshIndicator(
      onRefresh: _handleRefresh,
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: EdgeInsets.all(
          screenSize.isMobile ? AppSpacing.md : AppSpacing.lg,
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Real-time status card
            RealTimeStatusCard(
              orderTracking: _controller.orderTracking!,
              isConnected: _controller.isConnected,
              lastUpdateTime: _controller.lastUpdateTime,
            ).animate()
             .slideY(begin: -0.2, duration: AppAnimations.normal)
             .fadeIn(delay: 100.ms),

            const SizedBox(height: AppSpacing.lg),

            // Order status indicator
            OrderStatusIndicator(
              currentStatus: _controller.orderTracking!.currentStatus,
              progress: _controller.overallProgress,
              estimatedTimeRemaining: _controller.estimatedTimeRemainingMinutes,
              isOverdue: _controller.isOverdue,
            ).animate()
             .slideY(begin: 0.2, duration: AppAnimations.normal)
             .fadeIn(delay: 200.ms),

            const SizedBox(height: AppSpacing.lg),

            // Order details section
            _buildOrderDetailsSection(context, screenSize)
                .animate()
                .slideY(begin: 0.2, duration: AppAnimations.normal)
                .fadeIn(delay: 300.ms),

            const SizedBox(height: AppSpacing.lg),

            // Timeline section
            if (_controller.timeline != null)
              _buildTimelineSection(context, screenSize)
                  .animate()
                  .slideY(begin: 0.2, duration: AppAnimations.normal)
                  .fadeIn(delay: 400.ms),

            // Bottom spacing for floating action button
            const SizedBox(height: AppSpacing.xxl),
          ],
        ),
      ),
    );
  }

  Widget _buildLoadingState(BuildContext context) {
    return const Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          EnhancedLoading(
            size: 48,
            message: 'Loading order tracking...',
          ),
        ],
      ),
    );
  }

  Widget _buildErrorState(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.lg),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.error_outline,
              size: 64,
              color: Theme.of(context).colorScheme.error,
            ),
            const SizedBox(height: AppSpacing.md),
            Text(
              'Unable to load order tracking',
              style: Theme.of(context).textTheme.headlineSmall,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: AppSpacing.sm),
            Text(
              _controller.error ?? 'An unexpected error occurred',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7),
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: AppSpacing.lg),
            EnhancedButton(
              onPressed: _loadOrderTracking,
              text: 'Try Again',
              variant: ButtonVariant.primary,
              icon: Icons.refresh,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEmptyState(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.lg),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.receipt_long_outlined,
              size: 64,
              color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.5),
            ),
            const SizedBox(height: AppSpacing.md),
            Text(
              'No order found',
              style: Theme.of(context).textTheme.headlineSmall,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: AppSpacing.sm),
            Text(
              'The order you\'re looking for could not be found.',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7),
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildOrderDetailsSection(BuildContext context, ScreenSize screenSize) {
    final order = _controller.orderTracking!;
    
    return EnhancedCard(
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.lg),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Order Details',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: AppSpacing.md),
            
            // Order information
            _buildDetailRow(
              context,
              'Order Number',
              order.orderNumber,
              Icons.receipt,
            ),
            
            if (order.estimatedCompletionTime != null)
              _buildDetailRow(
                context,
                'Estimated Completion',
                _formatEstimatedTime(order.estimatedCompletionTime!),
                Icons.schedule,
              ),
            
            _buildDetailRow(
              context,
              'Status',
              order.currentStatus.displayName,
              Icons.info,
              valueColor: _getStatusColor(order.currentStatus),
            ),
            
            if (order.itemTracking.isNotEmpty) ...[
              const SizedBox(height: AppSpacing.md),
              const Divider(),
              const SizedBox(height: AppSpacing.md),
              
              Text(
                'Items Progress',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: AppSpacing.sm),
              
              ...order.itemTracking.map((item) => _buildItemProgress(context, item)),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildTimelineSection(BuildContext context, ScreenSize screenSize) {
    return EnhancedCard(
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.lg),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Order Timeline',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: AppSpacing.md),
            OrderTimelineWidget(
              timeline: _controller.timeline!,
              compact: screenSize.isMobile,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDetailRow(
    BuildContext context,
    String label,
    String value,
    IconData icon, {
    Color? valueColor,
  }) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: AppSpacing.xs),
      child: Row(
        children: [
          Icon(
            icon,
            size: 20,
            color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.6),
          ),
          const SizedBox(width: AppSpacing.sm),
          Expanded(
            child: Text(
              label,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7),
              ),
            ),
          ),
          Text(
            value,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              fontWeight: FontWeight.w600,
              color: valueColor,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildItemProgress(BuildContext context, OrderItemTracking item) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: AppSpacing.xs),
      child: Row(
        children: [
          Container(
            width: 8,
            height: 8,
            decoration: BoxDecoration(
              color: _getItemStatusColor(item.status),
              shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: AppSpacing.sm),
          Expanded(
            child: Text(
              item.itemName,
              style: Theme.of(context).textTheme.bodyMedium,
            ),
          ),
          Text(
            item.status.displayName,
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
              color: _getItemStatusColor(item.status),
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }

  Widget? _buildFloatingActionButton(BuildContext context) {
    if (!_controller.hasData) return null;
    
    return FloatingActionButton.extended(
      onPressed: () {
        // Show order details or actions
        _showOrderActions(context);
      },
      icon: const Icon(Icons.more_horiz),
      label: const Text('Actions'),
      backgroundColor: Theme.of(context).colorScheme.primary,
      foregroundColor: Theme.of(context).colorScheme.onPrimary,
    );
  }

  void _showOrderActions(BuildContext context) {
    showModalBottomSheet(
      context: context,
      builder: (context) => Container(
        padding: const EdgeInsets.all(AppSpacing.lg),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: const Icon(Icons.refresh),
              title: const Text('Refresh Status'),
              onTap: () {
                Navigator.pop(context);
                _handleRefresh();
              },
            ),
            ListTile(
              leading: const Icon(Icons.share),
              title: const Text('Share Order'),
              onTap: () {
                Navigator.pop(context);
                // Implement share functionality
              },
            ),
            ListTile(
              leading: const Icon(Icons.help_outline),
              title: const Text('Get Help'),
              onTap: () {
                Navigator.pop(context);
                // Navigate to help/support
              },
            ),
          ],
        ),
      ),
    );
  }

  String _formatEstimatedTime(DateTime estimatedTime) {
    final now = DateTime.now();
    final difference = estimatedTime.difference(now);
    
    if (difference.isNegative) {
      return 'Overdue';
    }
    
    if (difference.inMinutes < 60) {
      return '${difference.inMinutes} minutes';
    } else {
      final hours = difference.inHours;
      final minutes = difference.inMinutes % 60;
      return '${hours}h ${minutes}m';
    }
  }

  Color _getStatusColor(OrderStatus status) {
    return Color(int.parse(status.colorHex.substring(1), radix: 16) + 0xFF000000);
  }

  Color _getItemStatusColor(OrderItemStatus status) {
    return Color(int.parse(status.colorHex.substring(1), radix: 16) + 0xFF000000);
  }
}
