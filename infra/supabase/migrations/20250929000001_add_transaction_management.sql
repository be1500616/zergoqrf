-- Transaction Management System Migration
-- This migration adds comprehensive transaction management, refund processing,
-- and financial reporting capabilities to the ZERGO QR platform

BEGIN;

-- Create transaction status enum
CREATE TYPE transaction_status AS ENUM (
    'pending',
    'processing', 
    'completed',
    'failed',
    'refunded',
    'partially_refunded'
);

-- Create payment method enum (extending existing)
CREATE TYPE payment_method_extended AS ENUM (
    'cash',
    'card',
    'upi',
    'wallet',
    'bank_transfer',
    'stripe',
    'paypal',
    'razorpay'
);

-- Create refund status enum
CREATE TYPE refund_status AS ENUM (
    'pending',
    'processing',
    'completed',
    'failed',
    'cancelled'
);

-- Create payout status enum
CREATE TYPE payout_status AS ENUM (
    'scheduled',
    'processing',
    'completed',
    'failed',
    'cancelled'
);

-- Main transactions table for comprehensive financial tracking
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Transaction identification
    transaction_number VARCHAR(30) UNIQUE NOT NULL, -- Format: TXN-YYYYMMDD-XXXXXX
    
    -- Restaurant and order context
    restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    order_id UUID REFERENCES orders(id) ON DELETE SET NULL, -- Nullable for standalone transactions
    
    -- Transaction details
    amount DECIMAL(12, 2) NOT NULL CHECK (amount > 0),
    currency VARCHAR(3) DEFAULT 'INR' NOT NULL,
    payment_method payment_method_extended NOT NULL DEFAULT 'cash',
    status transaction_status NOT NULL DEFAULT 'pending',
    
    -- Gateway integration fields
    gateway_transaction_id VARCHAR(255) UNIQUE, -- External payment gateway transaction ID
    gateway_order_id VARCHAR(255), -- External payment gateway order ID
    gateway_response JSONB DEFAULT '{}', -- Store complete gateway response
    gateway_webhook_data JSONB DEFAULT '{}', -- Store webhook payload data
    
    -- Customer information (for standalone transactions)
    customer_name VARCHAR(255),
    customer_phone VARCHAR(20),
    customer_email VARCHAR(255),
    
    -- Transaction metadata
    description TEXT,
    reference_number VARCHAR(100), -- Internal reference
    failure_reason TEXT, -- Reason for failed transactions
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ, -- When transaction was completed/failed
    
    -- Indexes for performance
    CONSTRAINT transactions_restaurant_id_idx FOREIGN KEY (restaurant_id) REFERENCES restaurants(id)
);

-- Create indexes for transactions table
CREATE INDEX idx_transactions_restaurant_id ON transactions(restaurant_id);
CREATE INDEX idx_transactions_order_id ON transactions(order_id);
CREATE INDEX idx_transactions_status ON transactions(status);
CREATE INDEX idx_transactions_payment_method ON transactions(payment_method);
CREATE INDEX idx_transactions_created_at ON transactions(created_at);
CREATE INDEX idx_transactions_processed_at ON transactions(processed_at);
CREATE INDEX idx_transactions_gateway_transaction_id ON transactions(gateway_transaction_id);
CREATE INDEX idx_transactions_transaction_number ON transactions(transaction_number);

-- Refunds table for tracking refund operations
CREATE TABLE refunds (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Refund identification
    refund_number VARCHAR(30) UNIQUE NOT NULL, -- Format: REF-YYYYMMDD-XXXXXX
    
    -- Transaction relationship
    transaction_id UUID NOT NULL REFERENCES transactions(id) ON DELETE CASCADE,
    restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    
    -- Refund details
    amount DECIMAL(12, 2) NOT NULL CHECK (amount > 0),
    currency VARCHAR(3) DEFAULT 'INR' NOT NULL,
    reason TEXT NOT NULL,
    status refund_status NOT NULL DEFAULT 'pending',
    
    -- Gateway integration
    gateway_refund_id VARCHAR(255) UNIQUE, -- External gateway refund ID
    gateway_response JSONB DEFAULT '{}',
    
    -- Processing information
    processed_by UUID REFERENCES auth.users(id) ON DELETE SET NULL, -- Staff member who processed
    approved_by UUID REFERENCES auth.users(id) ON DELETE SET NULL, -- Manager who approved
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ, -- When refund was completed/failed
    
    -- Constraints
    CONSTRAINT refunds_amount_not_exceed_transaction CHECK (
        amount <= (SELECT amount FROM transactions WHERE id = transaction_id)
    )
);

