# Skill Creation Brief

## 1. Working Name

`diet-recipe-planner`

## 2. User Outcome

Joseph can ask agents what to cook from recorded fridge inventory, receive matched or recalled recipes, get a shopping list for missing ingredients, and record recipe decisions and cooked meals in Supabase Project Cogito.

## 3. Target Users / Context

Personal Codex skill for Joseph's Cogito workspace. It runs in an agent environment with Supabase access and may compose with web research or fridge-photo capture.

## 4. Activation Intent

Use for recipe suggestions from current inventory, recipe recall, shopping lists, accept/reject decisions, and cooked-meal logging.

## 5. Non-Activation Cases

Do not activate for generic recipes unrelated to inventory, medical diet advice, restaurant recommendations, or raw fridge-photo extraction without planning intent.

## 6. Inputs

Stored inventory rows, recipe history, user preferences, user accept/reject decisions, meal logs, optional new photos, and optional external recipe sources.

## 7. Outputs

Recipe options, match rationale, missing ingredients, shopping lists, saved suggested recipes, recipe status updates, and cooked meal rows.

## 8. Side Effects

Saving suggested recipes, updating recipe status, logging meals, and marking food items used are database writes. Preview-only planning makes no database changes.

## 9. Canonical Workflow

```text
recipe request
-> read current inventory
-> recall relevant recipes
-> generate or match candidates
-> compute missing ingredients
-> save suggestions when appropriate
-> verify readback
-> report options and shopping list
```

## 10. Domain Rules

Prefer recipes using available and perishable items. Do not claim missing ingredients are available. Group shopping list items while preserving per-recipe detail in stored JSON.

## 11. Data Model / Contracts

Read inventory from `public.diet_meta_food_item_record`. Store suggestions and decisions in `public.diet_meta_recipes_record`. Store cooked meals in `public.diet_meta_diet_record`.

## 12. Decision Rules

Save suggestions for Cogito-backed planning unless preview-only is requested. Update accepted/rejected only on explicit user decision. Log cooked meals only when Joseph says a meal was cooked, eaten, logged, or planned.

## 13. Deterministic Operations

Use deterministic SQL constraints for status values, JSON array/object shapes, confidence and score ranges, idempotency, and readback verification.

## 14. Script / Automation Strategy

No bundled scripts are needed. Use SQL and structured JSON records. External recipe lookup is optional and should use existing browser/research tools.

## 15. Existing Capabilities to Compose With

Use the Supabase skill/plugin for schema and writes, `fridge-capture` for image-based inventory, and browser/research tools only when live or sourced recipes are requested.

## 16. Responsibility Boundaries

This skill owns recipe planning and meal logging, not image extraction, receipt capture, or medical advice.

## 17. Validation Strategy

After schema creation or writes, read back table metadata or affected rows and confirm expected statuses or inserted records.

## 18. Duplicate / Idempotency Strategy

Use idempotency keys for repeated planning runs or decision updates. Reuse existing recipe rows when a user decision clearly refers to one.

## 19. Uncertainty Handling

If inventory is stale, empty, or ambiguous, say so and offer to capture a fresh fridge photo. Preserve substitutions and optional items separately from required purchases.

## 20. Failure and Recovery

On partial write failure, report which suggestions or meal rows saved and which need retry. Do not mark inventory used unless the user clearly confirms use.

## 21. User-Facing Completion Behavior

Show best recipe options, a consolidated shopping list, and saved/updated status. For preview-only runs, state that no database changes were made.

## 22. Portability Considerations

Core behavior is semantic. Supabase MCP/SQL is an adapter; exact packaging follows native skill conventions.

## 23. Suggested Skill Structure

```text
diet-recipe-planner/
|-- SKILL.md
`-- references/
    |-- workflow.md
    |-- schema.md
    `-- architecture-brief.md
```

## 24. Implementation Guidance

Use native skill-authoring conventions for packaging and metadata while preserving the side-effect boundary and Cogito schema contract.

# Prompt for Skill Creator

Create a Codex skill named `diet-recipe-planner` that reads Joseph's Cogito fridge inventory, suggests or recalls recipes, computes missing ingredients and shopping lists, records recipe suggestions and accept/reject decisions, and logs cooked meals in Supabase Project Cogito. It should compose with Supabase capabilities and the `fridge-capture` inventory skill, use `public.diet_meta_food_item_record`, `public.diet_meta_recipes_record`, and `public.diet_meta_diet_record`, require explicit intent for database writes, verify changes by reading them back, and avoid medical nutrition advice. Use your native skill-authoring conventions as authoritative for exact packaging, metadata, validation, and file layout, while preserving the architecture and responsibility boundaries above.
