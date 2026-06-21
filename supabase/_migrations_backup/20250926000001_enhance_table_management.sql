-- Enhanced Table Management Schema
-- This migration enhances the existing tables schema with comprehensive table management features

BEGIN;

-- Create ENUM types for better data integrity
CREATE TYPE table_status AS ENUM ('available', 'occupied', 'reserved', 'cleaning', 'maintenance', 'out_of_order');
CREATE TYPE table_shape AS ENUM ('round', 'square', 'rectangular', 'oval');
CREATE TYPE table_category AS ENUM ('regular', 'vip', 'outdoor', 'bar', 'counter', 'booth');

-- Create floors table for multi-floor restaurant support
CREATE TABLE IF NOT EXISTS floors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    floor_number INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT true,
    layout_config JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(restaurant_id, floor_number),
    UNIQUE(restaurant_id, name)
);

-- Enhance the existing tables table with comprehensive fields
-- First, drop the existing status column and recreate with proper ENUM
ALTER TABLE tables DROP COLUMN IF EXISTS status;
ALTER TABLE tables ADD COLUMN status table_status DEFAULT 'available';

-- Add new columns for enhanced table management
ALTER TABLE tables ADD COLUMN IF NOT EXISTS floor_id UUID REFERENCES floors(id) ON DELETE SET NULL;
ALTER TABLE tables ADD COLUMN IF NOT EXISTS shape table_shape DEFAULT 'round';
ALTER TABLE tables ADD COLUMN IF NOT EXISTS category table_category DEFAULT 'regular';
ALTER TABLE tables ADD COLUMN IF NOT EXISTS dimensions JSONB DEFAULT '{"width": 80, "height": 80}';
ALTER TABLE tables ADD COLUMN IF NOT EXISTS rotation DECIMAL(5,2) DEFAULT 0.0;
ALTER TABLE tables ADD COLUMN IF NOT EXISTS special_requirements TEXT[];
ALTER TABLE tables ADD COLUMN IF NOT EXISTS is_accessible BOOLEAN DEFAULT false;
ALTER TABLE tables ADD COLUMN IF NOT EXISTS has_power_outlet BOOLEAN DEFAULT false;
ALTER TABLE tables ADD COLUMN IF NOT EXISTS has_window_view BOOLEAN DEFAULT false;
ALTER TABLE tables ADD COLUMN IF NOT EXISTS min_party_size INTEGER DEFAULT 1;
ALTER TABLE tables ADD COLUMN IF NOT EXISTS max_party_size INTEGER;
ALTER TABLE tables ADD COLUMN IF NOT EXISTS qr_code_url TEXT;
ALTER TABLE tables ADD COLUMN IF NOT EXISTS qr_code_data JSONB;
ALTER TABLE tables ADD COLUMN IF NOT EXISTS last_cleaned_at TIMESTAMPTZ;
ALTER TABLE tables ADD COLUMN IF NOT EXISTS last_occupied_at TIMESTAMPTZ;
ALTER TABLE tables ADD COLUMN IF NOT EXISTS notes TEXT;
ALTER TABLE tables ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true;

-- Update max_party_size to match capacity if not set
UPDATE tables SET max_party_size = capacity WHERE max_party_size IS NULL;

-- Add constraints
ALTER TABLE tables ADD CONSTRAINT tables_capacity_positive CHECK (capacity > 0);
ALTER TABLE tables ADD CONSTRAINT tables_min_party_size_positive CHECK (min_party_size > 0);
ALTER TABLE tables ADD CONSTRAINT tables_max_party_size_valid CHECK (max_party_size >= min_party_size);
ALTER TABLE tables ADD CONSTRAINT tables_rotation_valid CHECK (rotation >= 0 AND rotation < 360);
ALTER TABLE tables ADD CONSTRAINT tables_table_number_restaurant_unique UNIQUE (restaurant_id, table_number);

-- Create table reservations table for advanced reservation management
CREATE TABLE IF NOT EXISTS table_reservations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_id UUID NOT NULL REFERENCES tables(id) ON DELETE CASCADE,
    restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    customer_name VARCHAR(255) NOT NULL,
    customer_phone VARCHAR(20),
    customer_email VARCHAR(255),
    party_size INTEGER NOT NULL,
    reservation_time TIMESTAMPTZ NOT NULL,
    duration_minutes INTEGER DEFAULT 120,
    status VARCHAR(50) DEFAULT 'confirmed' CHECK (status IN ('confirmed', 'seated', 'completed', 'cancelled', 'no_show')),
    special_requests TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create table sessions table for tracking table occupancy
