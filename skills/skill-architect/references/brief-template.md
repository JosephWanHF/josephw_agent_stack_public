# Skill Creation Brief Template

Use this template when the user is ready for an implementation-ready architecture brief. Adapt headings to the task; omit sections that are genuinely irrelevant, but keep side effects, validation, uncertainty, and responsibility boundaries visible.

# Skill Creation Brief

## 1. Working Name

Recommended skill name and any naming rationale needed for discovery.

## 2. User Outcome

The capability the user actually wants, separated from any initial implementation assumptions.

## 3. Target Users / Context

Who will use the skill, where it runs, and whether it is personal, team-based, public, technical, non-technical, project-local, or general-purpose.

## 4. Activation Intent

Semantic conditions under which the skill should apply. Include representative example requests and note whether activation should be automatic or explicit-only when that matters.

## 5. Non-Activation Cases

Similar requests that should not trigger the skill, or should not execute side effects. Include "analyze/preview only" cases when relevant.

## 6. Inputs

Expected input types and sources, such as text, images, documents, PDFs, code, repositories, URLs, structured data, external account data, or tool results.

## 7. Outputs

Expected result types, such as response, file, code change, database mutation, spreadsheet update, report, structured JSON, decision, or tool action.

## 8. Side Effects

External state changes the skill may perform. State authorization boundaries and distinguish read/analyze/plan/preview behavior from write/send/delete/publish/purchase/change behavior.

## 9. Canonical Workflow

High-level execution flow, for example:

```text
input
-> interpret
-> structure
-> validate
-> act
-> verify
-> report
```

## 10. Domain Rules

Domain-specific reasoning the skill should own. Avoid copying generic tool instructions here.

## 11. Data Model / Contracts

Canonical schemas, required fields, normalized values, file formats, interface contracts, or state transition rules.

## 12. Decision Rules

Important branches, thresholds, precedence rules, escalation points, and conditions that change behavior.

## 13. Deterministic Operations

Operations that should use deterministic logic, scripts, parsers, validators, checksums, arithmetic, exact normalization, or external constraints rather than open-ended model reasoning.

## 14. Script / Automation Strategy

Which deterministic or repeated operations should use existing capabilities, one-off commands, bundled scripts, validators, or no script. For each proposed script, specify purpose, interface, inputs, outputs, dependency strategy, error behavior, idempotency, dry-run behavior for risky actions, exit codes, output limits, and validation role.

## 15. Existing Capabilities to Compose With

Relevant installed skills, plugins, MCP servers, connectors, APIs, scripts, project utilities, or native harness capabilities. Describe each capability semantically and name known concrete adapters separately.

## 16. Responsibility Boundaries

What this skill owns and what supporting capabilities own. Identify avoided duplication.

## 17. Validation Strategy

How the agent verifies that the user's intended outcome occurred. Include proportional checks for generated files, state changes, schemas, tests, arithmetic, links, or changed records.

## 18. Duplicate / Idempotency Strategy

How retries, duplicate inputs, repeated commands, or partial previous runs should be detected and handled.

## 19. Uncertainty Handling

What to infer, what to preserve as unknown, what to investigate, and when to ask the user.

## 20. Failure and Recovery

Realistic failure modes and bounded recovery strategy. Prefer safe retry, supported alternative method, preserved partial progress, clear report, and user escalation when needed.

## 21. User-Facing Completion Behavior

What the user should see on normal success, partial success, failure, ambiguity, or blocked execution.

## 22. Portability Considerations

Harness-neutral core behavior and any adapter-specific concerns for Codex, ChatGPT, Claude Code, MCP, plugins, connectors, filesystem conventions, or project instructions.

## 23. Suggested Skill Structure

Suggested files and resources. Include only components with a concrete purpose, such as:

```text
skill-name/
|-- SKILL.md
|-- references/
|-- scripts/
|-- examples/
`-- assets/
```

## 24. Implementation Guidance

Instructions for the downstream skill-authoring system. Say when native conventions are authoritative for exact packaging, metadata, validation, and directory layout.

# Prompt for Skill Creator

Write this as a standalone implementation prompt that can be handed to OpenAI skill-creator, Claude Code, or another capable agent harness. It must not rely on the original conversation.

Include:

- The requested skill name and concise purpose.
- The complete user outcome and scope.
- Activation and non-activation requirements.
- Inputs, outputs, side effects, and authorization boundaries.
- Canonical workflow and domain rules.
- Data contracts, decision rules, deterministic operations, script or automation strategy, and validation strategy.
- Existing capabilities to compose with and responsibility boundaries.
- Uncertainty, failure, recovery, duplicate, and idempotency behavior.
- Portability requirements and harness-specific adapter notes.
- Suggested structure, with permission for the native skill creator to use its own conventions as authoritative for exact packaging and metadata.
- When scripts are useful, require agent-friendly script interfaces: non-interactive execution, `--help`, structured output, helpful errors, safe defaults, idempotency where relevant, dry-run support for risky actions, meaningful exit codes, and bounded output.

Useful closing sentence:

```text
Use your native skill-authoring conventions as authoritative for exact packaging, metadata, validation, and file layout, while preserving the architecture and responsibility boundaries above.
```
