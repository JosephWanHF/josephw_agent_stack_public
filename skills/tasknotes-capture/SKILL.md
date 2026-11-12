---
name: tasknotes-capture
description: Create new Obsidian TaskNotes task notes from chat requests; use for TaskNotes/tasknote/Obsidian task capture, not ordinary notes or generic reminders.
---

# TaskNotes Capture

Use this skill when the user wants to save, create, set up, schedule, or time-block a task in Obsidian TaskNotes from chat. Typical triggers include "TaskNotes", "tasknote", "Obsidian task", "save this as a task", or a clear request to put action items into Joseph's TaskNotes system.

Do not use this skill for ordinary Obsidian notes, knowledge-base updates, generic Codex reminders, scheduled follow-ups, or Google Calendar-only events. Use `obsidian-memory` for ordinary notes and the app automation tools for reminders or follow-ups.

## Boundaries

A request to create or capture a TaskNotes task authorizes only new task-note creation under `TaskNotes/Tasks`. It does not authorize editing `.obsidian`, changing TaskNotes plugin settings, mutating existing TaskNotes files, completing tasks, archiving tasks, deleting tasks, or creating external calendar events.

In Codex, prefer `mcp__obsidian_codex.create_task` for new tasks. Do not create TaskNotes tasks with generic `create_note`; the task-aware tool owns the TaskNotes schema and Backlog defaults. If the task-aware adapter is unavailable, prepare a preview and explain that no vault write occurred.

Do not expose raw `.obsidian/plugins/tasknotes/data.json` contents in chat or notes. If settings context is needed, use filtered adapter output when available, or inspect only the safe fields needed for the task while avoiding credential-bearing values.

## Workflow

1. Extract the task title, details, due date, scheduled date/time, duration, priority, and contexts from the user's request and nearby conversation.
2. Normalize dates and datetimes to ISO-8601 using the current conversation date and timezone. Include concrete dates in the confirmation when the user used relative wording.
3. Normalize priority to `none`, `low`, `normal`, or `high`; default to `normal` when unspecified.
4. Treat `scheduled` as the calendar/time-block placement, `due` as the deadline, and `timeEstimate` as minutes. If the user gives a start and end time, derive `timeEstimate` deterministically.
5. Preserve unsupported metadata such as projects, tags, recurrence, or reminders in `details` unless a safe adapter supports those fields.
6. Before creating a likely duplicate, list or search `TaskNotes/Tasks` when practical and compare normalized title plus due/scheduled metadata. Ask before creating an unclear duplicate.
7. Create the task with `create_task`, passing only supported fields.
8. Verify by reading back the returned path when possible. Confirm the path is under `TaskNotes/Tasks` and that required/requested fields are present.
9. Report the created title, vault-relative path, and important normalized metadata. Mention any unsupported fields preserved in details.

For multi-task requests, create multiple tasks only when each title is clear. Preview and ask first when the list is long, ambiguous, or likely to create duplicates.

## Field Contract

Read [references/tasknotes-field-contract.md](references/tasknotes-field-contract.md) when mapping nontrivial metadata, validating read-back frontmatter, or deciding how to handle unsupported fields.
