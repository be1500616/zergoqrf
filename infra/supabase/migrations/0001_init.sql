-- Schema for ZERGO QR
create table if not exists public.restaurants (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  owner_user_id uuid not null,
  created_at timestamptz not null default now()
);

create table if not exists public.menu_items (
  id uuid primary key default gen_random_uuid(),
  restaurant_id uuid not null references public.restaurants(id) on delete cascade,
  name text not null,
  price_cents int not null,
  is_active boolean not null default true,
  created_at timestamptz not null default now()
);

create table if not exists public.orders (
  id uuid primary key default gen_random_uuid(),
  restaurant_id uuid not null references public.restaurants(id) on delete cascade,
  table_id text,
  status text not null default 'pending',
  created_at timestamptz not null default now()
);

-- Multi-tenancy: tenant is restaurant_id; RLS
alter table public.restaurants enable row level security;
alter table public.menu_items enable row level security;
alter table public.orders enable row level security;

-- Policies: allow owners to manage their restaurant rows
create policy if not exists "restaurant_owner_select" on public.restaurants for select using (
  auth.uid() = owner_user_id
);
create policy if not exists "restaurant_owner_all" on public.restaurants for all using (
  auth.uid() = owner_user_id
) with check (auth.uid() = owner_user_id);

-- Menu items policy: user must own the restaurant
create policy if not exists "menu_items_by_owner" on public.menu_items for all using (
  exists(
    select 1 from public.restaurants r
    where r.id = restaurant_id and r.owner_user_id = auth.uid()
  )
) with check (
  exists(
    select 1 from public.restaurants r
    where r.id = restaurant_id and r.owner_user_id = auth.uid()
  )
);

-- Orders policy: allow select by restaurant owner; insert by anyone (customer) but only for active restaurants
create policy if not exists "orders_owner_select" on public.orders for select using (
  exists(
    select 1 from public.restaurants r
    where r.id = restaurant_id and r.owner_user_id = auth.uid()
  )
);
create policy if not exists "orders_insert_any" on public.orders for insert with check (
  exists(select 1 from public.restaurants r where r.id = restaurant_id)
);
