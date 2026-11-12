---
name: fridge-capture
description: Identify food from Joseph's fridge photos or fridge inventory notes and save dated item records to Supabase Project Cogito when asked to record, update, or track what is in the fridge.
metadata:
  short-description: Record fridge inventory in Cogito
---

# Fridge Capture

Use this skill when Joseph sends fridge, freezer, pantry, or food-storage photos and asks to identify, record, update, inventory, track, or save the food in Cogito. Explicit `$fridge-capture` invocation with photos counts as a fridge inventory request unless the prompt says preview, analyze, or plan only.

Do not use this skill for general image description with no inventory intent, restaurant meal logging, grocery receipt bookkeeping, nutrition advice, or recipe planning unless the user also asks to update the stored fridge inventory.

## Responsibility

This skill owns fridge-inventory capture: inspect user-provided photos or notes, identify visible food items, normalize item names, preserve uncertainty, estimate quantities only when visible or stated, and write dated item records to Joseph's Cogito diet tables.

Compose with existing capabilities instead of copying their mechanics:

- For image inspection, use the available visual/image-reading capability and treat the photo as source evidence.
- For Supabase project discovery, SQL, RLS, schema changes, and verification, also load and follow the installed Supabase skill when available.
- For recipe matching or shopping lists, hand off to the `diet-recipe-planner` skill after the inventory record is written or when the user asks for recipes.

## Side Effects

Photo inspection and previewing extracted items is allowed when this skill applies. Creating tables, changing schema, inserting records, or updating item status requires explicit storage intent from the user or invoking agent.

Before first-time schema setup in Project Cogito, identify the exact Supabase project, inspect existing Cogito tables, read [references/schema.md](references/schema.md), and verify created tables by reading them back. Never create a new Supabase project unless the user specifically asks for project creation and confirms any required organization or cost choices.

## Required References

Read [references/workflow.md](references/workflow.md) before running an inventory capture workflow.

Read [references/schema.md](references/schema.md) before creating, validating, or writing the Supabase diet inventory tables.

Read [references/architecture-brief.md](references/architecture-brief.md) only when revising this skill or handing its design to another skill authoring system.
