# Cross-Harness Guidance

Use this reference when a skill should remain portable across Codex, ChatGPT, Claude Code, or another agent harness, or when the architecture involves plugins, connectors, MCP servers, nested skills, or environment-specific instructions.

## Keep the Core Semantic

Describe capabilities by responsibility, not by one platform's tool name.

Prefer:

```text
Use the available spreadsheet capability to append the validated transaction while preserving the existing schema.
```

Avoid as a core requirement:

```text
Call google_sheets.batch_update with this exact schema.
```

Exact tool calls can appear in an adapter section when a target harness is known.

## Separate Core From Adapters

Use a layered model:

```text
core domain behavior
-> capability boundary
-> harness adapter
-> concrete tool or external system
```

The core domain behavior should remain stable if the target moves from Codex to Claude Code, from a plugin to MCP, or from one storage backend to another.

Adapter notes may include:

- Which native skill creator or command should package the skill.
- Which project instruction file may matter, such as AGENTS.md, CLAUDE.md, or another harness-specific guide.
- Which installed connector, plugin, MCP server, or script appears to own a supporting responsibility.
- Which metadata or invocation policy should be handled by the native authoring convention.

## Script Portability

Treat scripts as harness adapters unless their logic is central to the domain. Keep the brief clear about what the script must accomplish, then let the native skill creator choose exact packaging and runtime conventions when appropriate.

Portable script guidance should describe:

- The semantic operation the script performs.
- Whether it is a one-off command, bundled helper, validator, or adapter.
- Runtime prerequisites and dependency pinning or declaration.
- Non-interactive invocation, structured output, error behavior, idempotency, dry-run behavior, and output limits.

Avoid making the core architecture depend on one package runner, shell, or operating-system convention unless the target environment requires it.

## Codex / ChatGPT Notes

When working in Codex or ChatGPT environments that support skills:

- Inspect available skills and plugin-provided capabilities before designing tool logic.
- Let a native skill creator remain authoritative for exact `SKILL.md`, metadata, validation scripts, and UI metadata.
- Use project instructions when present and relevant.
- Treat connectors and MCP tools as concrete adapters, not as the domain architecture itself.

## Claude Code Notes

When targeting Claude Code:

- Look for CLAUDE.md, project-local commands, installed MCP servers, repository scripts, and existing slash commands.
- Express the core skill in harness-neutral terms, then note how Claude Code should package or route it according to its native conventions.
- Avoid assuming OpenAI-specific file names or metadata unless the user explicitly requests them.

## Other Harnesses

For other agent systems:

- Identify the native prompt, skill, command, or tool-registration mechanism.
- Map semantic responsibilities onto available capabilities.
- Preserve side-effect boundaries even if the harness has different permission UX.
- Keep the downstream prompt self-contained so another agent can adapt packaging without changing the architecture.

## Portability Review Questions

- Would the brief still make sense if tool names changed?
- Is platform-specific syntax isolated?
- Are side effects described semantically and concretely?
- Does the architecture compose with existing capabilities instead of copying them?
- Could a native authoring agent implement this in its own format without needing this conversation?
