---
name: odysseus-job-search-workspace
description: Use when working on Joseph's Odysseus fork for job-search workflows, personal hub reliability, Markdown/document output quality, performance/slowness triage, email/calendar/job application coordination, or future updates that connect Odysseus with Codex for career/work productivity.
---

# Odysseus Job Search Workspace

## Purpose

Use this skill to keep Odysseus improvements practical for Joseph's personal hub:
email, calendar, notes, job search, application tracking, Markdown documents,
and Codex-assisted coding work.

## Required Context

1. Work in `C:\Users\hongh\Desktop\Work\AI_Workspace\odysseus` unless the user says otherwise.
2. Read `docs\PERSONAL_MODIFICATION_BACKLOG.md` before adding or prioritizing Odysseus features.
3. Check `git status --short --branch` before edits and preserve unrelated user changes.
4. Treat email, calendar, job applications, resumes, cover letters, API keys, OAuth tokens, and local logs as sensitive.

## Improvement Priorities

Prefer changes in this order unless the user gives a different priority:

1. Reliability and speed: diagnose slow panels, slow email/calendar sync, oversized data, background jobs, provider probes, and degraded Docker services.
2. Job-search hub: track roles, companies, contacts, application status, deadlines, interviews, follow-ups, notes, documents, emails, and calendar events.
3. Markdown/document quality: make exports clean, structured, copyable, and suitable for `.md`, resumes, cover letters, application notes, and Codex handoff.
4. Google Calendar and email integrations: prefer OAuth/API-backed integrations over fragile password-style sync when the provider requires it.
5. Codex/Odysseus handoff: keep code work in Codex and personal context/workflow orchestration in Odysseus, with explicit boundaries.

## Implementation Guidance

- Start with a small diagnostic or workflow slice before broad rewrites.
- Prefer modular routes, services, tools, MCP integrations, or focused UI modules.
- For job-search features, build around explicit records and status transitions instead of free-form chat history.
- For Markdown exports, preserve raw model Markdown when possible, normalize headings/lists/tables/code fences, and avoid artifacts from rendered DOM text.
- For performance fixes, identify the slow operation first with logs/timing before changing caching or sync behavior.
- For any automation that reads email/calendar/job data, require user-visible permission and clear dry-run behavior before sending or modifying anything.

## Done Criteria

A good change should include:

- A clear user workflow improvement.
- Privacy-safe behavior for personal data.
- A focused test or manual verification path.
- A backlog update when it changes future direction.