CREATE TABLE IF NOT EXISTS table_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_id UUID NOT NULL REFERENCES tables(id) ON DELETE CASCADE,
    restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    session_start TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    session_end TIMESTAMPTZ,
    party_size INTEGER,
    server_id UUID REFERENCES restaurant_staff(id),
    order_total DECIMAL(10,2),
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'completed', 'abandoned')),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create table maintenance logs
CREATE TABLE IF NOT EXISTS table_maintenance_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_id UUID NOT NULL REFERENCES tables(id) ON DELETE CASCADE,
    restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    maintenance_type VARCHAR(50) NOT NULL CHECK (maintenance_type IN ('cleaning', 'repair', 'inspection', 'setup')),
    performed_by UUID REFERENCES restaurant_staff(id),
    performed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    description TEXT,
    duration_minutes INTEGER,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_tables_restaurant_id ON tables(restaurant_id);
CREATE INDEX IF NOT EXISTS idx_tables_floor_id ON tables(floor_id);
CREATE INDEX IF NOT EXISTS idx_tables_status ON tables(status);
CREATE INDEX IF NOT EXISTS idx_tables_category ON tables(category);
CREATE INDEX IF NOT EXISTS idx_tables_is_active ON tables(is_active);

CREATE INDEX IF NOT EXISTS idx_floors_restaurant_id ON floors(restaurant_id);
CREATE INDEX IF NOT EXISTS idx_floors_is_active ON floors(is_active);

CREATE INDEX IF NOT EXISTS idx_table_reservations_table_id ON table_reservations(table_id);
CREATE INDEX IF NOT EXISTS idx_table_reservations_restaurant_id ON table_reservations(restaurant_id);
CREATE INDEX IF NOT EXISTS idx_table_reservations_reservation_time ON table_reservations(reservation_time);
CREATE INDEX IF NOT EXISTS idx_table_reservations_status ON table_reservations(status);

CREATE INDEX IF NOT EXISTS idx_table_sessions_table_id ON table_sessions(table_id);
CREATE INDEX IF NOT EXISTS idx_table_sessions_restaurant_id ON table_sessions(restaurant_id);
CREATE INDEX IF NOT EXISTS idx_table_sessions_status ON table_sessions(status);
CREATE INDEX IF NOT EXISTS idx_table_sessions_session_start ON table_sessions(session_start);

CREATE INDEX IF NOT EXISTS idx_table_maintenance_logs_table_id ON table_maintenance_logs(table_id);
CREATE INDEX IF NOT EXISTS idx_table_maintenance_logs_restaurant_id ON table_maintenance_logs(restaurant_id);
CREATE INDEX IF NOT EXISTS idx_table_maintenance_logs_performed_at ON table_maintenance_logs(performed_at);

-- Enable RLS on new tables
ALTER TABLE floors ENABLE ROW LEVEL SECURITY;
ALTER TABLE table_reservations ENABLE ROW LEVEL SECURITY;
ALTER TABLE table_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE table_maintenance_logs ENABLE ROW LEVEL SECURITY;

-- RLS Policies for floors
CREATE POLICY "floors_select_staff" ON floors
    FOR SELECT USING (
        auth.get_restaurant_id() = restaurant_id
    );

CREATE POLICY "floors_insert_manager" ON floors
    FOR INSERT WITH CHECK (
        auth.get_restaurant_id() = restaurant_id AND
        auth.get_user_role() IN ('owner', 'manager')
    );

CREATE POLICY "floors_update_manager" ON floors
    FOR UPDATE USING (
        auth.get_restaurant_id() = restaurant_id AND
        auth.get_user_role() IN ('owner', 'manager')
    );

CREATE POLICY "floors_delete_manager" ON floors
    FOR DELETE USING (
        auth.get_restaurant_id() = restaurant_id AND
        auth.get_user_role() IN ('owner', 'manager')
    );

-- RLS Policies for table_reservations
CREATE POLICY "table_reservations_select_staff" ON table_reservations
    FOR SELECT USING (
        auth.get_restaurant_id() = restaurant_id
    );

CREATE POLICY "table_reservations_insert_staff" ON table_reservations
    FOR INSERT WITH CHECK (
        auth.get_restaurant_id() = restaurant_id
    );

CREATE POLICY "table_reservations_update_staff" ON table_reservations
    FOR UPDATE USING (
        auth.get_restaurant_id() = restaurant_id
    );

