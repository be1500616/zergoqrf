-- QR Generation Setup Migration
-- This migration sets up the necessary infrastructure for QR code generation

BEGIN;

-- Create storage bucket for QR codes if it doesn't exist
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'qr-codes',
    'qr-codes',
    true,
    10485760, -- 10MB limit
    ARRAY['image/png', 'image/svg+xml', 'application/pdf', 'application/zip']
)
ON CONFLICT (id) DO NOTHING;

-- Create RLS policies for QR codes bucket
DROP POLICY IF EXISTS "QR codes are publicly accessible" ON storage.objects;
CREATE POLICY "QR codes are publicly accessible" ON storage.objects
    FOR SELECT USING (bucket_id = 'qr-codes');

DROP POLICY IF EXISTS "Restaurant staff can upload QR codes" ON storage.objects;
CREATE POLICY "Restaurant staff can upload QR codes" ON storage.objects
    FOR INSERT WITH CHECK (
        bucket_id = 'qr-codes' AND
        auth.jwt() ->> 'role' IN ('owner', 'manager', 'staff')
    );

DROP POLICY IF EXISTS "Restaurant staff can update their QR codes" ON storage.objects;
CREATE POLICY "Restaurant staff can update their QR codes" ON storage.objects
    FOR UPDATE USING (
        bucket_id = 'qr-codes' AND
        auth.jwt() ->> 'role' IN ('owner', 'manager', 'staff')
    );

DROP POLICY IF EXISTS "Restaurant staff can delete their QR codes" ON storage.objects;
CREATE POLICY "Restaurant staff can delete their QR codes" ON storage.objects
    FOR DELETE USING (
        bucket_id = 'qr-codes' AND
        auth.jwt() ->> 'role' IN ('owner', 'manager', 'staff')
    );

-- Create QR generation logs table for tracking and analytics
CREATE TABLE IF NOT EXISTS qr_generation_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    table_id UUID REFERENCES tables(id) ON DELETE CASCADE,
    generation_type VARCHAR(20) NOT NULL CHECK (generation_type IN ('single', 'bulk')),
    request_id VARCHAR(255),
    format VARCHAR(10) NOT NULL CHECK (format IN ('png', 'svg', 'pdf')),
    config JSONB DEFAULT '{}',
    file_size INTEGER,
    storage_url TEXT,
    generation_time_ms INTEGER,
    status VARCHAR(20) DEFAULT 'success' CHECK (status IN ('success', 'failed', 'partial')),
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_qr_generation_logs_restaurant_id ON qr_generation_logs(restaurant_id);
CREATE INDEX IF NOT EXISTS idx_qr_generation_logs_table_id ON qr_generation_logs(table_id);
CREATE INDEX IF NOT EXISTS idx_qr_generation_logs_created_at ON qr_generation_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_qr_generation_logs_status ON qr_generation_logs(status);

-- Enable RLS on QR generation logs
ALTER TABLE qr_generation_logs ENABLE ROW LEVEL SECURITY;

-- RLS Policies for QR generation logs
CREATE POLICY "qr_generation_logs_select_staff" ON qr_generation_logs
    FOR SELECT USING (
        auth.jwt() ->> 'restaurant_id' = restaurant_id::text
    );

CREATE POLICY "qr_generation_logs_insert_staff" ON qr_generation_logs
    FOR INSERT WITH CHECK (
        auth.jwt() ->> 'restaurant_id' = restaurant_id::text
    );

-- Create function to get QR generation statistics
CREATE OR REPLACE FUNCTION get_qr_generation_stats(restaurant_id_param UUID)
RETURNS TABLE(
    total_tables INTEGER,
    tables_with_qr INTEGER,
    tables_without_qr INTEGER,
    last_generation_date TIMESTAMPTZ,
    total_generations INTEGER,
    qr_coverage_percentage DECIMAL(5,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(t.*)::INTEGER as total_tables,
        COUNT(CASE WHEN t.qr_code_data IS NOT NULL THEN 1 END)::INTEGER as tables_with_qr,
        COUNT(CASE WHEN t.qr_code_data IS NULL THEN 1 END)::INTEGER as tables_without_qr,
        MAX(qgl.created_at) as last_generation_date,
        COUNT(qgl.*)::INTEGER as total_generations,
        CASE
            WHEN COUNT(t.*) > 0 THEN
                ROUND((COUNT(CASE WHEN t.qr_code_data IS NOT NULL THEN 1 END)::DECIMAL / COUNT(t.*)::DECIMAL) * 100, 2)
            ELSE 0.00
        END as qr_coverage_percentage
    FROM tables t
    LEFT JOIN qr_generation_logs qgl ON qgl.table_id = t.id AND qgl.status = 'success'
    WHERE t.restaurant_id = restaurant_id_param AND t.is_active = true
    AND auth.jwt() ->> 'restaurant_id' = restaurant_id_param::text;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to clean up old QR generation logs (optional, for maintenance)
CREATE OR REPLACE FUNCTION cleanup_old_qr_logs(days_to_keep INTEGER DEFAULT 90)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM qr_generation_logs 
    WHERE created_at < NOW() - INTERVAL '1 day' * days_to_keep;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to update table QR metadata
CREATE OR REPLACE FUNCTION update_table_qr_metadata(
    table_id_param UUID,
    qr_url_param TEXT,
    storage_url_param TEXT,
    format_param TEXT,
    restaurant_code_param TEXT
) RETURNS BOOLEAN AS $$
BEGIN
    UPDATE tables 
    SET 
        qr_token = restaurant_code_param || '_' || table_id_param::TEXT,
        qr_code_data = jsonb_build_object(
            'token', restaurant_code_param || '_' || table_id_param::TEXT,
            'url', qr_url_param,
            'data', jsonb_build_object(
                'restaurant_code', restaurant_code_param,
                'table_id', table_id_param::TEXT,
                'generated_at', NOW()::TEXT,
                'format', format_param,
                'storage_url', storage_url_param
            )
        ),
        updated_at = NOW()
    WHERE id = table_id_param;
    
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMIT;
