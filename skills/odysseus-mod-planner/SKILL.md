---
name: odysseus-mod-planner
description: Manage a change to Joseph's Odysseus workspace against its Personal Modification Backlog. Use when planning, implementing, reviewing, or aligning a change in the configured Odysseus repository.
---

# Odysseus Mod Planner

## Overview

Treat the Personal Modification Backlog as the source of truth for Odysseus changes.

Backlog path:

`C:\Users\hongh\Desktop\Work\AI_Workspace\odysseus\docs\PERSONAL_MODIFICATION_BACKLOG.md`

## Required Workflow

1. Read the backlog and inspect `git status --short` before planning or editing. Finish only when the request's current backlog status and existing user changes are known.
2. Match the request to an existing backlog item. If it introduces a new feature, add the item before editing code.
3. Choose the smallest modular change that fits: a route, service, integration, MCP server, tool, or focused UI module.
4. Preserve unrelated user changes while implementing or reviewing the requested work.
5. Update the backlog status and add a short update-log entry after meaningful work. Finish by reporting the backlog item, the change made, and the verification completed.

## Planning Guidance

Use the backlog to decide whether a request should connect or improve these Odysseus areas:

- Brain and memory
- Library and documents
- Notes
- Tasks
- Calendar
- Email
- Agents and tools
- Personal dashboards and trackers

If a requested feature conflicts with the backlog, call out the conflict and propose a small backlog update before proceeding.
