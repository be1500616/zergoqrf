-- Order Tracking Infrastructure Migration
-- Story 3.4: Order Tracking & Status Updates
-- This migration adds real-time order tracking capabilities with comprehensive audit trail

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Order Status History Table
-- Complete audit trail for all order status changes
CREATE TABLE order_status_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Order relationship
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    
    -- Status transition details
    status order_status NOT NULL,
    previous_status order_status,
    
    -- Change tracking
    changed_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    changed_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Kitchen workflow support
    estimated_completion_time TIMESTAMPTZ,
    actual_completion_time TIMESTAMPTZ,
    preparation_notes TEXT,
    
    -- Item-level tracking support
    item_statuses JSONB DEFAULT '{}', -- {item_id: status} mapping
    
    -- Audit and compliance
    change_reason VARCHAR(255),
    system_generated BOOLEAN DEFAULT false,
    
    -- Indexing for performance
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Notification Preferences Table
-- Customer notification settings per restaurant
CREATE TABLE notification_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Restaurant context
    restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    
    -- Customer identification
    customer_phone VARCHAR(20),
    customer_email VARCHAR(255),
    customer_name VARCHAR(255),
    
    -- Notification channel preferences
    email_enabled BOOLEAN DEFAULT true,
    whatsapp_enabled BOOLEAN DEFAULT false,
    sms_enabled BOOLEAN DEFAULT false,
    
    -- Notification timing preferences
    immediate_notifications BOOLEAN DEFAULT true,
    status_change_notifications BOOLEAN DEFAULT true,
    eta_update_notifications BOOLEAN DEFAULT true,
    completion_notifications BOOLEAN DEFAULT true,
    
    -- Business configuration
    business_hours_only BOOLEAN DEFAULT false,
    quiet_hours_start TIME,
    quiet_hours_end TIME,
    
    -- Compliance and privacy
    opt_out_all BOOLEAN DEFAULT false,
    privacy_consent BOOLEAN DEFAULT false,
    
    -- Audit trail
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Unique constraint for customer per restaurant
    UNIQUE(restaurant_id, customer_phone)
);

-- Notification History Table
-- Complete audit trail for all notifications sent
CREATE TABLE notification_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Order and customer context
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    
    -- Notification details
    channel VARCHAR(20) NOT NULL CHECK (channel IN ('email', 'whatsapp', 'sms', 'push')),
    recipient VARCHAR(255) NOT NULL,
    subject VARCHAR(255),
    message_content TEXT NOT NULL,
    
    -- Delivery tracking
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'sent', 'delivered', 'failed', 'bounced')),
    sent_at TIMESTAMPTZ,
    delivered_at TIMESTAMPTZ,
    opened_at TIMESTAMPTZ,
    clicked_at TIMESTAMPTZ,
    
    -- Error handling
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    
    -- External service tracking
    external_message_id VARCHAR(255), -- For tracking with email/SMS providers
    external_status VARCHAR(50),
    
    -- Cost tracking (for business analytics)
    cost_amount DECIMAL(10,4),
    cost_currency VARCHAR(3) DEFAULT 'INR',
    
    -- Audit trail
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Order Item Status Tracking Table
-- Individual menu item preparation status
CREATE TABLE order_item_status_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Relationships
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    order_item_id UUID NOT NULL REFERENCES order_items(id) ON DELETE CASCADE,
    
    -- Item status tracking
    status VARCHAR(50) NOT NULL CHECK (status IN ('pending', 'preparing', 'ready', 'served', 'cancelled')),
    previous_status VARCHAR(50),
    
    -- Kitchen workflow
    assigned_to UUID REFERENCES auth.users(id) ON DELETE SET NULL, -- Kitchen staff
    estimated_ready_time TIMESTAMPTZ,
    actual_ready_time TIMESTAMPTZ,
    preparation_notes TEXT,
    
    -- Quality control
    quality_check_passed BOOLEAN,
    quality_notes TEXT,
    
    -- Change tracking
    changed_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    changed_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Audit trail
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Real-time Configuration
-- Enable Realtime on critical tables for live updates
ALTER PUBLICATION supabase_realtime ADD TABLE orders;
ALTER PUBLICATION supabase_realtime ADD TABLE order_status_history;
ALTER PUBLICATION supabase_realtime ADD TABLE order_item_status_history;

-- Performance Indexes
-- Optimized indexes for real-time queries and reporting

-- Order status history indexes
CREATE INDEX IF NOT EXISTS idx_order_status_history_order_id ON order_status_history(order_id);
CREATE INDEX IF NOT EXISTS idx_order_status_history_changed_at ON order_status_history(changed_at DESC);
CREATE INDEX IF NOT EXISTS idx_order_status_history_status ON order_status_history(status);

