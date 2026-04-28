-- Add missing restaurant profile fields
-- This migration adds the missing columns that the backend expects

BEGIN;

-- Add missing columns to restaurants table
ALTER TABLE public.restaurants
  ADD COLUMN IF NOT EXISTS description TEXT,
  ADD COLUMN IF NOT EXISTS address TEXT,
  ADD COLUMN IF NOT EXISTS phone TEXT,
  ADD COLUMN IF NOT EXISTS email VARCHAR(255),
  ADD COLUMN IF NOT EXISTS website TEXT,
  ADD COLUMN IF NOT EXISTS cuisine_type VARCHAR(100),
  ADD COLUMN IF NOT EXISTS dining_style VARCHAR(50),
  ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT TRUE;

-- Set proper defaults for JSONB columns
ALTER TABLE public.restaurants
  ALTER COLUMN business_hours SET DEFAULT '{}'::jsonb,
  ALTER COLUMN settings SET DEFAULT '{}'::jsonb;

-- Update existing NULL values to empty JSON objects
UPDATE public.restaurants 
SET business_hours = '{}'::jsonb 
WHERE business_hours IS NULL;

UPDATE public.restaurants 
SET settings = '{}'::jsonb 
WHERE settings IS NULL;

-- Add indexes for commonly queried fields
CREATE INDEX IF NOT EXISTS idx_restaurants_email ON public.restaurants(email);
CREATE INDEX IF NOT EXISTS idx_restaurants_phone ON public.restaurants(phone);
CREATE INDEX IF NOT EXISTS idx_restaurants_is_active ON public.restaurants(is_active);
CREATE INDEX IF NOT EXISTS idx_restaurants_cuisine_type ON public.restaurants(cuisine_type);

COMMIT;
