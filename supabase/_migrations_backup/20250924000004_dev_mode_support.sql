-- Development mode support migration
-- This migration adds support for development mode by creating a users table
-- and modifying constraints to support mock users

BEGIN;

-- Create a local users table for development mode
-- This mirrors the structure of auth.users but allows us to create mock users
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    encrypted_password VARCHAR(255),
    email_confirmed_at TIMESTAMPTZ,
    invited_at TIMESTAMPTZ,
    confirmation_token VARCHAR(255),
    confirmation_sent_at TIMESTAMPTZ,
    recovery_token VARCHAR(255),
    recovery_sent_at TIMESTAMPTZ,
    email_change_token_new VARCHAR(255),
    email_change VARCHAR(255),
    email_change_sent_at TIMESTAMPTZ,
    last_sign_in_at TIMESTAMPTZ,
    raw_app_meta_data JSONB,
    raw_user_meta_data JSONB,
    is_super_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    phone VARCHAR(15),
    phone_confirmed_at TIMESTAMPTZ,
    phone_change VARCHAR(15),
    phone_change_token VARCHAR(255),
    phone_change_sent_at TIMESTAMPTZ,
    confirmed_at TIMESTAMPTZ DEFAULT NOW(),
    email_change_token_current VARCHAR(255),
    email_change_confirm_status SMALLINT DEFAULT 0,
    banned_until TIMESTAMPTZ,
    reauthentication_token VARCHAR(255),
    reauthentication_sent_at TIMESTAMPTZ,
    is_sso_user BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMPTZ
);

-- Add trigger for updated_at
CREATE TRIGGER set_timestamp_users
BEFORE UPDATE ON public.users
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);
CREATE INDEX IF NOT EXISTS idx_users_phone ON public.users(phone);

-- Drop the existing foreign key constraint on restaurant_staff
ALTER TABLE restaurant_staff DROP CONSTRAINT IF EXISTS restaurant_staff_user_id_fkey;

-- Add a new constraint that references either auth.users or public.users
-- For now, we'll make it reference public.users for development mode
ALTER TABLE restaurant_staff 
ADD CONSTRAINT restaurant_staff_user_id_fkey 
FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;

-- Create a function to handle user creation for development mode
CREATE OR REPLACE FUNCTION create_dev_user(
    p_id UUID,
    p_email VARCHAR(255),
    p_name VARCHAR(255) DEFAULT NULL,
    p_restaurant_id UUID DEFAULT NULL,
    p_role VARCHAR(50) DEFAULT 'owner'
) RETURNS UUID AS $$
DECLARE
    user_id UUID;
BEGIN
    -- Insert user into public.users table
    INSERT INTO public.users (
        id,
        email,
        raw_user_meta_data,
        confirmed_at,
        email_confirmed_at
    ) VALUES (
        p_id,
        p_email,
        jsonb_build_object(
            'name', COALESCE(p_name, 'Development User'),
            'restaurant_id', p_restaurant_id,
            'role', p_role
        ),
        NOW(),
        NOW()
    ) ON CONFLICT (id) DO UPDATE SET
        email = EXCLUDED.email,
        raw_user_meta_data = EXCLUDED.raw_user_meta_data,
        updated_at = NOW()
    RETURNING id INTO user_id;
    
    RETURN user_id;
END;
$$ LANGUAGE plpgsql;

COMMIT;
