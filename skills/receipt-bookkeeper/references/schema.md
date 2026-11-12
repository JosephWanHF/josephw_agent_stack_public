# Canonical Schema

The core receipt-bookkeeper domain model is storage-independent. Always create canonical `Transaction` and `Item` records before adapting them to Google Sheets, another spreadsheet, a database, or any other bookkeeping destination.

## Canonical Payload

A complete bookkeeping candidate can be represented as:

```json
{
  "transaction": {},
  "items": [],
  "validation": {},
  "duplicate_check": {},
  "storage": {}
}
```

`transaction` and `items` are the canonical bookkeeping records. `validation`, `duplicate_check`, and `storage` are operational metadata used to decide whether and how to write safely.

Storage adapters may add derived convenience fields, but those fields must be generated from the canonical `transaction` and `items` rather than replacing them. For example, a spreadsheet adapter can add a `details_json` transaction column that denormalizes item and adjustment detail for quick inspection while the `Items` records remain the authoritative item-level detail.

## Transaction

Required fields:

| Field | Type | Notes |
| --- | --- | --- |
| `transaction_id` | string | Preserve an existing destination convention. Otherwise generate a stable unique ID after duplicate checks and collision checks. |
| `merchant` | string | Readable merchant name as printed or confidently normalized. |
| `transaction_date` | string | `YYYY-MM-DD`. Use the purchase date, not upload date. |
| `currency` | string | ISO-style code such as `GBP`, `EUR`, or `USD`. |
| `total` | number | Decimal numeric value without currency symbols. This is the amount charged or payable for the transaction. |
| `validation_status` | string | One of `validated`, `partial`, or `needs_review`. |

Optional fields:

| Field | Type | Notes |
| --- | --- | --- |
| `transaction_time` | string or null | `HH:MM` when available. Preserve uncertainty in notes rather than guessing. |
| `subtotal` | number or null | Receipt subtotal before transaction-level discounts, tax, fees, or final total when clearly labeled. |
| `discount_total` | number or null | Positive transaction-level or unallocated discount amount. Do not subtract item-level discounts a second time during reconciliation. |
| `tax` | number or null | Explicit tax amount when available. Use null for tax-inclusive receipts without a separate tax amount. |
| `payment_method` | string or null | Card type, cash, wallet, account, or masked card detail when shown. |
| `location` | string or null | Store location, address, branch, website, or marketplace when useful. |
| `source` | object or string or null | Receipt evidence descriptor such as file name, document page, email/order ID, image region, or source URL when available. |
| `notes` | string or null | Concise facts needed to preserve uncertainty, original text, unallocated discounts, or receipt-specific adjustments. |

Do not use `notes` as a dumping ground for the whole receipt. Keep it short and decision-relevant.

## Item

Use item records when identifiable purchased items exist. A receipt or payment confirmation may sometimes only support a transaction-level record; in that case `items` can be empty and the validation status should reflect the missing line-item evidence.

Required where an identifiable item exists:

| Field | Type | Notes |
| --- | --- | --- |
| `transaction_id` | string | Must match the parent transaction. |
| `item_name` | string | Preserve useful original receipt wording. Normalize only when identity is clear. |
| `quantity` | number | Use the explicit quantity. If a normal receipt line implies one item and no quantity marker exists, use `1`. |
| `final_price` | number | Extended line amount after item-level discounts. This is the amount contributing to item-sum reconciliation. |

Optional fields:

| Field | Type | Notes |
| --- | --- | --- |
| `unit_price` | number or null | Price per unit before multiplication when visible. |
| `original_price` | number or null | Pre-discount item price when visible. |
| `discount` | number or null | Positive item-level discount amount only when confidently associated with this item. |
| `category` | string or null | Use existing user or destination categories when clear. Do not stop the workflow for category uncertainty. |

## Derived Detail JSON

When a storage destination benefits from a transaction-row detail field, derive it after canonical extraction and validation.

Recommended field name:

- `details_json`

Recommended JSON object shape:

```json
{
  "items": [
    {
      "name": "Item name",
      "quantity": 1,
      "unit_price": 1.23,
      "final_price": 1.23,
      "discount": 0.25
    }
  ],
  "charges": [
    {
      "name": "Service charge",
      "amount": 2.50
    }
  ],
  "discounts": [
    {
      "name": "Coupon",
      "amount": 1.00,
      "allocation": "transaction"
    }
  ],
  "tax": {
    "rate": 0.20,
    "net": 10.00,
    "amount": 2.00
  }
}
```

Rules:

- Keep `details_json` valid JSON, preferably compact single-line JSON for spreadsheet cells.
- In SQL databases that support native JSON types, store `details_json` as JSON or JSONB rather than a string while preserving the same object shape.
- Include item names, quantities, unit prices when available, final prices, and item-level discounts when known.
- Include transaction-level charges, discounts, service charges, delivery charges, fees, and tax breakdowns when available.
- Omit keys or use `null` where evidence is unavailable; do not invent missing detail.
- Do not use `details_json` as the canonical source of truth. It is a derived view for human inspection and downstream convenience.

## Normalization

- Dates: normalize to `YYYY-MM-DD`.
- Times: normalize to 24-hour `HH:MM` when available.
- Currency: use ISO-style currency codes. Infer from locale, symbol, merchant, or document context only when evidence is strong.
- Money: store decimal numeric values without currency symbols. Keep exact arithmetic internally using decimal or integer minor units when the harness supports it.
- Quantities: store numeric values. Weighted items can use decimal quantities and note the unit if the destination has a place for it.
- Merchant: use a readable merchant name. Remove obvious company suffix noise only when it does not change identity.
- Discounts: store discounts as positive reductions. Never use a negative discount unless the destination's existing schema explicitly requires it.

Preserve original receipt text in the source descriptor, notes, or storage-specific evidence field when normalization could lose important meaning.

## Validation Status

- `validated`: required transaction fields are present, duplicate risk is resolved, and deterministic checks reconcile within an appropriate tolerance when enough evidence exists.
- `partial`: the transaction is reliable enough to record, but non-critical fields or line-item detail are incomplete, or arithmetic cannot be fully tested from the available evidence.
- `needs_review`: required fields are missing or conflicting, arithmetic remains materially unreconciled, the source is too incomplete, or duplicate risk is unresolved.

## Transaction IDs

Preserve the destination's existing transaction ID convention whenever one exists. Otherwise generate a stable unique identifier after reading enough existing records to avoid collision.

A human-readable pattern such as `TX-YYYYMMDD-NNN` is acceptable when the destination supports date-based sequencing. If sequence state is unavailable, use a deterministic suffix from normalized merchant, date, total, and source evidence. Always check the candidate ID against existing records before writing.
