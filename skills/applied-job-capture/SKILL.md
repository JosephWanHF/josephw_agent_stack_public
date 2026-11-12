---
name: applied-job-capture
description: Record the user's newly applied jobs from pasted job links, enrich them with Gmail confirmation evidence when available, and sync the result to the Supabase job_search source of truth plus the Google Drive shortlist tracker.
---

# Applied Job Capture

Use this skill when the user says they have applied to one or more jobs and pastes job links, application links, LinkedIn/Indeed URLs, company career-page URLs, screenshots/text from a posting, or a short natural-language note to record the application.

Do not use this skill for jobs the user is only considering, shortlisting, researching, or drafting materials for. It also does not submit applications, send emails, or manage recruiter outreach unless the user explicitly asks for a separate action.

## Outcome

Create or update a confirmed job-application record with the least friction for the user:

1. Interpret the provided link or note.
2. Check Gmail only as needed to confirm or enrich the application details.
3. Write Supabase first, because it is the source of truth.
4. Reflect the same record in the existing Google Drive shortlist tracker.
5. Verify both destinations by reading the changed records back.

If the user clearly says they applied, treat that as sufficient evidence to record the application. Gmail confirmation is preferred for enrichment, not required. If neither the link nor Gmail reveals a non-empty company and role title, ask one concise grouped question before writing.

## Destinations

Supabase source of truth:

- Ask the user to select a connected Supabase project and an application table. Never guess a project reference, table, or profile row.
- If no compatible table exists, explain the schema in **Supabase Contract** and ask before creating or migrating anything.
- Use the Supabase connector and respect the project's existing RLS and write-access policy.

Google Drive tracker:

- Ask the user to select an existing spreadsheet and applications tab, or offer to create them.
- Search by the user's description through the connected Drive account; never guess a spreadsheet ID, tab, range, or column layout.
- Confirm the selected sheet contains columns equivalent to `Confirmed date`, `Company`, `Role`, `Evidence source`, `Status / outcome`, and `Notes`.
- Keep resource identifiers in machine-local configuration or connector state, never in the portable skill or repository.

## Supabase Contract

Required fields for `<selected application table>`:

- `profile_id`: look up from `<selected profile table>` by `profile_key = '<selected profile key>'`.
- `company`: non-empty text.
- `role_title`: non-empty text.
- `application_status`: one of `wishlist`, `shortlisted`, `applied`, `application_received`, `interviewing`, `rejected`, `closed_not_progressed`, `position_filled`, `shortlisting_outcome`, `offer`, `withdrawn`.

Useful fields to populate when known:

- `application_date`: date the user applied. Use the user-provided date when given; otherwise use today's date in the user's current timezone.
- `status_date`: date of the latest evidence or status update. Default to `application_date`.
- `application_url`: the job posting, confirmation page, or application link the user provided.
- `evidence_source`: short provenance string, such as `User-provided applied job link` or `Gmail confirmation: <sender or subject>, <date>`.
- `source_channel`: normalized origin such as `linkedin`, `indeed`, `company_site`, `gmail`, or `user_link`.
- `email_thread_id`: Gmail thread or message id when email evidence was used.
- `notes`: concise human-readable context, uncertainties, duplicate notes, or outcome details.
- `metadata`: JSONB for raw links, Gmail message ids, confidence, original posting text, and `source_sheet: "<selected applications tab>"`.

For a fresh application, use `application_status = 'applied'` unless Gmail or another reliable source confirms receipt, in which case use `application_status = 'application_received'`. If the latest evidence is a rejection, interview, offer, withdrawal, filled role, or closed process, record that latest state instead.

## Efficient Workflow

For each batch, process all submitted jobs together:

1. Normalize the input into candidate records: URL, likely company, likely role, application date, and source channel.
2. Open or inspect the job URL only when it is likely to add missing company/role information. If LinkedIn, Indeed, or another site is login-blocked, expired, or noisy, do not spend time fighting the page; fall back to Gmail and the user's text.
3. Search Gmail with targeted queries around the likely company, role, application platform, and application date. Prefer recent confirmation or status emails with subjects like application received, thank you for applying, update on your application, interview, rejection, role filled, or closed.
4. Merge evidence. Keep email snippets short in notes; do not store full email bodies unless the user explicitly asks.
5. Read Supabase for possible duplicates before writing. Match on application URL, email thread id, or the natural key `(profile_id, company, role_title, application_date)`.
6. Insert new rows or update existing rows in `<selected application table>`. Preserve older useful notes and append only genuinely new evidence.
7. Update the selected applications tab sheet from the final Supabase-shaped record. If a matching row exists by company, role, and date, update it; otherwise append. Use batch updates for multiple rows.
8. Read back the Supabase rows and the affected sheet range. Report what was recorded, what was enriched from Gmail, and what remains uncertain.

## Duplicate and Idempotency Rules

Do not create duplicates on retries. Prefer updating an existing record when:

- The same `application_url` is already present.
- The same `email_thread_id` is already present.
- The same `profile_id`, `company`, `role_title`, and `application_date` already exist.
- Gmail reveals that a new user-provided link belongs to an existing application process.

When a duplicate is found, update missing fields, latest status, evidence source, and notes rather than inserting another record. In the Google Sheet, update the matching row instead of appending.

## Uncertainty Rules

Safe defaults:

- Application date: current date in the user's timezone when not specified.
- Evidence source: `User-provided applied job link` when the user says they applied and no email confirmation is found.
- Status: `applied` without email confirmation; `application_received` with a receipt email.

Ask the user one concise question only when required data is missing or multiple materially different interpretations remain after link and Gmail checks, such as two possible roles at the same company on the same day.

Never invent company names, role titles, salaries, or outcomes. Use `notes` or `metadata` for uncertain but useful context.

## Validation

After writing:

- Read the affected `<selected application table>` rows back from Supabase and confirm the row count and key fields.
- Read the affected selected applications tab sheet rows back and confirm they mirror the Supabase record.
- If either destination fails, report the successful destination and the failed one clearly, then leave enough detail for a later retry without duplicating records.

Keep the final response short and useful: list the applications recorded or updated, mention any Gmail evidence used, and flag only the uncertainties the user needs to resolve.
