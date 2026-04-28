-- Add user_id foreign key to customers table
-- This migration establishes the proper relationship between customers and auth.users

BEGIN;

-- Add user_id column to customers table
-- This will reference auth.users.id to establish proper authentication relationship
ALTER TABLE customers 
ADD COLUMN user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE;

-- Create index for performance on the new foreign key
CREATE INDEX idx_customers_user_id ON customers(user_id);

-- Add constraint to ensure either phone or email is provided (business rule)
ALTER TABLE customers 
ADD CONSTRAINT customers_contact_required 
CHECK (phone IS NOT NULL OR email IS NOT NULL);

-- Add constraint to ensure user_id is unique (one customer record per user)
ALTER TABLE customers 
ADD CONSTRAINT customers_user_id_unique UNIQUE(user_id);

-- Update existing customers to link with auth.users where possible
-- This is a data migration that attempts to match existing customers with auth users
-- by email address (if both exist)
UPDATE customers 
SET user_id = auth_users.id
FROM auth.users AS auth_users
WHERE customers.email = auth_users.email
  AND customers.user_id IS NULL
  AND auth_users.email IS NOT NULL;

-- For customers that couldn't be matched, we'll leave user_id as NULL
-- These represent customers who placed orders without creating accounts
-- They can still be linked later when they sign up

-- Add comment to document the purpose of this column
COMMENT ON COLUMN customers.user_id IS 'Foreign key to auth.users.id - links customer records to authenticated users';

COMMIT;
