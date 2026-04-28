-- Migration: Create business-verification storage bucket with secure RLS policies
-- Date: 2025-10-07

-- 1) Create bucket if not exists
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('business-verification', 'business-verification', false, 10485760, array['application/pdf','image/jpeg','image/png','image/webp'])
on conflict (id) do nothing;

-- 2) Policies on storage.objects for the new bucket
-- Enable RLS on storage.objects (usually enabled by default)
alter table storage.objects enable row level security;

-- Drop existing policies if re-running (idempotent)
drop policy if exists "business_verification_insert" on storage.objects;
drop policy if exists "business_verification_select" on storage.objects;
drop policy if exists "business_verification_update" on storage.objects;
drop policy if exists "business_verification_delete" on storage.objects;

-- Allow authenticated users to upload to their own bucket objects; owner is set automatically
create policy "business_verification_insert"
  on storage.objects for insert
  to authenticated
  with check (
    bucket_id = 'business-verification'
    and owner = auth.uid()
  );

-- Allow owners to read their own verification documents
create policy "business_verification_select"
  on storage.objects for select
  to authenticated
  using (
    bucket_id = 'business-verification'
    and owner = auth.uid()
  );

-- Allow owners to update their own verification documents
create policy "business_verification_update"
  on storage.objects for update
  to authenticated
  using (
    bucket_id = 'business-verification' and owner = auth.uid()
  )
  with check (
    bucket_id = 'business-verification' and owner = auth.uid()
  );

-- Allow owners to delete their own verification documents
create policy "business_verification_delete"
  on storage.objects for delete
  to authenticated
  using (
    bucket_id = 'business-verification' and owner = auth.uid()
  );

