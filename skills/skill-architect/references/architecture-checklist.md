# Architecture Checklist

Use this checklist before producing a final Skill Creation Brief, reviewing another brief, or deciding whether the architecture is ready for implementation.

## Intent

- The actual user outcome is clear.
- Outcome is separated from initial implementation assumptions.
- The target user and operating context are clear enough for the requested scope.
- Examples supplied by the user have been treated as evidence without overfitting.

## Activation

- Activation intent is semantic, not just exact phrase matching.
- Representative user requests are included when useful.
- Non-activation cases are defined, especially similar read-only or analysis-only requests.
- Automatic invocation cannot accidentally authorize state-changing behavior.

## Inputs and Outputs

- Expected input artifacts and sources are named.
- Required versus optional input fields are distinguished when relevant.
- Output types are explicit.
- Any structured output contract is clear enough to validate.

## Side Effects

- Read/analyze/plan/preview actions are separated from write/send/delete/publish/purchase/change actions.
- External mutations have authorization boundaries.
- Consequential, irreversible, or externally visible actions are not hidden behind ordinary topic matching.

## Composition

- The environment has been inspected where possible for existing skills, plugins, connectors, MCP servers, APIs, scripts, or project utilities.
- Existing capabilities are composed with rather than duplicated.
- Domain logic and tool logic are separated.
- The architecture avoids both monolithic tool ownership and unnecessary micro-skills.

## Reasoning Mode

- Model-reasoned steps are appropriate for semantic interpretation, ambiguity, extraction, classification, or synthesis.
- Deterministic operations are identified for arithmetic, schema validation, exact parsing, normalization, duplicate keys, transformations, checksums, or constraints.
- Scripts or validators are recommended only where they materially improve reliability or reuse.

## Script and Automation Design

- The design distinguishes existing capabilities, one-off commands, bundled scripts, validators, and model reasoning.
- Proposed scripts have a clear purpose and interface instead of being vague implementation placeholders.
- Script inputs are non-interactive and use command-line flags, stdin, or environment variables.
- Script outputs are structured where useful, with data on stdout and diagnostics on stderr.
- `--help`, helpful errors, meaningful exit codes, safe defaults, dependency strategy, idempotency, dry-run behavior for risky actions, and output-size limits are specified when relevant.

## Validation

- Success is defined by user outcome, not tool-call success.
- The validation plan is proportional to consequence.
- State changes are verified when meaningful, such as by reading changed records back.
- Generated artifacts have an observable existence, structure, or behavior check.

## Uncertainty

- Minor uncertainty has a safe default, null/unknown representation, or preservation strategy.
- Material uncertainty triggers investigation or a concise user question.
- The design does not invent facts to finish the workflow.

## Failure and Recovery

- Realistic failure modes are covered.
- Recovery is bounded: safe retry, alternative supported method, preserve partial progress, report clearly, ask user when necessary.
- The design avoids speculative fallback trees and endless retries.

## Duplicates and Idempotency

- Repeated inputs, retries, partial previous runs, and duplicate records are considered when relevant.
- Idempotency keys, natural keys, checksums, or read-before-write checks are proposed where they reduce risk.

## Portability

- Core requirements are expressed as semantic capabilities rather than hard-coded tool calls.
- Harness-specific implementation details are isolated as adapters or notes.
- Platform-specific packaging syntax is left to the native authoring workflow unless the user requested a specific platform.

## Implementation Readiness

- Suggested skill structure includes only files with concrete purpose.
- The downstream prompt is self-contained.
- A skill creator could implement the skill without seeing the original conversation.
- Open questions, if any, are consequential and grouped for the user.
