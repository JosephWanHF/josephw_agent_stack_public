---
name: skill-architect
description: Architect reusable agent capabilities from rough user ideas before implementation. Use when the user needs help specifying, decomposing, composing, validating, or making an agent skill portable. Produces a self-contained Skill Creation Brief for a native skill creator or another agent harness; focuses on intent, responsibility boundaries, side effects, validation, existing capability reuse, and cross-harness architecture rather than native skill packaging.
---

# Skill Architect

Use this skill to turn an incomplete idea for an agent capability into a well-reasoned, implementation-ready Skill Creation Brief. The brief should be complete enough that another capable agent, without the original conversation, can create the intended skill reliably.

This is a meta-skill. It does not replace a native skill creator, package manager, command generator, or harness-specific authoring workflow. Its job is to understand and architect the capability before implementation.

## Operating Boundary

Own requirements discovery, user-intent analysis, workflow decomposition, activation and non-activation reasoning, inputs and outputs, side-effect boundaries, domain/tool separation, composition with existing capabilities, deterministic/script strategy, validation strategy, uncertainty handling, failure/recovery design, portability, suggested structure, and the final creation brief.

Do not primarily own native packaging details, exact platform metadata syntax, tool-specific mechanics already covered by another installed skill, or implementation of the requested domain skill unless the user explicitly asks to proceed after the architecture is resolved.

When a native skill-authoring capability is available, let it remain authoritative for exact file layout, metadata, and validation conventions. Think of the flow as:

```text
rough user idea
-> Skill Architect
-> Skill Creation Brief
-> native skill creator or authoring workflow
-> finished skill
```

## Discovery Style

Understand before authoring. Do not immediately convert the first user sentence into a `SKILL.md` or equivalent native package.

Separate the user's desired outcome from their proposed implementation. Respect explicit requirements, but identify unnecessary coupling. For example, "put receipts in Google Sheets" may mean the domain skill owns receipt bookkeeping semantics while an existing spreadsheet capability owns sheet mechanics.

Infer reasonable details from conversation context, files, existing project structure, installed skills, plugins, connectors, MCP servers, tools, and local conventions. Ask questions only when an answer would materially change architecture, user-facing behavior, data model, safety, side effects, integration choice, irreversible behavior, or important validation logic. Group consequential questions instead of interrupting repeatedly.

Treat examples as requirements evidence. Infer semantic activation intent, likely schemas, edge cases, tone, and automation level without overfitting to exact wording or assuming one example covers every case.

## Environment Inspection

Before specifying detailed tool behavior, inspect available capabilities when possible. Look for installed skills, plugins, connectors, MCP servers, native tools, scripts, APIs, project utilities, and harness instructions that already own part of the workflow.

Prefer composition over duplication:

```text
user request
-> domain skill
-> supporting skill or adapter
-> tool capability
-> external system
```

Split responsibilities when it improves reuse, maintainability, portability, clarity, independent evolution, or tool abstraction. Keep responsibilities together when splitting would only add complexity.

## Architecture Rules

Distinguish domain logic from tool logic. Domain logic defines what the task means; tool logic defines how an external system is manipulated. Prefer a domain skill that composes with available tool capabilities over embedding every tool's mechanics.

Distinguish model reasoning from deterministic operations. Use model reasoning for semantic interpretation, classification, extraction from messy inputs, ambiguity resolution, and synthesis. Use deterministic logic or scripts for arithmetic, schema validation, exact ID generation, duplicate key checks, date normalization, file transformations, checksums, database constraints, and exact parsing when format is known.

When deterministic or repeated logic may be needed, decide whether it belongs in an existing capability, a one-off command, a bundled script, or no script at all. If recommending scripts, architect their interfaces for agentic use: non-interactive inputs, clear `--help`, structured stdout, diagnostics on stderr, helpful errors, pinned or declared dependencies, idempotency, dry-run support for risky actions, meaningful exit codes, safe defaults, and bounded output. For script-heavy skills, read [references/script-automation-strategy.md](references/script-automation-strategy.md).

Make side effects explicit. Separate read/analyze/plan/preview work from write/send/delete/publish/purchase/change operations. A topic match does not authorize external mutation. If automatic activation is possible, ensure execution boundaries prevent accidental state changes.

Define success by user outcome, not by "a tool call succeeded." Validation should be proportional to consequence: read changed records back, reconcile arithmetic, validate schemas, run checks, confirm generated files, or otherwise verify the intended outcome when meaningful.

Design uncertainty handling. Minor uncertainty should usually be preserved or handled with safe defaults; material uncertainty should trigger investigation or a concise user question. Never invent information merely to complete the workflow.

## Output Contract

The primary deliverable is a self-contained `Skill Creation Brief`, followed by a `Prompt for Skill Creator`. Use [references/brief-template.md](references/brief-template.md) when producing the final brief or a handoff prompt.

Before finalizing a substantial brief, review it against [references/architecture-checklist.md](references/architecture-checklist.md). For cross-platform, connector-heavy, MCP-heavy, or harness-specific work, consult [references/cross-harness-guidance.md](references/cross-harness-guidance.md) and isolate adapters from the core domain architecture. For skills likely to need reusable deterministic helpers, consult [references/script-automation-strategy.md](references/script-automation-strategy.md) before proposing `scripts/` resources.

If the user asks for a concrete example or you need a pattern for capability composition, refer to [examples/receipt-bookkeeper.md](examples/receipt-bookkeeper.md). Do not bias unrelated skills toward bookkeeping or spreadsheets; use it only as an architecture example.

## Handoff Behavior

If the current environment has a native skill creator and the user explicitly asks to implement the skill, first produce or preserve the architecture brief, then hand the completed brief to that authoring capability or continue using its native conventions. If direct delegation is unavailable, provide the complete brief and downstream prompt.

For iterative refinement, maintain the working architecture: confirmed requirements, inferred requirements, unresolved consequential decisions, discarded alternatives, discovered existing capabilities, and responsibility boundaries. When the user changes one requirement, update affected sections without restarting unrelated analysis.
