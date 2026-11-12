---
name: sync-matt-pocock-skills
description: Check, install, or safely update the maintained general-purpose skills from mattpocock/skills in a Codex profile. Use when a user asks to install, sync, refresh, compare, or update Matt Pocock's Skills for Real Engineers on this or another Codex machine.
---

# Sync Matt Pocock Skills

Use the bundled script to compare the maintained engineering and productivity set with `mattpocock/skills` on GitHub. It manages 22 skills only; it deliberately excludes upstream `deprecated`, `in-progress`, `misc`, and `personal` folders.

## Workflow

1. Run a preview first:

   ```powershell
   python scripts/sync_matt_pocock_skills.py --check
   ```

   The script downloads the current upstream snapshot, compares every managed file, and reports missing, current, and changed skills. It makes no local changes in this mode.

2. Explain the result. If the user has asked to update or explicitly confirms the preview, apply it:

   ```powershell
   python scripts/sync_matt_pocock_skills.py --apply
   ```

   The apply mode installs missing skills and replaces changed managed skills. Before a replacement, it moves the existing folder to `.mattpocock-skills-backups` under the same skills directory, so local edits are recoverable. It never removes unrelated skills.

3. Report the upstream commit and the skills changed. Tell the user that newly installed or updated skills are available on their next Codex turn.

## Another Codex Machine

Copy this entire `sync-matt-pocock-skills` folder into the other machine's `$CODEX_HOME/skills` directory (usually `~/.codex/skills`). On that machine, start a new Codex turn and ask to use `$sync-matt-pocock-skills` to run the preview and apply the update.

If the other machine has not received this helper yet, install the desired upstream folders with Codex's standard GitHub skill installer first, then copy this folder for future updates.
