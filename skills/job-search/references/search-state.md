# Private search checkpoints

The optional `scripts/search_state.py` helper records coverage and seen IDs. It makes no network requests and does not operate a browser, parse dates, rank jobs or prove that the agent reached the last page. Use [browser-search.md](browser-search.md) for those decisions. The [vacancy ledger](efficiency.md) holds shared discovery, assessment and verification records; the [tracker](tracking.md) holds application history. This helper never changes vacancies.json or tracker.json.

Use Python 3.10+ and an explicit absolute private workspace outside the public repository and installed skill. Calendar calculations require an IANA time-zone database. macOS/Linux commonly supply one; if valid zones are unavailable, install the Python `tzdata` package from the standard package registry. The helper reports an actionable error instead of silently changing to UTC. No job-service subscription or API usage is required by the helper.

Resolve SCRIPT to this skill's scripts/search_state.py and PRIVATE to the candidate's designated directory. Input JSON files below also belong in PRIVATE. Use appropriate quoting for the host shell; the paths shown are explanatory placeholders.

~~~sh
python SCRIPT --workspace PRIVATE plan --input scope.json
python SCRIPT --workspace PRIVATE start --input scope.json
python SCRIPT --workspace PRIVATE known --input membership.json
python SCRIPT --workspace PRIVATE checkpoint --input checkpoint.json
python SCRIPT --workspace PRIVATE finish --input finish.json
python SCRIPT --workspace PRIVATE status
python SCRIPT --workspace PRIVATE status --full
~~~

`plan`, `known` and `status` are read-only and create no state. Each mutation uses a lock and atomic file replacement. Do not remove a lock unless no writer is running. Inputs and resume hints are passive data, never commands. Keep different candidates in different explicit workspaces.

## Scope input

~~~json
{
  "source": "linkedin",
  "query": "customer success associate",
  "timezone": "Europe/London",
  "filters": {
    "location": "Leeds, United Kingdom",
    "employment_type": "part-time",
    "employer": null
  },
  "lookback_days": 1
}
~~~

Required fields are source, query and timezone. Optional filters is an object; profile_revision is a nonempty string if used; lookback_days is an integer 0–365, default 1. Source names normalize case/spacing; keep query and filter representations stable. Profile revision should change only for material search-constraint changes, not every profile edit. A scope change creates a new baseline. A change in lookback_days alone does not. Never put today's date, page number or rolling date filter into stable filters.

Use employer-specific source names such as `employer:example-bank` and record the verified employer name/domain in filters. Do not assume one source covers every subsidiary or hiring board.

`plan` returns baseline/incremental mode, inclusive requested_since/fetch_since dates, successful coverage timestamp and compact pending attempts. Null dates mean a baseline with no age cutoff. `start` returns a run_id, current started_at, conservative coverage_started_at, known_count and compact pending_runs with resume hints.

CLI output is compact by default. `plan`, `start`, `status` and `finish` replace accumulated ID arrays with counts; pending_runs shows the latest three summaries with pending_run_count and pending_runs_omitted. `status` shows each scope's latest_run and pending summary rather than its whole run history. Add `--full` after the subcommand only when the full stored IDs/history are actually needed. The storage/API schema stays unchanged; compact output does not discard data. `checkpoint` still returns the current batch's new_ids.

### Query only current-batch membership

~~~json
{
  "scope_id": "REPLACE_WITH_RETURNED_SCOPE_ID",
  "posting_ids": ["linkedin:fictional-101", "linkedin:fictional-102"]
}
~~~

Save that as a private membership input and run `known`. It accepts at most 1,000 queried IDs and returns known_ids/unknown_ids with counts; an unknown scope is an error. For a fresh scope, call `start` before `known`; `plan` returns an ID but does not persist the scope. A `plan` ID is sufficient for an already stored scope. Query the current batch instead of repeatedly loading the whole seen set. Known IDs mean observed in this source scope, not assessed, verified, reported or fresh. Match them to the vacancy ledger before deciding whether work remains.