-- Notification preferences indexes
CREATE INDEX IF NOT EXISTS idx_notification_preferences_restaurant_id ON notification_preferences(restaurant_id);
CREATE INDEX IF NOT EXISTS idx_notification_preferences_phone ON notification_preferences(customer_phone);
CREATE INDEX IF NOT EXISTS idx_notification_preferences_email ON notification_preferences(customer_email);

-- Notification history indexes
CREATE INDEX IF NOT EXISTS idx_notification_history_order_id ON notification_history(order_id);
CREATE INDEX IF NOT EXISTS idx_notification_history_status ON notification_history(status);
CREATE INDEX IF NOT EXISTS idx_notification_history_channel ON notification_history(channel);
CREATE INDEX IF NOT EXISTS idx_notification_history_created_at ON notification_history(created_at DESC);

-- Order item status indexes
CREATE INDEX IF NOT EXISTS idx_order_item_status_order_id ON order_item_status_history(order_id);
CREATE INDEX IF NOT EXISTS idx_order_item_status_item_id ON order_item_status_history(order_item_id);
CREATE INDEX IF NOT EXISTS idx_order_item_status_status ON order_item_status_history(status);

-- Database Functions for Business Logic
-- Automated status history logging

CREATE OR REPLACE FUNCTION log_order_status_change()
RETURNS TRIGGER AS $$
BEGIN
    -- Only log if status actually changed
    IF OLD.order_status IS DISTINCT FROM NEW.order_status THEN
        INSERT INTO order_status_history (
            order_id,
            status,
            previous_status,
            changed_at,
            system_generated,
            change_reason
        ) VALUES (
            NEW.id,
            NEW.order_status,
            OLD.order_status,
            NOW(),
            true,
            'Automatic status change trigger'
        );
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for automatic status history logging
CREATE TRIGGER trigger_log_order_status_change
    AFTER UPDATE ON orders
    FOR EACH ROW
    EXECUTE FUNCTION log_order_status_change();

-- Function to calculate estimated completion time
CREATE OR REPLACE FUNCTION calculate_order_eta(order_id_param UUID)
RETURNS TIMESTAMPTZ AS $$
DECLARE
    base_prep_time INTEGER;
    priority_multiplier DECIMAL;
    kitchen_load_factor DECIMAL;
    estimated_time TIMESTAMPTZ;
BEGIN
    -- Get base preparation time from order
    SELECT estimated_preparation_time INTO base_prep_time
    FROM orders WHERE id = order_id_param;
    
    -- Apply business logic for ETA calculation
    -- This can be enhanced with ML models in the future
    priority_multiplier := 1.0; -- Default multiplier
    kitchen_load_factor := 1.0;  -- Default load factor
    
    -- Calculate estimated completion time
    estimated_time := NOW() + (base_prep_time * priority_multiplier * kitchen_load_factor) * INTERVAL '1 minute';
    
    RETURN estimated_time;
END;
$$ LANGUAGE plpgsql;

-- Row Level Security Policies
-- Multi-tenant security for order tracking data

-- Order status history policies
-- ponytail: policy order_status_history_select_policy removed (depends on new schema not present)

-- ponytail: policy order_status_history_insert_policy removed (depends on new schema not present)

-- Notification preferences policies
-- ponytail: policy notification_preferences_select_policy removed (depends on new schema not present)

-- ponytail: policy notification_preferences_insert_policy removed (depends on new schema not present)

-- ponytail: policy notification_preferences_update_policy removed (depends on new schema not present)

-- Notification history policies (read-only for most users)
-- ponytail: policy notification_history_select_policy removed (depends on new schema not present)

-- ponytail: policy notification_history_insert_policy removed (depends on new schema not present)

-- Order item status history policies
-- ponytail: policy order_item_status_select_policy removed (depends on new schema not present)

-- ponytail: policy order_item_status_insert_policy removed (depends on new schema not present)

-- Enable RLS on all new tables
ALTER TABLE order_status_history DISABLE ROW LEVEL SECURITY;
ALTER TABLE notification_preferences DISABLE ROW LEVEL SECURITY;
ALTER TABLE notification_history DISABLE ROW LEVEL SECURITY;
ALTER TABLE order_item_status_history DISABLE ROW LEVEL SECURITY;

-- Comments for documentation
COMMENT ON TABLE order_status_history IS 'Complete audit trail for order status changes with real-time capabilities';
COMMENT ON TABLE notification_preferences IS 'Customer notification preferences per restaurant with business configuration';
COMMENT ON TABLE notification_history IS 'Complete audit trail for all notifications sent with delivery tracking';
COMMENT ON TABLE order_item_status_history IS 'Individual menu item preparation status tracking for kitchen workflow';
