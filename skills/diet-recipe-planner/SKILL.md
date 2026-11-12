---
name: diet-recipe-planner
description: Use Joseph's Cogito fridge inventory to suggest or recall recipes, save recipe suggestions and accept/reject decisions, log cooked meals, and produce shopping lists for missing ingredients.
metadata:
  short-description: Plan recipes from Cogito inventory
---

# Diet Recipe Planner

Use this skill when Joseph asks what to cook from current fridge inventory, wants recipe ideas matched to stored food items, asks for missing ingredients or a shopping list, accepts or rejects a suggested recipe, or wants to record a cooked meal in Cogito. Explicit `$diet-recipe-planner` invocation counts as a recipe-planning request unless the prompt says preview, analyze, or plan only.

Do not use this skill for generic recipes unrelated to Joseph's stored inventory, medical nutrition advice, calorie planning, restaurant recommendations, or fridge-photo extraction unless the user also asks to record inventory; use `fridge-capture` for inventory capture first.

## Responsibility

This skill owns recipe planning from stored inventory: read current available food records, recall previously suggested recipes, propose recipes with a clear match rationale, identify missing ingredients, format a shopping list, save suggested recipes when the user asks for Cogito-backed planning, update recipe decisions, and log cooked meals.

Compose with existing capabilities instead of copying their mechanics:

- For Supabase project discovery, SQL, RLS, schema changes, and verification, also load and follow the installed Supabase skill when available.
- For fresh fridge photos or food-identification from images, use `fridge-capture` before planning from inventory.
- For web research into recipes, use browser or research capabilities only when the user wants external recipes or live source lookup; otherwise synthesize recipes from common culinary knowledge and stored recipe records.

## Side Effects

Reading inventory and presenting recipe options is allowed when this skill applies. Creating tables, inserting suggested recipes, updating accepted/rejected status, logging cooked meals, or marking food items as used requires explicit recipe-planning, decision, or meal-logging intent from the user or invoking agent.

When the user asks for recipes based on Cogito or fridge inventory, save each suggested recipe to `public.diet_meta_recipes_record` with status `suggested` unless they explicitly request preview-only output. Only change a recipe to `accepted` or `rejected` when the user clearly makes that decision. Only insert a meal into `public.diet_meta_diet_record` when the user says they cooked, ate, logged, or planned that meal.

## Required References

Read [references/workflow.md](references/workflow.md) before running a recipe-planning, recipe-decision, shopping-list, or meal-logging workflow.

Read [references/schema.md](references/schema.md) before creating, validating, or writing the Supabase diet recipe and meal tables.

Read [references/architecture-brief.md](references/architecture-brief.md) only when revising this skill or handing its design to another skill authoring system.
