insert into public.restaurants (name, owner_user_id)
values ('Demo Resto', '00000000-0000-0000-0000-000000000000')
on conflict do nothing;

insert into public.menu_items (restaurant_id, name, price_cents)
select r.id, 'Margherita Pizza', 499 from public.restaurants r limit 1;
