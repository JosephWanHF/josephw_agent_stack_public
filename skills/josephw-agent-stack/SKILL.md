---
name: josephw-agent-stack
description: Export, install, validate, or update Joseph's portable agent skill stack across Codex-style environments.
---

# JosephW Agent Stack

Use this skill when Joseph asks to sync, install, validate, publish, or update `josephw_agent_stack`.

## Workflow

Work from the repo root. Prefer the stack CLI over manual copying:

```bash
python scripts/agent-stack.py validate
python scripts/agent-stack.py export
python scripts/agent-stack.py install --dry-run
python scripts/agent-stack.py install
```

Use `export` on the source Codex machine to refresh `skills/` and `agent-stack.yaml`. Use `install` on another Codex machine to copy the stack into that machine's `$CODEX_HOME/skills` or `~/.codex/skills`.

## Boundaries

Share portable skills and declarative capability requirements. Keep credentials, OAuth sessions, browser state, logs, SQLite databases, plugin caches, and machine-local Codex state out of the repo.

Do not vendor OpenAI built-in/default skills. The stack may declare desired plugins or connectors, but each target environment must install or authorize them locally.

Before publishing or pushing, run `validate` and inspect `git status` so the commit contains only intended stack files.
