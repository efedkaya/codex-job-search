# Private records and time budgets

Use the helper only when a persistent tracker helps the user's request. It is an offline record keeper, not a search engine, scraper, mail client or application submitter. With no Python or filesystem access, provide a table in chat and say that no persistent tracker was updated.

## Working tracker and reconciliation

Reuse the candidate's chosen workbook or other working view and save its location in their private profile. Do not create a second tracker just because a new session starts. Before an update, read the latest file and relevant event history; preserve user-entered notes, dates, custom columns, filters, formulas, validation and links. Do not regenerate it from an older builder or export. Back up material edits and verify the saved result using available spreadsheet tools when applicable.

Give each kind of record a clear owner:

| Record | Owns |
|---|---|
| Profile/evidence | Candidate facts, constraints, submission mode and document preferences |
| Vacancy/queue | Posting identity, observed source checks, fit and current application priority |
| Attempt/event history | What happened, when, who reported or observed it, and which attempt it concerns |
| Working tracker | The candidate's current view, next actions and manually maintained notes |
| Material catalogue and retained files | Stable résumé/letter version IDs and their exact files; see [materials](applications.md#reuse-and-version-materials) |

These may share a file; do not create every optional record by default. When several exist, save pointers and identity mappings rather than inventing competing sources of truth. Keep a stable job ID and attempt ID separate from queue rank and spreadsheet row position. Existing short row references can map to canonical IDs in a private sidecar. A prepared-only row can retain a preparation ID until an actual attempt is created; it must not inflate submitted counts.

After a material event, reconcile the affected records as one completion checkpoint:

1. Resolve the exact job/attempt and inspect its latest events. Repeated reports of the same completed send do not create a new attempt or duplicate submission event. Preserve history; later notes do not erase earlier draft states.
2. Record the fact once with its date and provenance: observed confirmation or the candidate's direct report. A reported email send is a submitted application, not proof of employer delivery, receipt or an unchanged attachment. An intended future send remains planned.
3. Update the matching working row and queue application status, document IDs, next action and confirmation source. If a new authoritative posting or candidate fact resolves an old condition, update the current recommendation/gap labels as well; preserve the earlier observation in history. Do not erase a candidate's conflicting edit: reconcile from available evidence or surface the specific unresolved conflict.
4. Check that confirmed submission counts, current statuses and material references agree. Discovery totals, prepared files and applied dates without submission evidence must not substitute for confirmed events. Keep historical submission counts separate from current outcome status, and remove obsolete active draft actions after a send. Report any view that could not be updated instead of claiming synchronisation.

For Excel, useful fields are company/role and stable reference, source posting, application route, status and dates, résumé/letter IDs, next action, optional follow-up/interview dates, evidence source and notes. Discovery source and application route are different: a role found on a board may be applied to by employer email. Leave unknown fields blank. Use simple filters/dropdowns and formula totals when helpful; no extra dashboard is required. Keep linked PDFs with the workbook or use verified reachable paths, and preserve portable relative links when moving the package. A due follow-up is a planning cue, not permission to send or schedule one.

## Invocation

Python 3.10+; standard library only. Resolve the script from this skill's installation directory. Every call requires an explicit absolute private workspace outside the public repository and skill. Save input JSON in that private workspace; never interpolate posting text into shell commands. Use a file tool to write JSON and pass its path as a properly quoted argument.

~~~text
python <skill-directory>/scripts/track.py --workspace <absolute-private-directory> init
python <skill-directory>/scripts/track.py --workspace <absolute-private-directory> upsert-job --input <job-json-path>
python <skill-directory>/scripts/track.py --workspace <absolute-private-directory> record-application --input <application-json-path>
python <skill-directory>/scripts/track.py --workspace <absolute-private-directory> record-event --input <event-json-path>
python <skill-directory>/scripts/track.py --workspace <absolute-private-directory> log-time --input <time-json-path>
python <skill-directory>/scripts/track.py --workspace <absolute-private-directory> list
python <skill-directory>/scripts/track.py --workspace <absolute-private-directory> summary --budget-hours 24
python <skill-directory>/scripts/track.py --workspace <absolute-private-directory> export --output <new-csv-path>
~~~

Replace angle-bracket arguments with actual paths. On systems using python3 or py, use that interpreter. The 24-hour value is an example, not a global default. Copy returned job/application IDs into dependent inputs instead of guessing them.

## Inputs

**upsert-job:** required text fields employer, title, posting_url, checked_on (YYYY-MM-DD). Optional text: requisition_id, deadline (YYYY-MM-DD), location, work_arrangement, salary, notes. Omit unknown optional fields rather than supplying null. Use notes for source context, recommendation and unresolved facts; keep fuller assessments in private files associated with the job ID.

- status: open / closed / unverified (default unverified).
- retrieval_status: verified / blocked / unavailable (default verified). Here verified means the retrieval was checked; it does not certify the employer or candidate fit.
- closed requires closure_confirmed: true and closure_evidence text. A verified closed banner or explicit past deadline can support closure; an access failure cannot.
- Reopening an existing closed job requires status: open, reopen_confirmed: true and reopen_evidence text.
- An inaccessible recheck preserves the last known open/closed status and records the new retrieval_status. **Present current availability as unverified when retrieval is blocked/unavailable**, even if stored status says open. Do not present the latest attempted checked_on date as proof of a fresh successful verification. Prior observations remain in history.

Job identity uses employer plus requisition ID when supplied, otherwise the canonical posting URL. Known tracking parameters are removed; meaningful query identifiers and fragments remain. Employer aliases and cross-board duplicates may need reconciliation. If requisition and compatible URL identify different existing records, the helper rejects the update unchanged; resolve the conflict rather than retrying with a guessed identity or hand-editing application links. Use a verified canonical employer name consistently. Distinct explicit requisitions remain separate, even when they share a posting URL.

**record-application:** job_id and created_on required; optional resume_version and notes. Each call creates a new draft attempt. Do not retry blindly after an ambiguous response: inspect tracker.json for the created attempt first. Creating a draft does not imply submission, and jobs and application attempts have different IDs. Store source snapshots and exact document versions under applications/<application-id>/.

**record-event:** application_id, type and occurred_on required; optional confirmed (boolean), evidence and notes. Types: prepared, submitted, followup_planned, followup_sent, interview_scheduled, interview_completed, offer_received, accepted, rejected, withdrawn, note. Actual outcomes and sends require confirmed: true plus evidence, and cannot be future-dated. Evidence can be an observed confirmation or the user's explicit report of a completed action. The helper cannot independently validate the truth of that report; the agent must not manufacture confirmation.

For interview_scheduled, occurred_on is when scheduling was confirmed; put the future interview date/time in notes. For a planned follow-up, use followup_planned with no confirmed flag. Never turn “I will send it tomorrow” into followup_sent. Chronological corrections must not overwrite historical facts; add a note and preserve originals. Terminal outcomes cannot silently regress; a genuine new application gets a new attempt ID. A mistaken event needs a reviewed correction, not a fabricated new application.

**log-time:** date, nonnegative integer human_minutes and category required. Categories: setup / search / application / networking / interview / other. Optional agent_minutes (nonnegative integer), basis (reported / measured / estimated; default reported) and notes. Every time log represents completed work: basis describes how its duration is known, not whether it is planned. The helper rejects future dates for all bases using the computer's local calendar date (the same basis as confirmed application events). Explicitly mark estimated durations; keep future plans outside completed-work logs. If the candidate's day differs from the computer's, retain their reported date and resolve the mismatch before logging rather than changing it to bypass validation.

## Interpreting budgets

The summary totals all logged human minutes, breaks them down by basis, and reports agent minutes separately. Agent time does not reduce the candidate's human-time budget. If estimates are included, describe remaining time as estimated, not measured. Do not log the same session twice when replacing an estimate with a report; reconcile the private log with the user first. There is no automatic stopwatch or token-cost meter.

`summary` reports current statuses, not historical funnel conversion. Use the dated events and the [outcome review rules](applications.md#review-outcomes-without-inventing-causes) for stage-reach/cohort analysis; no new analytics command is bundled. Optional discovery-source, application-route or role-family annotations belong in private attempt notes/sidecar records keyed by application ID. Do not pass unsupported fields to the helper, infer missing categories from URLs, or add new event types outside the documented schema. A known scheduled interview or offer can exist without a separately logged submission; disclose incomplete history when calculating rates.

One optional eight-week, 24-hour allocation is: setup 2h, shortlist review 4h, applications 10h, networking 3h, interview preparation 3h, reserve 2h. Customize it to the candidate and revise priorities when interviews arrive. Preserve any separately budgeted learning time. No application or interview count is guaranteed.

## Storage behavior and limits

tracker.json holds jobs, applications, events and time_logs, with schema version 1. Writes use a lock and atomic replacement; invalid inputs leave existing records unchanged. init is idempotent and does not reset damaged data. A stale lock is an explicit error: confirm no other command is running before removing it. Do not silently repair or discard a corrupted tracker; preserve it and report the issue.

The CSV export contains job rows, not the complete event history. It quotes fields, uses UTF-8 with a BOM, and prefixes formula-looking text to reduce spreadsheet formula injection. Export refuses an existing destination. The JSON remains the full record; keep backups appropriate to the user's storage system. These safeguards do not encrypt files or guarantee secrecy from other processes or cloud sync.