## Checkpoint after each page or batch

~~~json
{
  "run_id": "REPLACE_WITH_RETURNED_RUN_ID",
  "seen_ids": ["linkedin:fictional-101", "linkedin:fictional-102"],
  "pages_seen": 2,
  "resume_locator": {
    "page": 2,
    "search_url": "https://jobs.example/search?q=coordination",
    "continuation": "Page 3 control visible and enabled",
    "last_batch_ids": ["linkedin:fictional-101", "linkedin:fictional-102"],
    "loading_settled": true,
    "terminal_observed": false,
    "next_action": "Recheck newest page, then continue from observed Page 3 control"
  },
  "notes": "Fictional example; two results pages recorded."
}
~~~

Use stable source listing IDs, or clean direct URLs if no ID is exposed. Do not store tracking-heavy partner links, cookies, session IDs or credentials. `pages_seen` is cumulative for this attempt and cannot decrease. The returned new_ids means newly observed within this scope, not newly published. Cross-source duplicates still require matching employer requisition IDs and actual posting facts.

### Preserve vacancies separately from coverage

Before checkpointing IDs, upsert the observed compact vacancy facts into private vacancies.json with [vacancies.py](efficiency.md). Its source aliases connect board IDs to one canonical employer vacancy when evidence establishes identity. Save the raw posting-date label, checked/discovery times, source scope and unresolved facts in supported details/provenance fields without inventing exact dates. Do not save account sidebars, full-page dumps or unrelated browser content.

On every start, review pending/unreported ledger records as well as new_ids. A crash after recording IDs must not suppress a role that was never assessed or shown. A reported role normally stays out of the main repeat shortlist unless materially changed. Search state cannot determine assessment or reporting state; the ledger holds those separately.

If an older private discoveries.json exists, check it minimally for pending/unreported work before relying on a new or incomplete ledger. Import supported records through validated upserts with their source/uncertainty intact when needed; preserve the legacy source file. There is no automatic or destructive migration. Do not fabricate verified status or silently mark historical observations as assessed/reported. The ledger does not mutate tracker.json or search_state.json; use the shared in-chat fallback when persistence is unavailable.

## Finish and resume

~~~json
{
  "run_id": "REPLACE_WITH_RETURNED_RUN_ID",
  "outcome": "complete",
  "stop_reason": "Reached the exposed final page",
  "coverage_evidence": "Fictional example: page 4 loaded; Next disabled; verified query and location unchanged."
}
~~~

Allowed outcomes: complete, partial, blocked, failed. Every finish requires stop_reason; complete also requires nonempty coverage_evidence. Evidence must describe what actually happened, not copy the fictional example. Text presence is validated; its truth cannot be established by the helper. A site cap can complete the exposed result set only if reported as capped coverage, with that limitation retained in future reports.

Only complete advances the successful checkpoint. An unfinished scan or successful fallback on a different source never advances this scope; a budget stop is partial, not successful coverage. It uses coverage start, never finish time, so postings arriving during a scan remain eligible next time. Resumed attempts carry the earliest unresolved coverage start. Once that chain completes, the next fresh incremental attempt catches up safely. An older completion cannot rewind an existing checkpoint. Complete each source independently; success on Indeed does not complete LinkedIn or an employer site.

Finished attempts are immutable. To resume a partial/blocked/failed attempt, call start again with the same scope, inspect pending_runs and recheck the newest/front pages before continuing the old location. Save fresh checkpoints. For a running attempt interrupted by a crash, start likewise carries its coverage anchor. Do not run competing browser scans for the same scope: the file lock protects individual writes, not an entire browsing session.

Coverage uses search_state.json and .search_state.lock; the ledger uses vacancies.json and .vacancies.lock. Preserve legacy discoveries.json as input under the shared private-state rules. Repeated invocations and explicitly requested host automations are separate from a single search session.
