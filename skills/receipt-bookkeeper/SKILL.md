---
name: receipt-bookkeeper
description: Extract, validate, deduplicate, and record receipts or purchase evidence into a configured bookkeeping destination. Use when the user intends to log or bookkeep a purchase, not for read-only receipt summaries.
---

# Receipt Bookkeeper

Use this skill when the user provides or references purchase evidence and indicates they want it recorded, logged, tracked, saved, expensed, or bookkept. Purchase evidence can include photographed paper receipts, scans, screenshots, PDF receipts, invoices, digital receipts, order confirmations, and similar artifacts. Semantic intent matters; examples include "log this purchase", "add this to my expenses", "help me record this receipt", "幫我記數", and "記低呢張單".

Do not mutate a bookkeeping destination merely because a receipt is attached. If the user asks what a receipt says, to translate it, or to summarize it, handle that as read-only receipt understanding unless they also authorize recording. Writing to storage is a side effect.

## Workflow

1. Understand the source using the native multimodal, document, or vision capabilities available in the current harness. Do not default to traditional OCR just because text is present. If important image details are hard to read and closer inspection tools are available, inspect the source more closely before treating the data as unavailable.
2. Convert the purchase into the storage-independent canonical `Transaction` and `Item` model before calling any storage adapter. For field definitions, normalization, and example shapes, read [references/schema.md](references/schema.md).
3. Normalize merchant, date, time, currency, quantities, money, discounts, and useful original receipt text. Preserve original text when normalization could hide uncertainty. Do not aggressively expand abbreviated item names unless the identity is clear.
4. Validate the transaction deterministically. Reconcile item totals, taxes, fees, discounts, and receipt total when enough evidence exists. For reconciliation, discount handling, duplicate detection, transaction IDs, and uncertainty policy, read [references/validation.md](references/validation.md).
5. If material information is missing or conflicting, investigate available evidence first. Ask the user only when the uncertainty would make the bookkeeping record unreliable or could create a meaningful bookkeeping error.
6. Before writing, check the configured destination for likely duplicates when the storage capability can read or search existing records. Do not create a duplicate when the purchase is clearly already recorded. Ask before creating a materially ambiguous duplicate.
7. Hand the canonical records to the configured storage adapter. The core skill owns bookkeeping semantics; the adapter and existing tool skills own storage mechanics.
8. Verify after writing when read-back capability exists. A successful write call alone is not enough. Confirm the transaction exists, the `transaction_id` and total are correct, expected item records exist, item records link to the transaction, and no accidental duplicate was created.
9. Report concisely. For routine success, mention merchant, date, total, item count, and meaningful savings if useful. Mention unresolved uncertainty briefly. Do not expose the full internal schema unless the user asks.

## Storage Adapters

Prefer the user's configured bookkeeping destination. The core model must remain portable across storage systems and agent harnesses.

When Google Sheets is the configured or requested destination and Google Drive / Google Sheets capability is available, read [references/google-sheets.md](references/google-sheets.md). Compose with the installed Google Drive and Google Sheets skills, plugins, connectors, or MCP tools for file discovery, spreadsheet metadata, range operations, row writes, and native spreadsheet behavior. Do not duplicate their tool-specific instructions here.

When Supabase is the configured or requested destination, or when the user mentions Project Cogito receipt bookkeeping, read [references/supabase.md](references/supabase.md). Compose with the installed Supabase skill, plugin, connector, or native database capability for project discovery, SQL execution, migrations, advisors, and current Supabase security conventions. Do not duplicate Supabase tool mechanics in this skill.

For other destinations, apply the same adapter boundary: discover or ground the target, map the canonical model to the destination's existing structure, search for duplicates, write transaction and item records, read back, and verify.

## Side-Effect Safety

- Recording requires user intent to bookkeep the purchase or an already configured workflow that authorizes recording.
- Creating a new bookkeeping system requires explicit user intent. Do not create a new spreadsheet or database just because no destination was found.
- Preserve existing destination structure, formulas, formatting, validation, relationships, and ID conventions unless the user explicitly asks to change them or the current bookkeeping operation requires a minimal compatible addition.
- Never fabricate unreadable or missing data. Use `partial` or `needs_review` validation status when uncertainty remains.
