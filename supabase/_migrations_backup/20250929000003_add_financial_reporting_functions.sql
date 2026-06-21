-- Financial Reporting and Analytics Functions
-- This migration adds database functions for transaction summaries,
-- revenue analytics, and financial reporting

BEGIN;

-- Function to get transaction summary for a restaurant within a date range
CREATE OR REPLACE FUNCTION get_transaction_summary(
  p_restaurant_id UUID,
  p_start_date DATE DEFAULT CURRENT_DATE - INTERVAL '30 days',
  p_end_date DATE DEFAULT CURRENT_DATE
)
RETURNS TABLE (
  total_transactions BIGINT,
  total_amount DECIMAL(12,2),
  completed_transactions BIGINT,
  completed_amount DECIMAL(12,2),
  pending_transactions BIGINT,
  pending_amount DECIMAL(12,2),
  failed_transactions BIGINT,
  failed_amount DECIMAL(12,2),
  refunded_transactions BIGINT,
  refunded_amount DECIMAL(12,2),
  average_transaction_amount DECIMAL(12,2)
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    COUNT(*)::BIGINT as total_transactions,
    COALESCE(SUM(amount), 0)::DECIMAL(12,2) as total_amount,
    COUNT(*) FILTER (WHERE status = 'completed')::BIGINT as completed_transactions,
    COALESCE(SUM(amount) FILTER (WHERE status = 'completed'), 0)::DECIMAL(12,2) as completed_amount,
    COUNT(*) FILTER (WHERE status IN ('pending', 'processing'))::BIGINT as pending_transactions,
    COALESCE(SUM(amount) FILTER (WHERE status IN ('pending', 'processing')), 0)::DECIMAL(12,2) as pending_amount,
    COUNT(*) FILTER (WHERE status = 'failed')::BIGINT as failed_transactions,
    COALESCE(SUM(amount) FILTER (WHERE status = 'failed'), 0)::DECIMAL(12,2) as failed_amount,
    COUNT(*) FILTER (WHERE status IN ('refunded', 'partially_refunded'))::BIGINT as refunded_transactions,
    COALESCE(SUM(amount) FILTER (WHERE status IN ('refunded', 'partially_refunded')), 0)::DECIMAL(12,2) as refunded_amount,
    COALESCE(AVG(amount) FILTER (WHERE status = 'completed'), 0)::DECIMAL(12,2) as average_transaction_amount
  FROM transactions
  WHERE restaurant_id = p_restaurant_id
    AND DATE(created_at) BETWEEN p_start_date AND p_end_date;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get payment method breakdown
CREATE OR REPLACE FUNCTION get_payment_method_breakdown(
  p_restaurant_id UUID,
  p_start_date DATE DEFAULT CURRENT_DATE - INTERVAL '30 days',
  p_end_date DATE DEFAULT CURRENT_DATE
)
RETURNS TABLE (
  payment_method payment_method_extended,
  transaction_count BIGINT,
  total_amount DECIMAL(12,2),
  percentage DECIMAL(5,2)
) AS $$
DECLARE
  total_completed_amount DECIMAL(12,2);
BEGIN
  -- Get total completed amount for percentage calculation
  SELECT COALESCE(SUM(amount), 0) INTO total_completed_amount
  FROM transactions
  WHERE restaurant_id = p_restaurant_id
    AND status = 'completed'
    AND DATE(created_at) BETWEEN p_start_date AND p_end_date;

  RETURN QUERY
  SELECT 
    t.payment_method,
    COUNT(*)::BIGINT as transaction_count,
    COALESCE(SUM(t.amount), 0)::DECIMAL(12,2) as total_amount,
    CASE 
      WHEN total_completed_amount > 0 THEN 
        (COALESCE(SUM(t.amount), 0) * 100 / total_completed_amount)::DECIMAL(5,2)
      ELSE 0::DECIMAL(5,2)
    END as percentage
  FROM transactions t
  WHERE t.restaurant_id = p_restaurant_id
    AND t.status = 'completed'
    AND DATE(t.created_at) BETWEEN p_start_date AND p_end_date
  GROUP BY t.payment_method
  ORDER BY total_amount DESC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get daily revenue trends
CREATE OR REPLACE FUNCTION get_daily_revenue_trends(
  p_restaurant_id UUID,
  p_start_date DATE DEFAULT CURRENT_DATE - INTERVAL '30 days',
  p_end_date DATE DEFAULT CURRENT_DATE
)
RETURNS TABLE (
  transaction_date DATE,
  transaction_count BIGINT,
  total_revenue DECIMAL(12,2),
  completed_revenue DECIMAL(12,2),
  refunded_amount DECIMAL(12,2),
  net_revenue DECIMAL(12,2)
) AS $$
BEGIN
  RETURN QUERY
  WITH date_series AS (
    SELECT generate_series(p_start_date, p_end_date, '1 day'::interval)::date as date
  ),
  daily_stats AS (
    SELECT 
      DATE(t.created_at) as transaction_date,
      COUNT(*)::BIGINT as transaction_count,
      COALESCE(SUM(t.amount), 0)::DECIMAL(12,2) as total_revenue,
      COALESCE(SUM(t.amount) FILTER (WHERE t.status = 'completed'), 0)::DECIMAL(12,2) as completed_revenue,
      COALESCE(SUM(r.amount), 0)::DECIMAL(12,2) as refunded_amount
    FROM transactions t
    LEFT JOIN refunds r ON t.id = r.transaction_id AND r.status = 'completed'
    WHERE t.restaurant_id = p_restaurant_id
      AND DATE(t.created_at) BETWEEN p_start_date AND p_end_date
    GROUP BY DATE(t.created_at)
  )
  SELECT 
    ds.date as transaction_date,
    COALESCE(daily_stats.transaction_count, 0) as transaction_count,
    COALESCE(daily_stats.total_revenue, 0) as total_revenue,
    COALESCE(daily_stats.completed_revenue, 0) as completed_revenue,
    COALESCE(daily_stats.refunded_amount, 0) as refunded_amount,
    (COALESCE(daily_stats.completed_revenue, 0) - COALESCE(daily_stats.refunded_amount, 0))::DECIMAL(12,2) as net_revenue
  FROM date_series ds
  LEFT JOIN daily_stats ON ds.date = daily_stats.transaction_date
  ORDER BY ds.date;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get transaction history with pagination and filters
CREATE OR REPLACE FUNCTION get_transaction_history(
  p_restaurant_id UUID,
  p_limit INTEGER DEFAULT 50,
  p_offset INTEGER DEFAULT 0,
  p_status transaction_status DEFAULT NULL,
  p_payment_method payment_method_extended DEFAULT NULL,
  p_start_date DATE DEFAULT NULL,
  p_end_date DATE DEFAULT NULL,
  p_search_term TEXT DEFAULT NULL
)
RETURNS TABLE (
  id UUID,
  transaction_number VARCHAR(30),
  order_id UUID,
  amount DECIMAL(12,2),
  currency VARCHAR(3),
  payment_method payment_method_extended,
  status transaction_status,
  customer_name VARCHAR(255),
  customer_phone VARCHAR(20),
  description TEXT,
  gateway_transaction_id VARCHAR(255),
  created_at TIMESTAMPTZ,
  processed_at TIMESTAMPTZ,
  total_count BIGINT
) AS $$
DECLARE
  total_records BIGINT;
BEGIN
  -- Get total count for pagination
  SELECT COUNT(*) INTO total_records
  FROM transactions t
  WHERE t.restaurant_id = p_restaurant_id
    AND (p_status IS NULL OR t.status = p_status)
    AND (p_payment_method IS NULL OR t.payment_method = p_payment_method)
    AND (p_start_date IS NULL OR DATE(t.created_at) >= p_start_date)
    AND (p_end_date IS NULL OR DATE(t.created_at) <= p_end_date)
    AND (p_search_term IS NULL OR 
         t.transaction_number ILIKE '%' || p_search_term || '%' OR
         t.customer_name ILIKE '%' || p_search_term || '%' OR
         t.customer_phone ILIKE '%' || p_search_term || '%' OR
         t.description ILIKE '%' || p_search_term || '%');

  RETURN QUERY
  SELECT 
    t.id,
    t.transaction_number,
    t.order_id,
    t.amount,
    t.currency,
    t.payment_method,
    t.status,
    t.customer_name,
    t.customer_phone,
    t.description,
    t.gateway_transaction_id,
    t.created_at,
    t.processed_at,
    total_records as total_count
  FROM transactions t
  WHERE t.restaurant_id = p_restaurant_id
    AND (p_status IS NULL OR t.status = p_status)
    AND (p_payment_method IS NULL OR t.payment_method = p_payment_method)
    AND (p_start_date IS NULL OR DATE(t.created_at) >= p_start_date)
    AND (p_end_date IS NULL OR DATE(t.created_at) <= p_end_date)
    AND (p_search_term IS NULL OR 
         t.transaction_number ILIKE '%' || p_search_term || '%' OR
         t.customer_name ILIKE '%' || p_search_term || '%' OR
         t.customer_phone ILIKE '%' || p_search_term || '%' OR
         t.description ILIKE '%' || p_search_term || '%')
  ORDER BY t.created_at DESC
  LIMIT p_limit OFFSET p_offset;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get refund history for a restaurant
CREATE OR REPLACE FUNCTION get_refund_history(
  p_restaurant_id UUID,
  p_limit INTEGER DEFAULT 50,
  p_offset INTEGER DEFAULT 0,
  p_status refund_status DEFAULT NULL,
  p_start_date DATE DEFAULT NULL,
  p_end_date DATE DEFAULT NULL
)
RETURNS TABLE (
  id UUID,
  refund_number VARCHAR(30),
  transaction_id UUID,
  transaction_number VARCHAR(30),
  amount DECIMAL(12,2),
  reason TEXT,
  status refund_status,
  processed_by UUID,
  processed_by_name VARCHAR(255),
  created_at TIMESTAMPTZ,
  processed_at TIMESTAMPTZ,
  total_count BIGINT
) AS $$
DECLARE
  total_records BIGINT;
BEGIN
  -- Get total count for pagination
  SELECT COUNT(*) INTO total_records
  FROM refunds r
  JOIN transactions t ON r.transaction_id = t.id
  WHERE r.restaurant_id = p_restaurant_id
    AND (p_status IS NULL OR r.status = p_status)
    AND (p_start_date IS NULL OR DATE(r.created_at) >= p_start_date)
    AND (p_end_date IS NULL OR DATE(r.created_at) <= p_end_date);

  RETURN QUERY
  SELECT 
    r.id,
    r.refund_number,
    r.transaction_id,
    t.transaction_number,
    r.amount,
    r.reason,
    r.status,
    r.processed_by,
    COALESCE(u.raw_user_meta_data->>'name', u.email) as processed_by_name,
    r.created_at,
    r.processed_at,
    total_records as total_count
  FROM refunds r
  JOIN transactions t ON r.transaction_id = t.id
  LEFT JOIN auth.users u ON r.processed_by = u.id
  WHERE r.restaurant_id = p_restaurant_id
    AND (p_status IS NULL OR r.status = p_status)
    AND (p_start_date IS NULL OR DATE(r.created_at) >= p_start_date)
    AND (p_end_date IS NULL OR DATE(r.created_at) <= p_end_date)
  ORDER BY r.created_at DESC
  LIMIT p_limit OFFSET p_offset;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get payout history for a restaurant
CREATE OR REPLACE FUNCTION get_payout_history(
  p_restaurant_id UUID,
  p_limit INTEGER DEFAULT 50,
  p_offset INTEGER DEFAULT 0,
  p_status payout_status DEFAULT NULL
)
RETURNS TABLE (
  id UUID,
  payout_number VARCHAR(30),
  gross_amount DECIMAL(12,2),
  platform_fee DECIMAL(12,2),
  tax_amount DECIMAL(12,2),
  net_amount DECIMAL(12,2),
  status payout_status,
  scheduled_date DATE,
  period_start_date DATE,
  period_end_date DATE,
  bank_account_last4 VARCHAR(4),
  bank_name VARCHAR(100),
  created_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  total_count BIGINT
) AS $$
DECLARE
  total_records BIGINT;
BEGIN
  -- Get total count for pagination
  SELECT COUNT(*) INTO total_records
  FROM payouts p
  WHERE p.restaurant_id = p_restaurant_id
    AND (p_status IS NULL OR p.status = p_status);

  RETURN QUERY
  SELECT 
    p.id,
    p.payout_number,
    p.gross_amount,
    p.platform_fee,
    p.tax_amount,
    p.net_amount,
    p.status,
    p.scheduled_date,
    p.period_start_date,
    p.period_end_date,
    p.bank_account_last4,
    p.bank_name,
    p.created_at,
    p.completed_at,
    total_records as total_count
  FROM payouts p
  WHERE p.restaurant_id = p_restaurant_id
    AND (p_status IS NULL OR p.status = p_status)
  ORDER BY p.created_at DESC
  LIMIT p_limit OFFSET p_offset;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant execute permissions on functions
GRANT EXECUTE ON FUNCTION get_transaction_summary TO authenticated;
GRANT EXECUTE ON FUNCTION get_payment_method_breakdown TO authenticated;
GRANT EXECUTE ON FUNCTION get_daily_revenue_trends TO authenticated;
GRANT EXECUTE ON FUNCTION get_transaction_history TO authenticated;
GRANT EXECUTE ON FUNCTION get_refund_history TO authenticated;
GRANT EXECUTE ON FUNCTION get_payout_history TO authenticated;

COMMIT;
