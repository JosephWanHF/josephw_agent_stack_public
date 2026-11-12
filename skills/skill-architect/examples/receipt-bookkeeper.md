# Receipt Bookkeeper Example

Use this example only as a pattern for architecture quality and composition. It should not bias unrelated skills toward receipts, spreadsheets, or bookkeeping.

## Rough User Idea

```text
I want a skill where I upload receipt photos and it puts everything into my Google Sheet.
```

## Architecture Reasoning

The user outcome is automatic receipt bookkeeping, not "write arbitrary extracted text into a spreadsheet."

The likely domain skill is `receipt-bookkeeper`. It should own bookkeeping semantics:

- Interpret receipt images or PDFs.
- Extract merchant, date, currency, line items, discounts, tax, tip, payment hints, and total.
- Normalize a canonical transaction record.
- Reconcile arithmetic where possible.
- Detect likely duplicates.
- Decide what uncertainty is minor versus material.
- Verify the bookkeeping outcome and report what was recorded.

The spreadsheet capability should own spreadsheet mechanics:

- Discover or open the target spreadsheet.
- Preserve existing schema where possible.
- Append or update rows.
- Read back changed ranges for verification.

## Composition

```text
user
-> receipt-bookkeeper
-> storage adapter
-> existing spreadsheet capability
-> Google Sheets or another ledger
```

This avoids copying a full Google Sheets implementation into the receipt skill.

## Brief Excerpt

### Activation Intent

Applies when the user wants to record, log, categorize, reconcile, or persist receipt or expense information from an uploaded artifact or supplied receipt details.

### Non-Activation Cases

Does not automatically record expenses when the user only asks what a receipt says, requests OCR, asks for translation, or wants to compare prices without bookkeeping.

### Side Effects

Reading and extracting receipt information is safe analysis. Writing to a ledger, spreadsheet, accounting system, or database is a state-changing action and should occur only when the user's request implies recording or after explicit confirmation in ambiguous cases.

### Deterministic Operations

Use deterministic checks for arithmetic reconciliation, required-field validation, duplicate keys, date normalization, currency normalization, and idempotency checks.

### Validation Strategy

After recording, read back the changed ledger row or record when possible. Confirm that required fields are present, totals reconcile or uncertainty is preserved, and likely duplicates were handled according to the duplicate strategy.

## Downstream Prompt Shape

```text
Create a skill called receipt-bookkeeper. Its purpose is automatic receipt bookkeeping from uploaded receipt images, PDFs, or text. It owns receipt and expense semantics, extraction, normalization, arithmetic reconciliation, duplicate detection, uncertainty handling, and verification. It composes with the available spreadsheet, database, or bookkeeping capability for persistence rather than implementing every storage API itself. Use your native skill-authoring conventions as authoritative for exact packaging and metadata.
```
