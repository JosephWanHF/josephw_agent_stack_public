# Cogito Diet Inventory Schema

This contract defines the Supabase table used by `fridge-capture`, plus the related recipe and meal tables used by `diet-recipe-planner`. Inspect existing data before changing anything. Do not drop, rename, or rewrite existing user data as part of ordinary capture.

## Supabase Tables

Default schema: `public`, following Joseph's existing Cogito tables. Because Postgres supports `schema.table` rather than nested `joseph_cogito > diet_meta > table` paths, diet tables use the `diet_meta_` prefix and every row is scoped to `public.joseph_cogito.id`.

If these tables are in an exposed Supabase schema, enable RLS and do not grant `anon` or `authenticated` access by default. Let future applications add narrowly scoped policies when their access model is known.

Use the current Supabase skill and tool guidance for the exact migration mechanism. The SQL below is the intended table contract, not permission to skip project inspection or verification.

```sql
create extension if not exists pgcrypto;

create table if not exists public.diet_meta_food_item_record (
  id uuid primary key default gen_random_uuid(),
  joseph_cogito_id uuid not null references public.joseph_cogito(id) on delete cascade,
  capture_batch_key text,
  idempotency_key text,
  source text not null default 'fridge_photo'
    check (source in ('fridge_photo', 'manual', 'receipt', 'import', 'correction')),
  source_label text,
  photo_reference text,
  photo_hash text,
  observed_at timestamptz not null default now(),
  observed_on date not null default current_date,
  item_name text not null check (btrim(item_name) <> ''),
  normalized_name text generated always as (lower(btrim(item_name))) stored,
  category text,
  quantity_value numeric(10,2) check (quantity_value is null or quantity_value >= 0),
  quantity_unit text,
  quantity_text text,
  storage_location text not null default 'fridge'
    check (storage_location in ('fridge', 'freezer', 'pantry', 'counter', 'unknown')),
  freshness_status text not null default 'unknown'
    check (freshness_status in ('unknown', 'fresh', 'use_soon', 'expired', 'discarded')),
  expiration_date date,
  status text not null default 'available'
    check (status in ('available', 'used', 'discarded', 'expired', 'unknown')),
  confidence numeric(3,2) check (confidence is null or (confidence >= 0 and confidence <= 1)),
  detection_payload jsonb not null default '{}'::jsonb,
  notes text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (joseph_cogito_id, idempotency_key)
);

create table if not exists public.diet_meta_recipes_record (
  id uuid primary key default gen_random_uuid(),
  joseph_cogito_id uuid not null references public.joseph_cogito(id) on delete cascade,
  idempotency_key text,
  recipe_name text not null check (btrim(recipe_name) <> ''),
  recipe_slug text,
  source text not null default 'agent'
    check (source in ('agent', 'user', 'web', 'import')),
  recipe_status text not null default 'suggested'
    check (recipe_status in ('suggested', 'accepted', 'rejected', 'cooked', 'archived')),
  suggested_at timestamptz not null default now(),
  decided_at timestamptz,
  cooked_at timestamptz,
  meal_type text check (meal_type is null or meal_type in ('breakfast', 'lunch', 'dinner', 'snack', 'dessert', 'other')),
  cuisine text,
  servings numeric(5,2) check (servings is null or servings > 0),
  prep_minutes integer check (prep_minutes is null or prep_minutes >= 0),
  cook_minutes integer check (cook_minutes is null or cook_minutes >= 0),
  ingredients jsonb not null default '[]'::jsonb
    check (jsonb_typeof(ingredients) = 'array'),
  steps jsonb not null default '[]'::jsonb
    check (jsonb_typeof(steps) = 'array'),
  matching_food_item_ids uuid[] not null default '{}'::uuid[],
  missing_ingredients jsonb not null default '[]'::jsonb
    check (jsonb_typeof(missing_ingredients) = 'array'),
  shopping_list jsonb not null default '[]'::jsonb
    check (jsonb_typeof(shopping_list) = 'array'),
  match_score numeric(3,2) check (match_score is null or (match_score >= 0 and match_score <= 1)),
  rationale text,
  source_url text,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (joseph_cogito_id, idempotency_key)
);

create table if not exists public.diet_meta_diet_record (
  id uuid primary key default gen_random_uuid(),
  joseph_cogito_id uuid not null references public.joseph_cogito(id) on delete cascade,
  recipe_record_id uuid references public.diet_meta_recipes_record(id) on delete set null,
  idempotency_key text,
  meal_name text not null check (btrim(meal_name) <> ''),
  meal_date date not null default current_date,
  cooked_at timestamptz not null default now(),
  meal_type text check (meal_type is null or meal_type in ('breakfast', 'lunch', 'dinner', 'snack', 'dessert', 'other')),
  servings numeric(5,2) check (servings is null or servings > 0),
  used_food_item_ids uuid[] not null default '{}'::uuid[],
  ingredients_used jsonb not null default '[]'::jsonb
    check (jsonb_typeof(ingredients_used) = 'array'),
  outcome_status text not null default 'cooked'
    check (outcome_status in ('planned', 'cooked', 'logged', 'skipped')),
  rating integer check (rating is null or (rating >= 1 and rating <= 5)),
  notes text,
  leftovers jsonb not null default '{}'::jsonb
    check (jsonb_typeof(leftovers) = 'object'),
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (joseph_cogito_id, idempotency_key)
);

create unique index if not exists idx_diet_meta_food_item_batch_name
  on public.diet_meta_food_item_record (joseph_cogito_id, capture_batch_key, normalized_name)
  where capture_batch_key is not null;

create index if not exists idx_diet_meta_food_item_current
  on public.diet_meta_food_item_record (joseph_cogito_id, status, storage_location, normalized_name);

create index if not exists idx_diet_meta_food_item_observed
  on public.diet_meta_food_item_record (joseph_cogito_id, observed_at desc);

create index if not exists idx_diet_meta_recipes_status
  on public.diet_meta_recipes_record (joseph_cogito_id, recipe_status, suggested_at desc);

create index if not exists idx_diet_meta_recipes_slug
  on public.diet_meta_recipes_record (joseph_cogito_id, recipe_slug);

create index if not exists idx_diet_meta_diet_meal_date
  on public.diet_meta_diet_record (joseph_cogito_id, meal_date desc, cooked_at desc);

create index if not exists idx_diet_meta_diet_recipe_record
  on public.diet_meta_diet_record (recipe_record_id);

alter table public.diet_meta_food_item_record enable row level security;
alter table public.diet_meta_recipes_record enable row level security;
alter table public.diet_meta_diet_record enable row level security;

revoke all on table public.diet_meta_food_item_record from anon, authenticated;
revoke all on table public.diet_meta_recipes_record from anon, authenticated;
revoke all on table public.diet_meta_diet_record from anon, authenticated;

grant all on table public.diet_meta_food_item_record to service_role;
grant all on table public.diet_meta_recipes_record to service_role;
grant all on table public.diet_meta_diet_record to service_role;

insert into public.joseph_cogito (profile_key, display_name)
values ('joseph', 'Joseph')
on conflict (profile_key) do update
set display_name = excluded.display_name,
    updated_at = now();
```

## Current Inventory Query

Use this pattern to read currently available food:

```sql
select *
from public.diet_meta_food_item_record
where joseph_cogito_id = (
  select id from public.joseph_cogito where profile_key = 'joseph'
)
and status = 'available'
order by observed_at desc, normalized_name;
```

Current inventory is a status view over dated records, not a destructive rewrite of history.
