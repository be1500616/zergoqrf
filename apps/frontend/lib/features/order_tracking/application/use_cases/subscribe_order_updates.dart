/// Subscribe to order updates use case.
/// 
/// This use case handles subscribing to real-time order updates using
/// Supabase Realtime with proper connection management and error handling.
import 'dart:async';
import 'package:flutter/foundation.dart';

import '../../domain/entities/order_status_update.dart';
import '../../domain/repositories/order_tracking_repository.dart';

/// Use case for subscribing to real-time order updates.
class SubscribeOrderUpdatesUseCase {
  /// Creates a subscribe order updates use case.
  /// 
  /// Args:
  ///   repository: Order tracking repository
  const SubscribeOrderUpdatesUseCase({
    required OrderTrackingRepository repository,
  }) : _repository = repository;

  final OrderTrackingRepository _repository;

  /// Execute the use case to subscribe to order updates.
  /// 
  /// Args:
  ///   orderId: Order identifier
  /// 
  /// Returns:
  ///   Stream of RealtimeStatusUpdate events
  /// 
  /// Throws:
  ///   OrderTrackingException: If subscription fails
  ///   ArgumentError: If orderId is invalid
  Future<Stream<RealtimeStatusUpdate>> execute(String orderId) async {
    // Validate input
    if (orderId.isEmpty) {
      throw ArgumentError('Order ID cannot be empty');
    }

    try {
      debugPrint('SubscribeOrderUpdatesUseCase: Subscribing to updates for order $orderId');

      // Subscribe to real-time updates from repository
      final stream = _repository.subscribeToOrderUpdates(orderId);

      // Transform stream to add validation and error handling
      final transformedStream = stream.transform(
        StreamTransformer<RealtimeStatusUpdate, RealtimeStatusUpdate>.fromHandlers(
          handleData: (update, sink) {
            try {
              // Validate update
              _validateStatusUpdate(update);
              
              // Log update
              debugPrint('SubscribeOrderUpdatesUseCase: Received update - ${update.newStatus}');
              
              // Forward to sink
              sink.add(update);
            } catch (e) {
              debugPrint('SubscribeOrderUpdatesUseCase: Invalid update received - $e');
              // Don't forward invalid updates
            }
          },
          handleError: (error, stackTrace, sink) {
            debugPrint('SubscribeOrderUpdatesUseCase: Stream error - $error');
            sink.addError(OrderTrackingStreamError(
              'Real-time update stream error: $error',
              originalError: error,
            ));
          },
          handleDone: (sink) {
            debugPrint('SubscribeOrderUpdatesUseCase: Stream closed for order $orderId');
            sink.close();
          },
        ),
      );

      debugPrint('SubscribeOrderUpdatesUseCase: Successfully subscribed to updates');
      return transformedStream;
    } catch (e) {
      debugPrint('SubscribeOrderUpdatesUseCase: Error subscribing to updates - $e');
      rethrow;
    }
  }

  /// Execute the use case to subscribe to kitchen updates.
  /// 
  /// Args:
  ///   restaurantId: Restaurant identifier
  /// 
  /// Returns:
  ///   Stream of RealtimeStatusUpdate events for all restaurant orders
  /// 
  /// Throws:
  ///   OrderTrackingException: If subscription fails
  ///   ArgumentError: If restaurantId is invalid
  Future<Stream<RealtimeStatusUpdate>> executeKitchenUpdates(String restaurantId) async {
    // Validate input
    if (restaurantId.isEmpty) {
      throw ArgumentError('Restaurant ID cannot be empty');
    }

    try {
      debugPrint('SubscribeOrderUpdatesUseCase: Subscribing to kitchen updates for restaurant $restaurantId');

      // Subscribe to kitchen updates from repository
      final stream = _repository.subscribeToKitchenUpdates(restaurantId);

      // Transform stream with validation and filtering
      final transformedStream = stream.transform(
        StreamTransformer<RealtimeStatusUpdate, RealtimeStatusUpdate>.fromHandlers(
          handleData: (update, sink) {
            try {
              // Validate update
              _validateStatusUpdate(update);
              
              // Filter relevant updates for kitchen
              if (_isKitchenRelevantUpdate(update)) {
                debugPrint('SubscribeOrderUpdatesUseCase: Kitchen update - ${update.orderId}: ${update.newStatus}');
                sink.add(update);
              }
            } catch (e) {
              debugPrint('SubscribeOrderUpdatesUseCase: Invalid kitchen update - $e');
              // Don't forward invalid updates
            }
          },
          handleError: (error, stackTrace, sink) {
            debugPrint('SubscribeOrderUpdatesUseCase: Kitchen stream error - $error');
            sink.addError(OrderTrackingStreamError(
              'Kitchen update stream error: $error',
              originalError: error,
            ));
          },
          handleDone: (sink) {
            debugPrint('SubscribeOrderUpdatesUseCase: Kitchen stream closed for restaurant $restaurantId');
            sink.close();
          },
        ),
      );

      debugPrint('SubscribeOrderUpdatesUseCase: Successfully subscribed to kitchen updates');
      return transformedStream;
    } catch (e) {
      debugPrint('SubscribeOrderUpdatesUseCase: Error subscribing to kitchen updates - $e');
      rethrow;
    }
  }

