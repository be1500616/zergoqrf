/// ZERGO QR Order Tracking Feature
/// 
/// This module provides comprehensive real-time order tracking capabilities
/// for customers and restaurant staff, including status updates, timeline
/// visualization, and notification management.
/// 
/// Features:
/// - Real-time order status updates via Supabase Realtime
/// - Complete order timeline with timestamps
/// - Kitchen staff order management interface
/// - Customer notification preferences
/// - Item-level preparation tracking
/// - Multi-device synchronization
/// 
/// Architecture:
/// - Domain: Order tracking entities and business rules
/// - Infrastructure: API clients and Supabase Realtime integration
/// - Application: GetX controllers and use cases
/// - Presentation: UI screens and widgets
/// 
/// Story: 3.4 - Order Tracking & Status Updates
library order_tracking;

// Domain exports
export 'domain/entities/order_tracking.dart';
export 'domain/entities/order_timeline.dart';
export 'domain/entities/order_status_update.dart';
export 'domain/entities/notification_preference.dart';
export 'domain/repositories/order_tracking_repository.dart';

// Infrastructure exports
export 'infrastructure/order_tracking_api_client.dart';
export 'infrastructure/order_tracking_realtime_client.dart';
export 'infrastructure/order_tracking_repository_impl.dart';

// Application exports
export 'application/controllers/order_tracking_controller.dart';
export 'application/controllers/kitchen_order_controller.dart';
export 'application/use_cases/fetch_order_tracking.dart';
export 'application/use_cases/subscribe_order_updates.dart';
export 'application/use_cases/update_order_status.dart';

// Presentation exports
export 'presentation/screens/order_tracking_screen.dart';
export 'presentation/screens/kitchen_order_management_screen.dart';
export 'presentation/widgets/order_timeline_widget.dart';
export 'presentation/widgets/order_status_indicator.dart';
export 'presentation/widgets/real_time_status_card.dart';
