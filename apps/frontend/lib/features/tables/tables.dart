/// Table management feature module.
/// 
/// This module contains all table management functionality including:
/// - Table CRUD operations
/// - Floor plan management
/// - Table status tracking
/// - QR code generation
/// - Reservation management

library tables;

// Domain exports
export 'domain/entities/table_entities.dart';
export 'domain/repositories/table_repositories.dart';
export 'domain/use_cases/table_use_cases.dart';

// Application exports
export 'application/controllers/table_controllers.dart';
export 'application/services/table_services.dart';

// Infrastructure exports
export 'infrastructure/datasources/table_datasources.dart';
export 'infrastructure/repositories/table_repositories_impl.dart';

// Presentation exports
export 'presentation/pages/table_pages.dart';
export 'presentation/widgets/table_widgets.dart';