  /// Create a filtered stream for specific status changes.
  /// 
  /// Args:
  ///   baseStream: Base stream of status updates
  ///   statusFilter: List of statuses to filter for
  /// 
  /// Returns:
  ///   Filtered stream of RealtimeStatusUpdate events
  Stream<RealtimeStatusUpdate> createFilteredStream(
    Stream<RealtimeStatusUpdate> baseStream,
    List<String> statusFilter,
  ) {
    if (statusFilter.isEmpty) {
      return baseStream;
    }

    return baseStream.where((update) {
      final isFiltered = statusFilter.contains(update.newStatus.toLowerCase());
      if (isFiltered) {
        debugPrint('SubscribeOrderUpdatesUseCase: Filtered update - ${update.newStatus}');
      }
      return isFiltered;
    });
  }

  /// Create a debounced stream to prevent rapid updates.
  /// 
  /// Args:
  ///   baseStream: Base stream of status updates
  ///   debounceDuration: Duration to debounce updates
  /// 
  /// Returns:
  ///   Debounced stream of RealtimeStatusUpdate events
  Stream<RealtimeStatusUpdate> createDebouncedStream(
    Stream<RealtimeStatusUpdate> baseStream,
    Duration debounceDuration,
  ) {
    Timer? debounceTimer;
    RealtimeStatusUpdate? lastUpdate;
    late StreamController<RealtimeStatusUpdate> controller;

    controller = StreamController<RealtimeStatusUpdate>(
      onListen: () {
        baseStream.listen(
          (update) {
            lastUpdate = update;
            debounceTimer?.cancel();
            debounceTimer = Timer(debounceDuration, () {
              if (lastUpdate != null && !controller.isClosed) {
                controller.add(lastUpdate!);
                debugPrint('SubscribeOrderUpdatesUseCase: Debounced update - ${lastUpdate!.newStatus}');
              }
            });
          },
          onError: controller.addError,
          onDone: () {
            debounceTimer?.cancel();
            controller.close();
          },
        );
      },
      onCancel: () {
        debounceTimer?.cancel();
      },
    );

    return controller.stream;
  }

  /// Create a stream that batches multiple updates.
  /// 
  /// Args:
  ///   baseStream: Base stream of status updates
  ///   batchSize: Maximum number of updates per batch
  ///   batchTimeout: Maximum time to wait for batch completion
  /// 
  /// Returns:
  ///   Stream of batched RealtimeStatusUpdate lists
  Stream<List<RealtimeStatusUpdate>> createBatchedStream(
    Stream<RealtimeStatusUpdate> baseStream,
    int batchSize,
    Duration batchTimeout,
  ) {
    final List<RealtimeStatusUpdate> batch = [];
    Timer? batchTimer;
    late StreamController<List<RealtimeStatusUpdate>> controller;

    void flushBatch() {
      if (batch.isNotEmpty && !controller.isClosed) {
        final batchCopy = List<RealtimeStatusUpdate>.from(batch);
        batch.clear();
        controller.add(batchCopy);
        debugPrint('SubscribeOrderUpdatesUseCase: Flushed batch of ${batchCopy.length} updates');
      }
      batchTimer?.cancel();
      batchTimer = null;
    }

    controller = StreamController<List<RealtimeStatusUpdate>>(
      onListen: () {
        baseStream.listen(
          (update) {
            batch.add(update);
            
            // Start batch timer if not already running
            batchTimer ??= Timer(batchTimeout, flushBatch);
            
            // Flush if batch is full
            if (batch.length >= batchSize) {
              flushBatch();
            }
          },
          onError: controller.addError,
          onDone: () {
            flushBatch();
            controller.close();
          },
        );
      },
      onCancel: () {
        batchTimer?.cancel();
        batch.clear();
      },
    );

    return controller.stream;
  }

  /// Validate status update data.
  /// 
  /// Args:
  ///   update: Status update to validate
  /// 
  /// Throws:
  ///   ArgumentError: If update is invalid
  void _validateStatusUpdate(RealtimeStatusUpdate update) {
    if (update.orderId.isEmpty) {
      throw ArgumentError('Status update must have a valid order ID');
    }

    if (update.newStatus.isEmpty) {
      throw ArgumentError('Status update must have a valid new status');
    }

    if (update.previousStatus.isEmpty) {
      throw ArgumentError('Status update must have a valid previous status');
    }

    // Validate timestamp is not in the future
    if (update.timestamp.isAfter(DateTime.now().add(const Duration(minutes: 1)))) {
      throw ArgumentError('Status update timestamp cannot be in the future');
    }

    // Validate status values
    final validStatuses = ['placed', 'confirmed', 'preparing', 'ready', 'completed', 'cancelled'];
    if (!validStatuses.contains(update.newStatus.toLowerCase())) {
      throw ArgumentError('Invalid new status: ${update.newStatus}');
    }

    if (!validStatuses.contains(update.previousStatus.toLowerCase())) {
      throw ArgumentError('Invalid previous status: ${update.previousStatus}');
    }
  }

