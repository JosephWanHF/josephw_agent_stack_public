# Cogito Link Storage Schema

This contract defines the expected Supabase tables and the `Saved Links` Google Sheet shape. Inspect existing data before changing anything. Do not drop, rename, or rewrite existing user data as part of ordinary ingestion.

## Supabase Tables

Default schema: `public`, unless Joseph has configured a private schema for Cogito. If these tables are in an exposed Supabase schema, enable RLS and do not grant `anon` or `authenticated` access by default. Let future applications add narrowly scoped policies when their access model is known.

Use the current Supabase skill and tool guidance for the exact migration mechanism. The SQL below is the intended table contract, not permission to skip project inspection or confirmation.

```sql
create extension if not exists pgcrypto;

create table if not exists public.joseph_cogito (
  id uuid primary key default gen_random_uuid(),
  profile_key text not null unique,
  display_name text not null,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.cogito_links (
  id uuid primary key default gen_random_uuid(),
  joseph_cogito_id uuid not null references public.joseph_cogito(id) on delete cascade,
  original_url text not null,
  canonical_url text not null,
  url_hash text generated always as (md5(canonical_url)) stored,
  title text,
  description text,
  summary text,
  site_name text,
  author text,
  published_at timestamptz,
  published_raw text,
  retrieved_at timestamptz not null default now(),
  content_type text,
  language text,
  status text not null default 'captured'
    check (status in ('captured', 'updated', 'needs_review', 'failed', 'skipped')),
  metadata jsonb not null default '{}'::jsonb,
  extraction jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (joseph_cogito_id, url_hash)
);

create table if not exists public.cogito_tags (
  id uuid primary key default gen_random_uuid(),
  joseph_cogito_id uuid not null references public.joseph_cogito(id) on delete cascade,
  tag_kind text not null check (tag_kind in ('file', 'ai', 'manual', 'system')),
  name text not null,
  slug text not null,
  description text,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (joseph_cogito_id, tag_kind, slug)
);

create table if not exists public.cogito_link_tags (
  link_id uuid not null references public.cogito_links(id) on delete cascade,
  tag_id uuid not null references public.cogito_tags(id) on delete cascade,
  source text not null check (source in ('user', 'ai', 'manual', 'system')),
  confidence numeric(3,2) check (confidence is null or (confidence >= 0 and confidence <= 1)),
  rationale text,
  created_at timestamptz not null default now(),
  primary key (link_id, tag_id)
);

create table if not exists public.cogito_link_transactions (
  id uuid primary key default gen_random_uuid(),
  joseph_cogito_id uuid not null references public.joseph_cogito(id) on delete cascade,
  link_id uuid references public.cogito_links(id) on delete set null,
  operation text not null check (operation in ('schema_setup', 'ingest', 'update', 'tag', 'sheet_sync', 'error')),
  status text not null check (status in ('started', 'succeeded', 'failed', 'partial', 'skipped')),
  idempotency_key text,
  input_payload jsonb not null default '{}'::jsonb,
  output_payload jsonb not null default '{}'::jsonb,
  error_message text,
  created_by text not null default 'codex',
  started_at timestamptz not null default now(),
  completed_at timestamptz,
  unique (joseph_cogito_id, idempotency_key)
);

create index if not exists idx_cogito_links_profile_retrieved
  on public.cogito_links (joseph_cogito_id, retrieved_at desc);

create index if not exists idx_cogito_links_metadata_gin
  on public.cogito_links using gin (metadata);

create index if not exists idx_cogito_tags_profile_slug
  on public.cogito_tags (joseph_cogito_id, slug);

alter table public.joseph_cogito enable row level security;
alter table public.cogito_links enable row level security;
alter table public.cogito_tags enable row level security;
alter table public.cogito_link_tags enable row level security;
alter table public.cogito_link_transactions enable row level security;

insert into public.joseph_cogito (profile_key, display_name)
values ('joseph', 'Joseph')
on conflict (profile_key) do update
set display_name = excluded.display_name,
    updated_at = now();
```

## Canonical Link Record

Each in-memory record should follow this shape before writes:

```json
{
  "original_url": "https://example.com/?utm_source=x",
  "canonical_url": "https://example.com/",
  "title": "Example title",
  "description": "Optional source description",
  "summary": "Short agent-written summary grounded in the source",
  "site_name": "Example",
  "author": null,
  "published_at": null,
  "published_raw": null,
  "retrieved_at": "ISO-8601 timestamp",
  "content_type": "text/html",
  "language": "en",
  "status": "captured",
  "file_tag": {
    "name": "User supplied file tag",
    "slug": "user-supplied-file-tag"
  },
  "ai_tags": [
    {
      "name": "AI Tag",
      "slug": "ai-tag",
      "confidence": 0.83,
      "rationale": "Short retrieval-oriented reason"
    }
  ],
  "metadata": {},
  "extraction": {
    "key_points": [],
    "entities": []
  }
}
```

## Google Sheet: Saved Links

Expected header row:

| Column | Purpose |
| --- | --- |
| Saved At | Timestamp when the row was written to the sheet |
| File Tag | User-controlled filing tag |
| Tags | Comma-separated AI tags |
| Title | Link title |
| Canonical URL | Deduplicated URL |
| Original URL | User-provided or redirected URL |
| Source | Batch/source context, such as human or agent |
| Author | Verified author if available |
| Published At | Normalized publication timestamp or blank |
| Retrieved At | Fetch timestamp |
| Summary | Short source-grounded summary |
| Content Type | MIME or inferred content type |
| Language | Language code when known |
| Status | captured, updated, needs_review, failed, or skipped |
| Supabase Link ID | UUID from `public.cogito_links.id` |
| Metadata JSON | Compact JSON for useful extra fields |
| Notes | User-supplied notes or review comments |

If the existing sheet has equivalent headers, map to them instead of creating duplicate columns. If required columns are missing, add them to the right edge of the sheet and then write rows.

Use `Supabase Link ID` as the preferred row key. If unavailable, use `Canonical URL`. Do not append a duplicate row when an existing row can be updated safely.
