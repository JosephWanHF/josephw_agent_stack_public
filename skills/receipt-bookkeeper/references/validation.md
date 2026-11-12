# Validation, Discounts, Duplicates, and Uncertainty

Use deterministic checks whenever the source provides enough evidence. Validation protects the bookkeeping record; it must not rewrite evidence to make the transaction fit.

## Arithmetic Reconciliation

Work from normalized numeric values. Use exact decimal arithmetic or integer minor units when possible.

Useful reconciliation checks:

1. Sum item `final_price` values.
2. Add fees or charges shown as line items or transaction-level additions, such as bags, deposits, delivery, service charges, bottle deposits, or shipping.
3. Subtract transaction-level or unallocated discounts that are not already reflected in item `final_price`.
4. Add tax only when prices are tax-exclusive and tax is separately added.
5. Compare the computed amount with receipt `total`.

Use a tolerance appropriate to the currency and source quality. For ordinary two-decimal currencies, a one-cent tolerance is usually appropriate. Allow slightly larger tolerances only when the receipt itself uses rounded line displays, weighted products, foreign-currency conversion, or source readability issues, and explain that uncertainty in validation metadata or notes.

Do not modify extracted numbers solely to force reconciliation. If the total does not reconcile, inspect the source again before downgrading status.

## Reconciliation Checklist

If arithmetic does not reconcile, check:

- missed or duplicated line items
- quantities, weights, and unit-price multiplication
- original price versus final price
- multi-buy promotions
- loyalty/member discounts
- coupons
- transaction-level discounts
- tax-inclusive versus tax-exclusive pricing
- deposits, bag charges, delivery, service, tips, shipping, handling, or other fees
- rounding and displayed precision
- refunds, voids, returns, or negative lines
- receipt sections that are summaries rather than purchased items

Keep unresolved evidence as extracted and set `validation_status` to `partial` or `needs_review` based on materiality.

## Discount Rules

Discounts are positive reductions.

- Associate a discount with a specific item only when the receipt provides enough evidence.
- Use item `discount` for item-level reductions. The item `final_price` should already be net of that item-level discount.
- Use transaction `discount_total` for transaction-level or unallocated discounts that reduce the final transaction total and are not already embedded in item `final_price`.
- If the receipt has an informational "you saved" amount that includes item discounts already represented elsewhere, do not subtract it again.
- Preserve unclear promotions as transaction-level or unallocated discounts rather than guessing item allocation.
- Multi-buy promotions spanning several items can remain unallocated unless the receipt clearly assigns the reduction.

For user reporting, total savings can be derived as item-level discounts plus transaction-level/unallocated discounts when both are reliable.

## Duplicate Detection

Before writing, search or read the configured destination when the adapter supports it.

Strong duplicate signals:

- same or highly similar merchant
- same transaction date
- same total
- same transaction time or close time
- same item count
- matching line items or source/order number

Merchant + date + total is a strong duplicate signal. Merchant + date + total + matching item count is usually enough to treat a record as the same purchase unless the context suggests repeated identical purchases.

Outcomes:

- Clear duplicate: do not write another transaction. Tell the user it appears already recorded.
- Ambiguous duplicate with meaningful bookkeeping risk: ask before writing.
- Weak similarity: proceed only if required fields and validation are otherwise adequate; include a short note if useful.

Do not rely only on generated `transaction_id` for duplicate detection, because imported or older records may use a different ID convention.

## Uncertainty Policy

Avoid unnecessary clarification questions. Use the consequence of uncertainty to decide whether to interrupt the workflow.

Usually non-blocking:

- category is unclear
- exact transaction time is unreadable
- product name normalization is uncertain
- payment method is missing
- item-level discount allocation is unclear but total is reliable

Handle non-blocking uncertainty by preserving original text, leaving optional fields null, storing a conservative note, using an unallocated transaction-level discount, or setting `validation_status` to `partial`.

Usually blocking or review-worthy:

- merchant cannot be determined
- transaction date cannot be determined
- total cannot be determined
- two different totals are equally plausible
- currency cannot be determined
- duplicate risk is unresolved
- source evidence is too incomplete to create a reliable transaction
- arithmetic is materially unreconciled after investigation

Investigate with available source tools before asking the user. Never fabricate missing data.

## Post-Write Verification

When read-back capability exists, verify:

- the transaction row exists
- stored `transaction_id` matches the canonical transaction
- stored total matches the canonical total
- expected item rows exist
- every item row links to the transaction ID
- row count matches expectations, allowing for destinations that summarize items
- duplicate search after write does not show an accidental extra transaction

If verification fails, do not report routine success. Explain the specific remaining issue and whether the write may have partially succeeded.
