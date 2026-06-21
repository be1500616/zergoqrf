-- Transaction Management RLS Policies and Functions
-- This migration adds Row Level Security policies and utility functions
-- for the transaction management system

BEGIN;

-- Helper function to check if user has restaurant access
CREATE OR REPLACE FUNCTION auth.user_has_restaurant_access(target_restaurant_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
  -- Check if user is authenticated
  IF auth.uid() IS NULL THEN
    RETURN FALSE;
  END IF;
  
  -- Check if user has access to the restaurant through restaurant_staff table
  RETURN EXISTS (
    SELECT 1 FROM restaurant_staff 
    WHERE restaurant_id = target_restaurant_id 
    AND user_id = auth.uid() 
    AND is_active = true
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Helper function to check if user has financial management permissions
CREATE OR REPLACE FUNCTION auth.user_has_financial_access(target_restaurant_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
  -- Check if user is authenticated
  IF auth.uid() IS NULL THEN
    RETURN FALSE;
  END IF;
  
  -- Check if user has financial management role (owner or manager)
  RETURN EXISTS (
    SELECT 1 FROM restaurant_staff 
    WHERE restaurant_id = target_restaurant_id 
    AND user_id = auth.uid() 
    AND role IN ('owner', 'manager')
    AND is_active = true
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- RLS Policies for transactions table
CREATE POLICY "Users can view transactions for their restaurants" ON transactions
  FOR SELECT USING (auth.user_has_restaurant_access(restaurant_id));

CREATE POLICY "Users can insert transactions for their restaurants" ON transactions
  FOR INSERT WITH CHECK (auth.user_has_restaurant_access(restaurant_id));

CREATE POLICY "Financial managers can update transactions" ON transactions
  FOR UPDATE USING (auth.user_has_financial_access(restaurant_id));

-- RLS Policies for refunds table
CREATE POLICY "Financial managers can view refunds" ON refunds
  FOR SELECT USING (auth.user_has_financial_access(restaurant_id));

CREATE POLICY "Financial managers can create refunds" ON refunds
  FOR INSERT WITH CHECK (auth.user_has_financial_access(restaurant_id));

CREATE POLICY "Financial managers can update refunds" ON refunds
  FOR UPDATE USING (auth.user_has_financial_access(restaurant_id));

-- RLS Policies for payouts table
CREATE POLICY "Financial managers can view payouts" ON payouts
  FOR SELECT USING (auth.user_has_financial_access(restaurant_id));

CREATE POLICY "System can manage payouts" ON payouts
  FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- RLS Policies for transaction_audit_logs table
CREATE POLICY "Financial managers can view audit logs" ON transaction_audit_logs
  FOR SELECT USING (
    (transaction_id IS NOT NULL AND auth.user_has_financial_access(
      (SELECT restaurant_id FROM transactions WHERE id = transaction_id)
    )) OR
    (refund_id IS NOT NULL AND auth.user_has_financial_access(
      (SELECT restaurant_id FROM refunds WHERE id = refund_id)
    )) OR
    (payout_id IS NOT NULL AND auth.user_has_financial_access(
      (SELECT restaurant_id FROM payouts WHERE id = payout_id)
    ))
  );

CREATE POLICY "System can insert audit logs" ON transaction_audit_logs
  FOR INSERT WITH CHECK (true); -- System-level logging

-- Function to generate transaction numbers
CREATE OR REPLACE FUNCTION generate_transaction_number()
RETURNS TEXT AS $$
DECLARE
  date_part TEXT;
  sequence_part TEXT;
  counter INTEGER;
BEGIN
  -- Get current date in YYYYMMDD format
  date_part := to_char(NOW(), 'YYYYMMDD');
  
  -- Get next sequence number for today
  SELECT COALESCE(MAX(
    CAST(SUBSTRING(transaction_number FROM 'TXN-\d{8}-(\d{6})') AS INTEGER)
  ), 0) + 1
  INTO counter
  FROM transactions
  WHERE transaction_number LIKE 'TXN-' || date_part || '-%';
  
  -- Format sequence with leading zeros
  sequence_part := LPAD(counter::TEXT, 6, '0');
  
  RETURN 'TXN-' || date_part || '-' || sequence_part;
END;
$$ LANGUAGE plpgsql;

-- Function to generate refund numbers
CREATE OR REPLACE FUNCTION generate_refund_number()
RETURNS TEXT AS $$
DECLARE
  date_part TEXT;
  sequence_part TEXT;
  counter INTEGER;
BEGIN
  -- Get current date in YYYYMMDD format
  date_part := to_char(NOW(), 'YYYYMMDD');
  
  -- Get next sequence number for today
  SELECT COALESCE(MAX(
    CAST(SUBSTRING(refund_number FROM 'REF-\d{8}-(\d{6})') AS INTEGER)
  ), 0) + 1
  INTO counter
  FROM refunds
  WHERE refund_number LIKE 'REF-' || date_part || '-%';
  
  -- Format sequence with leading zeros
  sequence_part := LPAD(counter::TEXT, 6, '0');
  
  RETURN 'REF-' || date_part || '-' || sequence_part;
END;
$$ LANGUAGE plpgsql;

-- Function to generate payout numbers
CREATE OR REPLACE FUNCTION generate_payout_number()
RETURNS TEXT AS $$
DECLARE
  date_part TEXT;
  sequence_part TEXT;
  counter INTEGER;
BEGIN
  -- Get current date in YYYYMMDD format
  date_part := to_char(NOW(), 'YYYYMMDD');
  
  -- Get next sequence number for today
  SELECT COALESCE(MAX(
    CAST(SUBSTRING(payout_number FROM 'PAY-\d{8}-(\d{6})') AS INTEGER)
  ), 0) + 1
  INTO counter
  FROM payouts
  WHERE payout_number LIKE 'PAY-' || date_part || '-%';
  
  -- Format sequence with leading zeros
  sequence_part := LPAD(counter::TEXT, 6, '0');
  
  RETURN 'PAY-' || date_part || '-' || sequence_part;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-generate transaction numbers
CREATE OR REPLACE FUNCTION set_transaction_number()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.transaction_number IS NULL OR NEW.transaction_number = '' THEN
    NEW.transaction_number := generate_transaction_number();
  END IF;
  NEW.updated_at := NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_set_transaction_number
  BEFORE INSERT OR UPDATE ON transactions
  FOR EACH ROW EXECUTE FUNCTION set_transaction_number();

-- Trigger to auto-generate refund numbers
CREATE OR REPLACE FUNCTION set_refund_number()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.refund_number IS NULL OR NEW.refund_number = '' THEN
    NEW.refund_number := generate_refund_number();
  END IF;
  NEW.updated_at := NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_set_refund_number
  BEFORE INSERT OR UPDATE ON refunds
  FOR EACH ROW EXECUTE FUNCTION set_refund_number();

-- Trigger to auto-generate payout numbers
CREATE OR REPLACE FUNCTION set_payout_number()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.payout_number IS NULL OR NEW.payout_number = '' THEN
    NEW.payout_number := generate_payout_number();
  END IF;
  NEW.updated_at := NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_set_payout_number
  BEFORE INSERT OR UPDATE ON payouts
  FOR EACH ROW EXECUTE FUNCTION set_payout_number();

-- Function to create audit log entries
CREATE OR REPLACE FUNCTION create_transaction_audit_log(
  p_transaction_id UUID DEFAULT NULL,
  p_refund_id UUID DEFAULT NULL,
  p_payout_id UUID DEFAULT NULL,
  p_action VARCHAR(50) DEFAULT NULL,
  p_entity_type VARCHAR(20) DEFAULT NULL,
  p_previous_status VARCHAR(50) DEFAULT NULL,
  p_new_status VARCHAR(50) DEFAULT NULL,
  p_changes JSONB DEFAULT '{}',
  p_reason TEXT DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
  audit_id UUID;
BEGIN
  INSERT INTO transaction_audit_logs (
    transaction_id,
    refund_id,
    payout_id,
    action,
    entity_type,
    previous_status,
    new_status,
    changes,
    reason,
    performed_by,
    ip_address,
    user_agent
  ) VALUES (
    p_transaction_id,
    p_refund_id,
    p_payout_id,
    p_action,
    p_entity_type,
    p_previous_status,
    p_new_status,
    p_changes,
    p_reason,
    auth.uid(),
    inet_client_addr(),
    current_setting('request.headers', true)::json->>'user-agent'
  ) RETURNING id INTO audit_id;
  
  RETURN audit_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT SELECT, INSERT, UPDATE ON transactions TO authenticated;
GRANT SELECT, INSERT, UPDATE ON refunds TO authenticated;
GRANT SELECT ON payouts TO authenticated;
GRANT SELECT ON transaction_audit_logs TO authenticated;
GRANT EXECUTE ON FUNCTION auth.user_has_restaurant_access TO authenticated;
GRANT EXECUTE ON FUNCTION auth.user_has_financial_access TO authenticated;
GRANT EXECUTE ON FUNCTION create_transaction_audit_log TO authenticated;

COMMIT;
