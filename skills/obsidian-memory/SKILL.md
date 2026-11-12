---
name: obsidian-memory
description: Use the local Obsidian vault as Joseph's personal and AI source of truth through the obsidian-codex MCP server. Use managed mode to read, create, update, append, tag, move, rename, archive, restore, index, and organise ordinary notes.
---

# Obsidian Memory

## Overview

Use the `obsidian-codex` MCP server to maintain Joseph's Obsidian vault in managed mode. Joseph has granted standing authorisation for ordinary note management; do not ask for `I approve` before normal vault changes.

The vault's Codex area is `AI/Codex`. The human communication note is `AI/Codex/Communication.md`. The legacy review queue is `AI/Codex/Approve pending`; it is an audit and compatibility area, not the default workflow.

## Read Workflow

1. Use `vault_info` to confirm managed-mode settings when needed.
2. Use `search_notes`, `list_notes`, and `read_note` to gather context.
3. Treat Obsidian as useful context, not as automatically authoritative when the user gives newer instructions in chat.

## Managed Write And Organize Workflow

Use direct managed tools for ordinary Markdown notes:

- `create_note`
- `update_note`
- `append_to_note`
- `move_note`
- `rename_note`
- `tag_note`
- `archive_note`
- `restore_note`

Every direct operation is recorded in `AI/Codex/Operation Log/`. Before a broad migration, inspect the affected notes, preserve internal links where practical, and report the completed migration with its operation-log location.

`archive_note` is the only removal tool. It moves a note into `AI/Codex/Trash/` and is reversible with `restore_note`. Do not permanently delete notes.

For new TaskNotes tasks, use the dedicated `tasknotes-capture` skill and `create_task` tool instead of generic note creation. That path is the narrow TaskNotes exception because it preserves the TaskNotes schema and Backlog defaults.

## Protected Areas And Secrets

- Never modify `TaskNotes/` or `.obsidian/`, including TaskNotes plugin data, except for creating new task notes through the dedicated `create_task` tool. Any other TaskNotes edit requires Joseph to give a new explicit instruction for a specific file and confirm its schema can be preserved.
- Do not directly modify `AI/Codex/Approve pending/` or `AI/Codex/Trash/`.
- Do not reveal, copy, summarise, or write secret values in conversation, logs, agent memory, or ordinary notes. Handle a credential locally only when Joseph explicitly authorises the specific operational need.
- Ask before external operations, credential rotation, permanent external deletion, or any action outside the vault.

## Legacy Proposal Workflow

Use proposal tools only when the configured server explicitly enables them for a temporary review-only workflow. In the current managed mode they are disabled.

## Note Template

For Codex-created notes, follow `AI/Codex/Templates/Codex Note Template.md` when applicable:

```yaml
created_by: codex
created_at: "{{date}}"
source: codex-mcp
status: draft
```
