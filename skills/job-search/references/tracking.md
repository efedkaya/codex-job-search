# Private records and time budgets

Use the helper only when a persistent tracker helps the user's request. It is an offline record keeper, not a search engine, scraper, mail client or application submitter. With no Python or filesystem access, provide a table in chat and say that no persistent tracker was updated.

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

Job identity uses employer plus requisition ID when supplied, otherwise the canonical posting URL. Known tracking parameters are removed; meaningful query identifiers and fragments remain. Employer aliases and cross-board duplicates may need human review. Use a verified canonical employer name consistently, without merging unrelated companies. Different requisitions with the same title remain distinct.

**record-application:** job_id and created_on required; optional resume_version and notes. Each call creates a new draft attempt. Do not retry blindly after an ambiguous response: inspect tracker.json for the created attempt first. Creating a draft does not imply submission, and jobs and application attempts have different IDs. Store source snapshots and exact document versions under applications/<application-id>/.

**record-event:** application_id, type and occurred_on required; optional confirmed (boolean), evidence and notes. Types: prepared, submitted, followup_planned, followup_sent, interview_scheduled, interview_completed, offer_received, accepted, rejected, withdrawn, note. Actual outcomes and sends require confirmed: true plus evidence, and cannot be future-dated. Evidence can be an observed confirmation or the user's explicit report of a completed action. The helper cannot independently validate the truth of that report; the agent must not manufacture confirmation.

For interview_scheduled, occurred_on is when scheduling was confirmed; put the future interview date/time in notes. For a planned follow-up, use followup_planned with no confirmed flag. Never turn “I will send it tomorrow” into followup_sent. Chronological corrections must not overwrite historical facts; add a note and preserve originals. Terminal outcomes cannot silently regress; a genuine new application gets a new attempt ID. A mistaken event needs a reviewed correction, not a fabricated new application.

**log-time:** date, nonnegative integer human_minutes and category required. Categories: setup / search / application / networking / interview / other. Optional agent_minutes (nonnegative integer), basis (reported / measured / estimated; default reported) and notes. Explicitly mark estimates; never call an inferred duration reported. Do not log future planned sessions as completed work.

## Interpreting budgets

The summary totals all logged human minutes, breaks them down by basis, and reports agent minutes separately. Agent time does not reduce the candidate's human-time budget. If estimates are included, describe remaining time as estimated, not measured. Do not log the same session twice when replacing an estimate with a report; reconcile the private log with the user first. There is no automatic stopwatch or token-cost meter.

One optional eight-week, 24-hour allocation is: setup 2h, shortlist review 4h, applications 10h, networking 3h, interview preparation 3h, reserve 2h. Customize it to the candidate and revise priorities when interviews arrive. Preserve any separately budgeted learning time. No application or interview count is guaranteed.

## Storage behavior and limits

tracker.json holds jobs, applications, events and time_logs, with schema version 1. Writes use a lock and atomic replacement; invalid inputs leave existing records unchanged. init is idempotent and does not reset damaged data. A stale lock is an explicit error: confirm no other command is running before removing it. Do not silently repair or discard a corrupted tracker; preserve it and report the issue.

The CSV export contains job rows, not the complete event history. It quotes fields, uses UTF-8 with a BOM, and prefixes formula-looking text to reduce spreadsheet formula injection. Export refuses an existing destination. The JSON remains the full record; keep backups appropriate to the user's storage system. These safeguards do not encrypt files or guarantee secrecy from other processes or cloud sync.
