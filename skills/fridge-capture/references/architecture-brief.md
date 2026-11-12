# Skill Creation Brief

## 1. Working Name

`fridge-capture`

## 2. User Outcome

Joseph can send agents photos or notes about food in his fridge and have the agent identify visible items, preserve uncertainty, and record dated inventory rows in Supabase Project Cogito.

## 3. Target Users / Context

Personal Codex skill for Joseph's Cogito workspace. It runs in an agent environment with image understanding and Supabase access.

## 4. Activation Intent

Use for fridge photos, freezer photos, pantry photos, food-storage notes, inventory updates, and requests to save or track what food is currently available.

## 5. Non-Activation Cases

Do not activate for recipe planning only, restaurant meals, nutrition advice, generic image description with no inventory intent, or receipt bookkeeping.

## 6. Inputs

Images, text notes, user corrections, attachment labels, optional source metadata, and existing Supabase records.

## 7. Outputs

Previewed item list, inserted or updated Supabase rows, and a completion summary with uncertain detections.

## 8. Side Effects

Database writes are allowed only when the user asks to record, update, save, or track inventory. Preview-only analysis makes no database changes.

## 9. Canonical Workflow

```text
photos or notes
-> identify visible items
-> normalize and preserve uncertainty
-> resolve Project Cogito
-> ensure schema
-> write dated records
-> verify readback
-> report
```

## 10. Domain Rules

Use conservative visual extraction. Do not infer hidden items or expiration dates. Aggregate duplicate visible items within a photo batch unless item-level separation matters.

## 11. Data Model / Contracts

Rows live in `public.diet_meta_food_item_record`, scoped by `joseph_cogito_id`. Related recipe and meal tables share the same `diet_meta_` prefix.

## 12. Decision Rules

Preview when storage intent is absent. Update prior rows only for clear corrections. Otherwise preserve dated history with new records.

## 13. Deterministic Operations

Use deterministic SQL constraints for confidence bounds, statuses, generated normalized names, uniqueness, and readback verification.

## 14. Script / Automation Strategy

No bundled scripts are needed. Supabase SQL and agent-side structured records are enough for this scope.

## 15. Existing Capabilities to Compose With

Use image-reading capability for photos, the Supabase skill/plugin for schema and writes, and `diet-recipe-planner` for recipe matching.

## 16. Responsibility Boundaries

This skill owns inventory capture, not recipe planning, nutrition advice, or receipt extraction.

## 17. Validation Strategy

After schema creation or writes, read back table metadata or affected rows and confirm RLS is enabled.

## 18. Duplicate / Idempotency Strategy

Use `idempotency_key` and `capture_batch_key` plus normalized item name when available. Avoid deleting history.

## 19. Uncertainty Handling

Store unknown values as null or `unknown`, include confidence, and report uncertain detections.

## 20. Failure and Recovery

On partial write failure, preserve successful rows, report failed items, and retry only safe idempotent operations.

## 21. User-Facing Completion Behavior

Report item counts, uncertain items, and whether records were saved or previewed only.

## 22. Portability Considerations

Core behavior is semantic. Supabase MCP/SQL is an adapter; exact packaging follows native skill conventions.

## 23. Suggested Skill Structure

```text
fridge-capture/
|-- SKILL.md
`-- references/
    |-- workflow.md
    |-- schema.md
    `-- architecture-brief.md
```

## 24. Implementation Guidance

Use native skill-authoring conventions for packaging and metadata while preserving the side-effect boundary and Cogito schema contract.

# Prompt for Skill Creator

Create a Codex skill named `fridge-capture` that identifies food from Joseph's fridge or food-storage photos and records dated inventory rows in Supabase Project Cogito. It should compose with image-reading and Supabase capabilities, use `public.diet_meta_food_item_record` scoped to `public.joseph_cogito`, preserve uncertainty, require explicit storage intent for writes, verify schema and row changes by reading them back, and route recipe planning to a separate `diet-recipe-planner` skill. Use your native skill-authoring conventions as authoritative for exact packaging, metadata, validation, and file layout, while preserving the architecture and responsibility boundaries above.