-- Create indexes for refunds table
CREATE INDEX idx_refunds_transaction_id ON refunds(transaction_id);
CREATE INDEX idx_refunds_restaurant_id ON refunds(restaurant_id);
CREATE INDEX idx_refunds_status ON refunds(status);
CREATE INDEX idx_refunds_created_at ON refunds(created_at);
CREATE INDEX idx_refunds_processed_by ON refunds(processed_by);

-- Payouts table for restaurant settlement tracking
CREATE TABLE payouts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Payout identification
    payout_number VARCHAR(30) UNIQUE NOT NULL, -- Format: PAY-YYYYMMDD-XXXXXX
    
    -- Restaurant relationship
    restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    
    -- Payout details
    gross_amount DECIMAL(12, 2) NOT NULL CHECK (gross_amount > 0),
    platform_fee DECIMAL(12, 2) DEFAULT 0 CHECK (platform_fee >= 0),
    tax_amount DECIMAL(12, 2) DEFAULT 0 CHECK (tax_amount >= 0),
    net_amount DECIMAL(12, 2) NOT NULL CHECK (net_amount > 0),
    currency VARCHAR(3) DEFAULT 'INR' NOT NULL,
    
    -- Status and scheduling
    status payout_status NOT NULL DEFAULT 'scheduled',
    scheduled_date DATE NOT NULL,
    
    -- Gateway integration
    gateway_payout_id VARCHAR(255) UNIQUE,
    gateway_response JSONB DEFAULT '{}',
    
    -- Bank account information (encrypted)
    bank_account_last4 VARCHAR(4),
    bank_name VARCHAR(100),
    
    -- Date range for transactions included in this payout
    period_start_date DATE NOT NULL,
    period_end_date DATE NOT NULL,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ -- When payout was completed
);

-- Create indexes for payouts table
CREATE INDEX idx_payouts_restaurant_id ON payouts(restaurant_id);
CREATE INDEX idx_payouts_status ON payouts(status);
CREATE INDEX idx_payouts_scheduled_date ON payouts(scheduled_date);
CREATE INDEX idx_payouts_period_dates ON payouts(period_start_date, period_end_date);

-- Transaction audit logs for compliance and tracking
CREATE TABLE transaction_audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Related entity
    transaction_id UUID REFERENCES transactions(id) ON DELETE CASCADE,
    refund_id UUID REFERENCES refunds(id) ON DELETE CASCADE,
    payout_id UUID REFERENCES payouts(id) ON DELETE CASCADE,
    
    -- Audit details
    action VARCHAR(50) NOT NULL, -- CREATE, UPDATE, REFUND, CANCEL, etc.
    entity_type VARCHAR(20) NOT NULL, -- transaction, refund, payout
    
    -- Status changes
    previous_status VARCHAR(50),
    new_status VARCHAR(50),
    
    -- Change details
    changes JSONB DEFAULT '{}', -- Store what changed
    reason TEXT, -- Reason for the change
    
    -- Actor information
    performed_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    ip_address INET,
    user_agent TEXT,
    
    -- Timestamp
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Ensure at least one entity is referenced
    CONSTRAINT audit_logs_entity_check CHECK (
        (transaction_id IS NOT NULL)::int + 
        (refund_id IS NOT NULL)::int + 
        (payout_id IS NOT NULL)::int = 1
    )
);

-- Create indexes for audit logs
CREATE INDEX idx_audit_logs_transaction_id ON transaction_audit_logs(transaction_id);
CREATE INDEX idx_audit_logs_refund_id ON transaction_audit_logs(refund_id);
CREATE INDEX idx_audit_logs_payout_id ON transaction_audit_logs(payout_id);
CREATE INDEX idx_audit_logs_created_at ON transaction_audit_logs(created_at);
CREATE INDEX idx_audit_logs_performed_by ON transaction_audit_logs(performed_by);
CREATE INDEX idx_audit_logs_action ON transaction_audit_logs(action);

-- Enable Row Level Security on all tables
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE refunds ENABLE ROW LEVEL SECURITY;
ALTER TABLE payouts ENABLE ROW LEVEL SECURITY;
ALTER TABLE transaction_audit_logs ENABLE ROW LEVEL SECURITY;

COMMIT;
