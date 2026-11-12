# josephw_agent_stack_public

A portable collection of Codex skills generated from Joseph's private canonical agent skill stack.

This public repository contains reusable instructions and helper scripts only. It includes instruction for quickly setup agents skills for harnesses. Skills that use Google Drive, Gmail, Supabase, or other connected services instruct each user to select and authorize their own resources.

## Install

```bash
git clone https://github.com/JosephWanHF/josephw_agent_stack_public.git
cd josephw_agent_stack_public
python scripts/agent-stack.py validate
python scripts/agent-stack.py install --dry-run
python scripts/agent-stack.py install
```

The installer writes to `$CODEX_HOME/skills` when set, otherwise `~/.codex/skills`. It verifies every skill against the checked-in manifest before changing the target profile and backs up changed destination skills.

## Connect your own services

The repository does not include accounts or resource IDs. When a skill needs Gmail, Google Drive, Supabase, GitHub, Figma, Vercel, or another service:

1. Install and authorize the relevant connector in your own Codex environment.
2. Ask the agent to locate or create the resource you want to use.
3. Keep selected resource IDs in local configuration or connector state, not in this repository.

## Synchronization

Do not edit this public mirror directly. It is generated from the private canonical repository, sanitized, integrity-checked, and published automatically.
