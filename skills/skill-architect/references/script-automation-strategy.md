# Script and Automation Strategy

Use this reference when a proposed skill may need reusable deterministic helpers, validators, one-off commands, or external tool invocations. Do not add scripts mechanically. Recommend them only when they materially improve reliability, repeatability, portability, or maintainability.

## Choose the Right Automation Shape

Prefer an existing capability when a tool, connector, MCP server, plugin, project script, or supporting skill already owns the responsibility.

Use a one-off command when an existing package or CLI can do the job with a short, stable invocation. Specify prerequisites and pin versions where possible.

Use a bundled script when the operation is repeated, fragile, multi-step, hard to invoke correctly, or needs deterministic validation. Scripts are especially useful for arithmetic, schema checks, normalization, duplicate detection, file transformations, exact parsing, and state verification.

Use model reasoning when the operation depends on semantic interpretation, ambiguous human language, synthesis, classification with context, or messy extraction that cannot be made deterministic.

## Script Interface Requirements

For each proposed script, specify:

- Purpose and boundary: what the script owns and what remains model-reasoned.
- Invocation: relative path from the skill root and expected command form.
- Inputs: command-line flags, stdin, or environment variables. Avoid interactive prompts.
- Outputs: structured stdout when data will be consumed by the agent or another tool.
- Diagnostics: progress, warnings, and debug information on stderr.
- Help: concise `--help` with description, flags, examples, and documented exit codes.
- Errors: messages that say what failed, what was expected, and what to try next.
- Dependencies: runtime prerequisites, pinned versions, or inline dependency declarations where supported.
- Idempotency: behavior for retries, duplicate inputs, and partial previous runs.
- Safety: `--dry-run`, `--confirm`, `--force`, or similar safeguards for risky or state-changing actions.
- Output size: default summaries, pagination, limits, or `--output` file support for large results.
- Validation role: how the script helps prove the user's outcome happened.

## Brief Example

For a receipt bookkeeping skill, a script recommendation might look like:

```text
scripts/validate_transaction.py

Purpose:
Validate a normalized receipt transaction before persistence.

Invocation:
python scripts/validate_transaction.py --input transaction.json --schema references/transaction.schema.json --output -

Inputs:
JSON transaction file and schema path. No interactive prompts.

Outputs:
JSON validation result on stdout:
{"valid": true, "warnings": [], "errors": []}

Diagnostics:
Progress and parse warnings go to stderr.

Behavior:
Exit 0 for valid, 2 for schema/validation failure, 3 for unreadable input. Does not write external state. Safe to retry.
```

The downstream skill creator may change the language, packaging, or exact runtime command according to native conventions, while preserving the script purpose and agent-friendly interface.
