# Google Sheets Storage Adapter

This reference defines bookkeeping-level expectations for using Google Sheets as a storage adapter. It deliberately does not duplicate Google Drive or Google Sheets tool mechanics.

## Responsibility Boundary

Receipt Bookkeeper owns:

- purchase intent and side-effect safety
- receipt understanding
- canonical `Transaction` and `Item` records
- normalization
- discount semantics
- validation status
- duplicate criteria
- transaction ID requirements
- verification expectations
- concise user reporting

The installed Google Drive / Google Sheets capability owns:

- Drive file discovery
- spreadsheet grounding
- spreadsheet metadata
- tab, sheet ID, table, header, range, and formula discovery
- row and cell reads/writes
- batch updates
- native Google Sheets behavior
- preserving spreadsheet structure, formatting, formulas, validation, and relationships
- Google-specific verification mechanics

In Codex environments where the `google-drive` and `google-sheets` skills are installed, load and follow them for all Google file and spreadsheet operations. If another harness exposes equivalent Google Drive or Sheets connectors, use their native conventions while preserving the same adapter boundary.

## Existing Bookkeeping Spreadsheet

For an existing Google Sheets bookkeeping destination, the desired high-level operation is:

1. Ground the exact target spreadsheet. Use Drive discovery if the user gave a name, folder, or ambiguous reference instead of a URL or ID.
2. Read spreadsheet metadata through the Sheets capability.
3. Identify the relevant transaction and item sheets, tabs, tables, or ranges.
4. Inspect existing headers and structure before deciding how to map fields.
5. Map canonical transaction and item fields onto the existing structure.
6. Search existing records for duplicate candidates using merchant, date, total, time, item count, source/order number, and matching line items when available.
7. Preserve existing ID conventions, categories, formulas, formatting, validation, protected ranges, and relationships.
8. Write the transaction record and associated item records using the Sheets capability's safe edit workflow.
9. Read back the affected records when supported.
10. Verify stored values against the canonical transaction and item records.

Do not guess spreadsheet IDs, tab names, sheet IDs, ranges, column positions, or headers. Do not redesign the sheet merely because its structure differs from the canonical model.

## New Bookkeeping Spreadsheet

Do not create a new bookkeeping spreadsheet unless the user explicitly asks to create one or has already configured a workflow that authorizes creation.

When creation is authorized, use the installed Google Sheets creation workflow. In the current Codex Google Sheets convention, that may involve composing with a spreadsheet-generation capability and importing a local workbook as a native Google Sheet. Follow the installed Google Sheets skill rather than restating those steps here.

For a new bookkeeping system, prefer two logical tables:

Transactions:

- `transaction_id`
- `date`
- `time`
- `merchant`
- `currency`
- `subtotal`
- `discount`
- `tax`
- `total`
- `payment_method`
- `location`
- `validation_status`
- `source`
- `notes`
- `details_json`

Items:

- `transaction_id`
- `item_name`
- `quantity`
- `unit_price`
- `original_price`
- `discount`
- `final_price`
- `category`

The actual Google Sheet implementation, formatting, formulas, native tables, validation, protected ranges, and import mechanics belong to the installed Google Sheets capability.

For new Google Sheets bookkeeping systems, place `details_json` immediately after `notes` in the `Transactions` table. Generate it from the canonical `Items` records plus transaction-level charges, discounts, service charges, delivery fees, and tax/VAT breakdowns. Keep the `Items` table as the authoritative normalized item detail; `details_json` is a compact denormalized transaction-row view.

For existing spreadsheets, add or populate `details_json` only when the column already exists, the user asks for this detail, or a minimal compatible addition is clearly within the requested bookkeeping operation. Preserve the user's existing schema when they did not ask for a new detail field.

## Field Mapping Guidance

Adapt to the existing spreadsheet's columns and terminology. Examples:

- `date` or `transaction_date` can map to canonical `transaction_date`.
- `amount`, `total`, `paid`, or `gross` may map to canonical `total` only after confirming meaning.
- `discount`, `coupon`, or `savings` may be item-level, transaction-level, or informational. Inspect surrounding columns and formulas before mapping.
- `category` should use the user's existing categories when they are clear; leave blank or null rather than inventing a category.

If the destination lacks item-level storage but the user still wants bookkeeping recorded, store the transaction according to the existing structure and report that item detail was not stored unless an appropriate notes field can preserve concise item detail.

If the destination supports `details_json`, the field should contain valid compact JSON. Prefer a shape with `items`, `charges`, `discounts`, and `tax` keys. Verify that the JSON parses and agrees with the stored item rows and transaction totals.

## Verification

After writing, use the Sheets capability to read back the affected rows or ranges when supported. Verify:

- transaction row exists once
- transaction ID matches
- date, merchant, currency, total, and validation status match
- expected item rows exist or item detail is represented according to the destination's structure
- item rows link to the transaction ID
- `details_json` exists and is parseable when the destination includes that column
- no accidental duplicate was created

Report routine success only after verification succeeds or after clearly explaining why read-back was unavailable.
