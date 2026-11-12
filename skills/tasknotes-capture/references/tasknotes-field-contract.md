# TaskNotes Field Contract

This reference documents Joseph's current TaskNotes capture contract for Codex. It is intentionally limited to safe task metadata and should not be treated as permission to expose or edit raw plugin settings.

## Local TaskNotes Context

- TaskNotes plugin: `tasknotes` version `4.4.0`
- Task folder: `TaskNotes/Tasks`
- View folder: `TaskNotes/Views`
- Task identification: tag-based, using `task`
- Backlog status: `none`
- Priority values: `none`, `low`, `normal`, `high`
- Default priority: `normal`

## Current Codex Adapter

Use `mcp__obsidian_codex.create_task` for new TaskNotes tasks.

Supported input fields:

```json
{
  "title": "string",
  "details": "string | optional",
  "due": "ISO-8601 date or datetime | optional",
  "scheduled": "ISO-8601 date or datetime | optional",
  "timeEstimate": "positive integer minutes | optional",
  "priority": "none | low | normal | high",
  "contexts": ["string"],
  "requestedBy": "codex | optional"
}
```

Expected created-note behavior:

- The path is under `TaskNotes/Tasks`.
- `status` is `none`, which TaskNotes labels as Backlog.
- `priority` is one of the supported priority values.
- `dateCreated` and `dateModified` are set by the adapter.
- Task-identifying tags include `task`.
- `due`, `scheduled`, `timeEstimate`, and `contexts` are present only when requested or inferred.

## Field Meaning

- `title`: concise task title. Keep execution details out of the title when they fit better in `details`.
- `details`: Markdown body for source context, notes, acceptance criteria, links, or unsupported metadata.
- `due`: deadline. Use for "due by", "deadline", or date-only expectations.
- `scheduled`: planned placement on the calendar. Use for "at", "from X to Y", "calendar block", or "work on this then".
- `timeEstimate`: duration in minutes. Derive from a start/end time when both are known.
- `priority`: normalize user wording such as "urgent" or "important" to `high`, "low priority" to `low`, and unspecified to `normal`.
- `contexts`: TaskNotes contexts, usually from `@context` wording or clear environment/person/workstream labels.

## Unsupported Or Future Fields

The local TaskNotes plugin also has concepts such as `projects`, `tags`, `recurrence`, `reminders`, dependency fields, calendar integration IDs, and time entries. Do not invent these frontmatter fields through the current `create_task` adapter.

When the user provides unsupported but useful metadata:

- Preserve it in `details` if doing so keeps the task useful and does not misrepresent adapter support.
- Ask before proceeding if the unsupported field is the core point of the request, such as a required reminder or recurrence.

## Duplicate And Retry Handling

The current adapter may fail when the filename already exists. Before creating obvious duplicates, list or search `TaskNotes/Tasks` and compare:

- normalized title
- due date
- scheduled date/time
- duration

If a create attempt returns an ambiguous failure, check whether the intended task was created before retrying.
