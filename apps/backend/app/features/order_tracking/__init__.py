"""Order tracking feature module.

This module implements real-time order tracking capabilities for the ZERGO QR
restaurant platform, providing comprehensive order status management, customer
notifications, and kitchen workflow integration.

Features:
- Real-time order status updates via Supabase Realtime
- Complete order timeline with audit trail
- Kitchen staff order management interface
- Extensible notification system (email, WhatsApp, SMS)
- Item-level preparation tracking
- Multi-device synchronization
- Performance optimized for 200+ concurrent sessions

Architecture:
- Domain: Order tracking entities, value objects, and business rules
- Application: Use cases for status updates, notifications, and timeline management
- Infrastructure: Supabase Realtime integration and notification services
- Presentation: REST API endpoints and WebSocket handlers

Story: 3.4 - Order Tracking & Status Updates
"""