  /// Check if update is relevant for kitchen display.
  /// 
  /// Args:
  ///   update: Status update to check
  /// 
  /// Returns:
  ///   True if update is relevant for kitchen
  bool _isKitchenRelevantUpdate(RealtimeStatusUpdate update) {
    // Kitchen is interested in all status changes except completed orders
    // unless they just became completed
    final kitchenRelevantStatuses = [
      'placed',
      'confirmed', 
      'preparing',
      'ready',
      'completed', // Show when order becomes completed
      'cancelled',
    ];

    return kitchenRelevantStatuses.contains(update.newStatus.toLowerCase());
  }
}

/// Custom exception for stream errors.
class OrderTrackingStreamError implements Exception {
  /// Creates an order tracking stream error.
  const OrderTrackingStreamError(
    this.message, {
    this.originalError,
  });

  /// Error message
  final String message;

  /// Original error that caused this stream error
  final dynamic originalError;

  @override
  String toString() {
    return 'OrderTrackingStreamError: $message${originalError != null ? ' (Original: $originalError)' : ''}';
  }
}

/// Stream connection manager for handling reconnections.
class StreamConnectionManager {
  /// Creates a stream connection manager.
  StreamConnectionManager({
    this.maxReconnectAttempts = 5,
    this.initialReconnectDelay = const Duration(seconds: 1),
    this.maxReconnectDelay = const Duration(seconds: 30),
    this.reconnectBackoffMultiplier = 2.0,
  });

  /// Maximum number of reconnection attempts
  final int maxReconnectAttempts;

  /// Initial delay before first reconnection attempt
  final Duration initialReconnectDelay;

  /// Maximum delay between reconnection attempts
  final Duration maxReconnectDelay;

  /// Backoff multiplier for reconnection delays
  final double reconnectBackoffMultiplier;

  int _reconnectAttempts = 0;
  Duration _currentReconnectDelay = Duration.zero;

  /// Create a resilient stream with automatic reconnection.
  /// 
  /// Args:
  ///   streamFactory: Function that creates the stream
  /// 
  /// Returns:
  ///   Stream with automatic reconnection capability
  Stream<T> createResilientStream<T>(
    Future<Stream<T>> Function() streamFactory,
  ) {
    late StreamController<T> controller;
    StreamSubscription<T>? subscription;

    void connect() async {
      try {
        debugPrint('StreamConnectionManager: Connecting... (attempt ${_reconnectAttempts + 1})');
        
        final stream = await streamFactory();
        subscription = stream.listen(
          (data) {
            // Reset reconnection state on successful data
            _reconnectAttempts = 0;
            _currentReconnectDelay = initialReconnectDelay;
            
            if (!controller.isClosed) {
              controller.add(data);
            }
          },
          onError: (error) {
            debugPrint('StreamConnectionManager: Stream error - $error');
            if (!controller.isClosed) {
              controller.addError(error);
            }
            _scheduleReconnect();
          },
          onDone: () {
            debugPrint('StreamConnectionManager: Stream closed');
            _scheduleReconnect();
          },
        );
        
        debugPrint('StreamConnectionManager: Connected successfully');
      } catch (e) {
        debugPrint('StreamConnectionManager: Connection failed - $e');
        if (!controller.isClosed) {
          controller.addError(e);
        }
        _scheduleReconnect();
      }
    }

    void _scheduleReconnect() {
      if (_reconnectAttempts >= maxReconnectAttempts) {
        debugPrint('StreamConnectionManager: Max reconnection attempts reached');
        if (!controller.isClosed) {
          controller.addError(
            OrderTrackingStreamError('Max reconnection attempts reached'),
          );
          controller.close();
        }
        return;
      }

      _reconnectAttempts++;
      _currentReconnectDelay = Duration(
        milliseconds: (_currentReconnectDelay.inMilliseconds * reconnectBackoffMultiplier)
            .clamp(initialReconnectDelay.inMilliseconds, maxReconnectDelay.inMilliseconds)
            .round(),
      );

      debugPrint('StreamConnectionManager: Scheduling reconnect in ${_currentReconnectDelay.inSeconds}s');
      
      Timer(_currentReconnectDelay, () {
        if (!controller.isClosed) {
          connect();
        }
      });
    }

    controller = StreamController<T>(
      onListen: connect,
      onCancel: () {
        subscription?.cancel();
      },
    );

    return controller.stream;
  }

  /// Reset reconnection state.
  void reset() {
    _reconnectAttempts = 0;
    _currentReconnectDelay = initialReconnectDelay;
  }
}
