# Supabase Storage Adapter

Use this reference when Supabase is the configured or requested bookkeeping destination, or when the user refers to Project Cogito receipt bookkeeping.

## Responsibility Boundary

Receipt Bookkeeper owns the bookkeeping domain model:

- canonical `Transaction` and `Item` extraction
- normalization and uncertainty policy
- discount, tax, fee, and service-charge semantics
- deterministic validation and duplicate detection
- concise user reporting

The installed Supabase capability owns Supabase mechanics:

- current Supabase documentation and changelog checks
- project discovery and grounding
- SQL execution, migrations, branches, and advisors
- grants, RLS policies, Data API exposure, and connector-specific behavior

Always load and follow the Supabase skill or connector instructions when performing Supabase work. Do not expose tables to `anon` or `authenticated`, alter Data API settings, create allow policies, upload receipt files, or create Edge Functions unless the user explicitly asks and the access model is clear.

## Project Cogito Convention

For Joseph's Project Cogito receipt workflow, the intended Supabase storage area is a private schema:

- project name: `Project Cogito`
- project reference: discover it through the user's connected Supabase account; never hard-code it in the portable skill
- schema: `receipt_bookkeeping`

Verify the project by name before writing. Treat the ref as a helpful hint, not the sole source of truth.

Supabase projects contain one Postgres database. A dedicated schema is the preferred boundary for this workflow because it keeps receipt bookkeeping separate now and still allows future joins to a broader personal database later.

## Current Schema Shape

The v1 schema uses these tables:

- `receipt_bookkeeping.transactions`: canonical transaction header, including `transaction_id`, merchant/date/time/currency, subtotal, discount, tax, service charge, total, validation status, notes, duplicate metadata, `source`, and `details_json` as `jsonb`.
- `receipt_bookkeeping.items`: authoritative line-item rows linked to `transactions.id`; includes line number, item name, quantity, unit price, original price, discount, final price, category, and raw text.
- `receipt_bookkeeping.adjustments`: service charges, tips, delivery/shipping fees, taxes/VAT, transaction-level discounts, deposits, rounding, and other non-item amounts. Store discount amounts as positive values and let `adjustment_type` define semantics.
- `receipt_bookkeeping.sources`: evidence and extraction provenance such as receipt image filename, Drive file id, content hash when available, raw text summary, extractor, and metadata.
- `receipt_bookkeeping.storage_syncs`: links from the canonical SQL transaction to adapter destinations such as Google Sheets or Google Drive rows/files.

Use `transactions.transaction_id` for the canonical human-readable bookkeeping ID shared with spreadsheets when possible. Use the internal UUID primary keys for SQL relationships.

`details_json` is a convenience JSONB view, not the source of truth. Generate it from canonical items, adjustments, discounts, and tax details. Keep item rows and adjustment rows authoritative.

## Security Posture

The Project Cogito receipt schema is private by default:

- RLS is enabled on receipt tables.
- `anon` and `authenticated` have explicit deny-all policies until a personal auth/ownership model exists.
- Server-side/service-role workflows may write through trusted tools.
- Do not grant client access or create permissive RLS policies merely to make an insert easier.

If the user later wants a browser or mobile app to access this data directly, first design ownership fields and RLS policies around the real personal database model. Do not default to `TO authenticated` without a row ownership predicate.

## Write Workflow

1. Ground the Supabase project by name or explicit project ref.
2. Confirm the `receipt_bookkeeping` schema and expected tables exist before writing. If they do not, discuss whether to create them.
3. Build the storage-independent canonical transaction and items first.
4. Validate arithmetic before writing:
   - sum `items.final_price`
   - add service charges, fees, tips, delivery, or other total-affecting adjustments
   - subtract transaction-level discounts
   - do not add tax again when the receipt shows tax as already included
   - compare against `transactions.total`
5. Search for duplicates before inserting. Prefer `transaction_id` and exact source hashes when available; also search merchant-normalized/date/time/currency/total and item count.
6. Insert the transaction, items, adjustments, source provenance, and sync links together when possible so partial writes are less likely.
7. Verify by reading back:
   - one transaction row
   - matching `transaction_id`, date, merchant, currency, total, and validation status
   - expected item count and item sum
   - expected service/tax/discount adjustments
   - sync links when writing alongside Google Sheets
8. Report merchant, date, total, item count, and any unresolved uncertainty. Mention Supabase and Sheets separately when both were updated.

## Google Sheets Sync

When both Supabase and Google Sheets are in the workflow, use Supabase as the durable canonical store and Google Sheets as a human-facing mirror or export unless the user says otherwise.

Record sheet linkage in `receipt_bookkeeping.storage_syncs` rather than embedding spreadsheet details into core transaction semantics. It is fine for `transactions.source` or `metadata` to include a concise adapter hint, but do not make Google Sheets fields required for SQL bookkeeping.

If Google Sheets contains a `details_json` column, keep it semantically aligned with Supabase `transactions.details_json`.
