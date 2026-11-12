---
name: link-ingest
description: Read one or more links, extract metadata and tags for Joseph's Cogito archive, and save validated records to Supabase Project Cogito plus the Google Sheet named Saved Links when asked to ingest, store, archive, or file links.
metadata:
  short-description: Archive links into Cogito
---

# Link Ingest

Use this skill when the user or another agent provides internet links and asks to save, ingest, archive, tag, file, or sync them into Joseph's Cogito system, Supabase Project Cogito, or the Google Sheet named `Saved Links`. Explicit `$link-ingest` invocation with links counts as an ingest request unless the prompt says preview, analyze, or plan only.

Do not use this skill for general web research, one-off link summarization with no storage intent, unrelated Supabase work, or unrelated Google Sheets edits.

## Responsibility

This skill owns the link-ingestion domain: parse the input links, read accessible content, extract metadata, summarize the linked resource, assign AI tags, preserve any user-supplied file tag, deduplicate records, and reconcile the Supabase and Google Sheets destinations.

Compose with existing capabilities instead of copying their mechanics:

- For Supabase project discovery, schema work, SQL, migrations, RLS, and verification, also load and follow the installed Supabase skill when available.
- For finding, creating, reading, or editing the `Saved Links` Google Sheet, also load and follow the installed Google Sheets or Google Drive skill when available.
- For PDFs, Drive files, docs, or other specialized link targets, use the appropriate reader capability and keep extracted facts grounded in the source.

## Side Effects

Reading links and preparing a preview is allowed when this skill applies. Creating database tables, applying migrations, inserting/updating Supabase rows, creating/editing the Google Sheet, or appending rows requires explicit storage intent from the user or invoking agent.

Before first-time schema setup in Project Cogito, identify the exact Supabase project, inspect existing tables, show or reference the intended missing-table setup, and get explicit confirmation if the prompt did not already authorize schema creation. Never create a new Supabase project unless the user specifically asks for project creation and confirms any cost/organization choice required by the Supabase tools.

## File Tag Rule

The `file tag` is special. It is a user-controlled filing label or collection marker, not an AI-generated topical tag. Use exactly the file tag supplied by the user, preserving its human-readable name while also storing a normalized slug. Do not invent a file tag. If the user asks to file links but omits the file tag, ask one concise question unless it is safe to store the links with no file tag.

Normal tags are AI-generated topical tags. Keep them concise, useful for retrieval, and distinct from the file tag.

## Required References

Read [references/workflow.md](references/workflow.md) before running an ingestion workflow.

Read [references/schema.md](references/schema.md) before creating, migrating, validating, or writing the Supabase tables or the `Saved Links` sheet.

Read [references/architecture-brief.md](references/architecture-brief.md) only when revising this skill or handing its design to another skill authoring system.
