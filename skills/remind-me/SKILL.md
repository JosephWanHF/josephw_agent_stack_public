---
name: remind-me
description: Schedule a future catch-up for the current Codex task and project.
disable-model-invocation: true
---

# Remind Me

Schedule a future **handoff** for the current task. Do not ask the user to restate the project or add a separate task.

## Handoff

1. Take the reminder date from the user. Use the current Codex task and its project by default. If the user omits a time, schedule 9:00 AM in their local time and state that assumption. Ask only when no usable date is provided.

2. Build the handoff from the current conversation and workspace. Capture:
   - project name and local path, or that the task is projectless;
   - current goal;
   - completed work and key decisions;
   - the exact stopping point, including relevant files, commands, results, or unanswered questions;
   - the next concrete action and any blocker.

3. Use the app's `automation_update` tool to create or update a follow-up attached to the current task. Check the automation list first and update a matching reminder rather than creating a duplicate. Name it `Follow up: <current project or task>`.

4. Store the handoff in the reminder prompt. At the scheduled time, the reminder must first return this compact catch-up note:

   ```text
   Project: <name and path>
   Goal: <current goal>
   Done: <completed work and decisions>
   Left off: <exact stopping point>
   Next: <one concrete action>
   Blocker: <blocker or none>
   ```

   End by saying that the task is ready to resume. Begin further work only when the user asks to continue.

5. Finish only when the reminder appears in Codex's automation list with the current task as its target, the requested date, and the saved handoff.