CREATE POLICY "table_reservations_delete_manager" ON table_reservations
    FOR DELETE USING (
        auth.get_restaurant_id() = restaurant_id AND
        auth.get_user_role() IN ('owner', 'manager')
    );

-- RLS Policies for table_sessions
CREATE POLICY "table_sessions_select_staff" ON table_sessions
    FOR SELECT USING (
        auth.get_restaurant_id() = restaurant_id
    );

CREATE POLICY "table_sessions_insert_staff" ON table_sessions
    FOR INSERT WITH CHECK (
        auth.get_restaurant_id() = restaurant_id
    );

CREATE POLICY "table_sessions_update_staff" ON table_sessions
    FOR UPDATE USING (
        auth.get_restaurant_id() = restaurant_id
    );

-- RLS Policies for table_maintenance_logs
CREATE POLICY "table_maintenance_logs_select_staff" ON table_maintenance_logs
    FOR SELECT USING (
        auth.get_restaurant_id() = restaurant_id
    );

CREATE POLICY "table_maintenance_logs_insert_staff" ON table_maintenance_logs
    FOR INSERT WITH CHECK (
        auth.get_restaurant_id() = restaurant_id
    );

-- Update existing tables RLS policies to be more comprehensive
DROP POLICY IF EXISTS "tables_select_public" ON tables;
DROP POLICY IF EXISTS "tables_insert_staff" ON tables;
DROP POLICY IF EXISTS "tables_update_staff" ON tables;
DROP POLICY IF EXISTS "tables_delete_manager" ON tables;

-- New comprehensive RLS policies for tables
CREATE POLICY "tables_select_staff" ON tables
    FOR SELECT USING (
        auth.get_restaurant_id() = restaurant_id
    );

CREATE POLICY "tables_insert_manager" ON tables
    FOR INSERT WITH CHECK (
        auth.get_restaurant_id() = restaurant_id AND
        auth.get_user_role() IN ('owner', 'manager')
    );

CREATE POLICY "tables_update_staff" ON tables
    FOR UPDATE USING (
        auth.get_restaurant_id() = restaurant_id
    );

CREATE POLICY "tables_delete_manager" ON tables
    FOR DELETE USING (
        auth.get_restaurant_id() = restaurant_id AND
        auth.get_user_role() IN ('owner', 'manager')
    );

-- Create functions for common operations
CREATE OR REPLACE FUNCTION update_table_status(
    table_id_param UUID,
    new_status table_status,
    restaurant_id_param UUID DEFAULT NULL
) RETURNS BOOLEAN AS $$
DECLARE
    target_restaurant_id UUID;
BEGIN
    -- Get restaurant_id from JWT if not provided
    IF restaurant_id_param IS NULL THEN
        target_restaurant_id := auth.get_restaurant_id();
    ELSE
        target_restaurant_id := restaurant_id_param;
    END IF;
    
    -- Update table status
    UPDATE tables 
    SET status = new_status, updated_at = NOW()
    WHERE id = table_id_param AND restaurant_id = target_restaurant_id;
    
    -- Return true if update was successful
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION get_table_occupancy_stats(restaurant_id_param UUID)
RETURNS TABLE(
    total_tables INTEGER,
    available_tables INTEGER,
    occupied_tables INTEGER,
    reserved_tables INTEGER,
    cleaning_tables INTEGER,
    occupancy_rate DECIMAL(5,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::INTEGER as total_tables,
        COUNT(CASE WHEN status = 'available' THEN 1 END)::INTEGER as available_tables,
        COUNT(CASE WHEN status = 'occupied' THEN 1 END)::INTEGER as occupied_tables,
        COUNT(CASE WHEN status = 'reserved' THEN 1 END)::INTEGER as reserved_tables,
        COUNT(CASE WHEN status = 'cleaning' THEN 1 END)::INTEGER as cleaning_tables,
        CASE 
            WHEN COUNT(*) > 0 THEN 
                ROUND((COUNT(CASE WHEN status IN ('occupied', 'reserved') THEN 1 END)::DECIMAL / COUNT(*)::DECIMAL) * 100, 2)
            ELSE 0.00
        END as occupancy_rate
    FROM tables 
    WHERE restaurant_id = restaurant_id_param AND is_active = true;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers to all relevant tables
CREATE TRIGGER update_tables_updated_at BEFORE UPDATE ON tables
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_floors_updated_at BEFORE UPDATE ON floors
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_table_reservations_updated_at BEFORE UPDATE ON table_reservations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_table_sessions_updated_at BEFORE UPDATE ON table_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMIT;
