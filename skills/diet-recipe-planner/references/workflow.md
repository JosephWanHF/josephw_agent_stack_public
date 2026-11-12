# Diet Recipe Planning Workflow

## Input Interpretation

Accept requests such as "what can I cook from my fridge", "match recipes to my inventory", "make a shopping list", "I accept recipe 2", "reject that suggestion", or "log that I cooked this".

If the user supplies new fridge photos in the same request, use `fridge-capture` first when they want the photos recorded. If they only want recipe ideas from a photo without persistence, identify visible items conservatively and do not update inventory.

## Destination Resolution

Resolve Supabase Project Cogito before database writes:

1. Use available Supabase project discovery to find the project named `Project Cogito`.
2. If multiple projects match, ask Joseph to choose.
3. If none matches, ask for the project ID. Do not create a Supabase project unless Joseph explicitly asks for project creation and confirms any required organization or cost choices.
4. Inspect existing tables before creating or changing schema.
5. Use [schema.md](schema.md) as the intended table contract.

## Inventory Reading

Read available inventory from `public.diet_meta_food_item_record`, scoped through the `joseph` row in `public.joseph_cogito`.

Treat inventory as dated and uncertain:

- Prefer records with `status = 'available'`.
- Keep confidence and notes in mind when using image-derived items.
- Do not assume a stored item is still available if later records mark it used, discarded, or expired.
- If inventory is empty or stale, say so and ask whether to capture a fresh fridge photo.

## Recipe Matching

First recall useful stored recipes from `public.diet_meta_recipes_record`, especially accepted or previously cooked recipes. Then synthesize new options when recall does not satisfy the request.

For each candidate, produce:

- Recipe name
- Match rationale based on available items
- Ingredients already available
- Missing ingredients
- Shopping list entries grouped by likely grocery category
- Basic steps
- Servings and timing when known or reasonably estimated
- Any uncertainty or substitution options

Prefer recipes that use perishable or `use_soon` items, then recipes that minimize missing ingredients. Do not fabricate that an ingredient is present merely to improve the match.

## Canonical Recipe Record

Build records in this shape before writing:

```json
{
  "recipe_name": "Mushroom spinach omelette",
  "recipe_slug": "mushroom-spinach-omelette",
  "source": "agent",
  "recipe_status": "suggested",
  "meal_type": "breakfast",
  "cuisine": null,
  "servings": 1,
  "prep_minutes": 5,
  "cook_minutes": 10,
  "ingredients": [
    {"name": "eggs", "quantity": 2, "unit": "each", "available": true}
  ],
  "steps": [
    {"order": 1, "text": "Beat the eggs."}
  ],
  "matching_food_item_ids": [],
  "missing_ingredients": [
    {"name": "butter", "quantity": 1, "unit": "tablespoon", "optional": false}
  ],
  "shopping_list": [
    {"name": "butter", "quantity_text": "1 small pack", "category": "dairy", "needed_for": "Mushroom spinach omelette"}
  ],
  "match_score": 0.82,
  "rationale": "Uses eggs and spinach already recorded in the fridge.",
  "metadata": {}
}
```

Use JSON arrays for `ingredients`, `steps`, `missing_ingredients`, and `shopping_list`. Use `null` or omit optional values when unknown.

## Decision and Meal Logging

When Joseph accepts a suggestion, update the matching recipe row to `accepted` and set `decided_at`.

When Joseph rejects a suggestion, update the matching recipe row to `rejected`, set `decided_at`, and preserve any reason in `metadata` or `rationale`.

When Joseph says a meal was cooked, insert a row into `public.diet_meta_diet_record`. If the meal came from a saved recipe, link `recipe_record_id` and update the recipe row to `cooked` with `cooked_at`. Only mark food items as `used` when Joseph explicitly says they were used or when the cooked-meal request clearly identifies the ingredients consumed.

## Shopping List

Generate the shopping list from missing required ingredients. Separate optional substitutions from required purchases. Combine duplicate items across recipes when presenting the list, but preserve per-recipe detail in stored `shopping_list` JSON.

Do not add staples such as salt, pepper, water, or oil unless the recipe truly depends on a nonstandard version or Joseph asks for a complete list.

## Write Sequence

For a Cogito-backed planning run:

1. Resolve Project Cogito and inspect schema.
2. Ensure the diet tables in [schema.md](schema.md) exist.
3. Read current available inventory and relevant recipe history.
4. Generate or recall candidate recipes.
5. Compute missing ingredients and shopping list entries.
6. Insert suggested recipes into `public.diet_meta_recipes_record`, unless preview-only was requested.
7. Verify saved recipe rows by reading them back.
8. Report recipe options, match rationale, missing ingredients, and saved record status.

For accept/reject/cooked updates, read the candidate row first, update or insert the specific row, verify by reading it back, and report the changed status.

## Completion Report

On success, show the best recipe options and one consolidated shopping list. Mention which recipes were saved, accepted, rejected, or logged. For preview-only runs, clearly say no database changes were made.
