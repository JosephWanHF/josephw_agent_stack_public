---
name: github-tool-first
description: Use when creating, reading, updating, publishing, or managing GitHub repositories, branches, commits, issues, or pull requests. Always inspect and use available GitHub connector tools before attempting GitHub CLI or another fallback.
---

# GitHub Tool First

Use the GitHub connector as the primary GitHub surface. Keep local Git for local repository inspection and commits.

## Workflow

1. Inspect the available GitHub connector tools relevant to the requested action.
2. Call a read-only GitHub tool first to confirm the connected account and the target repository or ownership context.
3. Use connector tools for repository, branch, commit, file, issue, pull-request, and review actions whenever the needed operation is available.
4. For a new repository, explicitly check whether a repository-creation connector tool is available before considering any fallback.
5. If the connector lacks the required action, state that specific capability gap. Use GitHub CLI only after the connector check, and only when the user has asked for the operation or approved the fallback.
6. Never expose tokens, and never replace or alter a remote without confirming the target repository and scope.

## Publish Check

Before a GitHub publish, confirm the working-tree scope with local Git, then use the connector to verify the repository and permissions. Prefer connector-created pull requests when a pull request is applicable.
