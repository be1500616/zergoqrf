-- Sample Table Management Data
-- This migration adds sample data for testing table management features

BEGIN;

-- Insert sample floors for existing restaurants
-- Note: This assumes there are existing restaurants in the system
INSERT INTO floors (restaurant_id, name, description, floor_number, layout_config)
SELECT 
    r.id,
    'Ground Floor',
    'Main dining area with regular seating',
    1,
    '{"width": 800, "height": 600, "grid_size": 16, "background_color": "#FAFAFA"}'::jsonb
FROM restaurants r
WHERE NOT EXISTS (
    SELECT 1 FROM floors f WHERE f.restaurant_id = r.id AND f.floor_number = 1
);

-- Insert sample tables for each restaurant's ground floor
WITH restaurant_floors AS (
    SELECT r.id as restaurant_id, f.id as floor_id
    FROM restaurants r
    JOIN floors f ON f.restaurant_id = r.id AND f.floor_number = 1
)
INSERT INTO tables (
    restaurant_id, 
    floor_id, 
    table_number, 
    capacity, 
    shape, 
    category, 
    position, 
    dimensions,
    qr_token,
    status,
    is_accessible,
    has_window_view
)
SELECT 
    rf.restaurant_id,
    rf.floor_id,
    'T' || LPAD(generate_series::text, 2, '0'),
    CASE 
        WHEN generate_series <= 4 THEN 2
        WHEN generate_series <= 8 THEN 4
        WHEN generate_series <= 10 THEN 6
        ELSE 8
    END,
    CASE 
        WHEN generate_series % 3 = 0 THEN 'round'::table_shape
        WHEN generate_series % 3 = 1 THEN 'square'::table_shape
        ELSE 'rectangular'::table_shape
    END,
    CASE 
        WHEN generate_series <= 2 THEN 'vip'::table_category
        WHEN generate_series <= 8 THEN 'regular'::table_category
        ELSE 'outdoor'::table_category
    END,
    jsonb_build_object(
        'x', (generate_series % 4) * 150 + 100,
        'y', ((generate_series - 1) / 4) * 120 + 100
    ),
    CASE 
        WHEN generate_series % 3 = 0 THEN '{"width": 80, "height": 80}'::jsonb
        WHEN generate_series % 3 = 1 THEN '{"width": 100, "height": 60}'::jsonb
        ELSE '{"width": 120, "height": 80}'::jsonb
    END,
    'table_' || rf.restaurant_id::text || '_' || generate_series::text,
    'available'::table_status,
    generate_series <= 2, -- First 2 tables are accessible
    generate_series % 5 = 0 -- Every 5th table has window view
FROM restaurant_floors rf
CROSS JOIN generate_series(1, 12)
WHERE NOT EXISTS (
    SELECT 1 FROM tables t 
    WHERE t.restaurant_id = rf.restaurant_id 
    AND t.table_number = 'T' || LPAD(generate_series::text, 2, '0')
);

-- Insert sample reservations for testing
INSERT INTO table_reservations (
    table_id,
    restaurant_id,
    customer_name,
    customer_phone,
    customer_email,
    party_size,
    reservation_time,
    duration_minutes,
    status,
    special_requests
)
SELECT 
    t.id,
    t.restaurant_id,
    'John Doe',
    '+1234567890',
    'john.doe@example.com',
    t.capacity / 2,
    NOW() + INTERVAL '2 hours',
    120,
    'confirmed',
    'Window seat preferred'
FROM tables t
WHERE t.table_number IN ('T01', 'T05')
AND NOT EXISTS (
    SELECT 1 FROM table_reservations tr 
    WHERE tr.table_id = t.id 
    AND tr.reservation_time > NOW()
);

-- Update some tables to have different statuses for testing
UPDATE tables 
SET status = 'occupied'::table_status, 
    last_occupied_at = NOW() - INTERVAL '45 minutes'
WHERE table_number IN ('T02', 'T06', 'T10');

UPDATE tables 
SET status = 'reserved'::table_status
WHERE table_number IN ('T01', 'T05');

UPDATE tables 
SET status = 'cleaning'::table_status,
    last_cleaned_at = NOW() - INTERVAL '15 minutes'
WHERE table_number IN ('T03');

-- Insert sample maintenance logs
INSERT INTO table_maintenance_logs (
    table_id,
    restaurant_id,
    maintenance_type,
    performed_at,
    description,
    duration_minutes
)
SELECT 
    t.id,
    t.restaurant_id,
    'cleaning',
    NOW() - INTERVAL '2 hours',
    'Regular table cleaning and sanitization',
    15
FROM tables t
WHERE t.table_number IN ('T01', 'T02', 'T03', 'T04');

-- Insert sample table sessions for occupied tables
INSERT INTO table_sessions (
    table_id,
    restaurant_id,
    session_start,
    party_size,
    status
)
SELECT 
    t.id,
    t.restaurant_id,
    NOW() - INTERVAL '45 minutes',
    t.capacity / 2,
    'active'
FROM tables t
WHERE t.status = 'occupied';

COMMIT;
