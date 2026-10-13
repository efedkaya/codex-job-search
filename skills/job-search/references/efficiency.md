# Focused searches and shared vacancy state

Use this reference for bounded searches, repeat runs, delegated work or the optional vacancy helper. It complements source coverage in [search-state.md](search-state.md) and application history in [tracking.md](tracking.md); these are separate records.

## Choose a mode and a stopping condition

| Mode | Use | Work and completion rule |
|---|---|---|
| Update | Established scopes with prior successful scans | First recover pending/unreported work, then check new or materially changed findings in the inclusive date window. Reuse current assessments and verification. A source finishes only when its requested coverage is observed. |
| Targeted | A bounded shortlist or short search session | Agree or infer a practical budget. About 25 unique promising/uncertain vacancies reviewed and up to eight final recommendations is a starting point, not a required quota. Stop when useful choices or the budget are reached; disclose unscanned pages. |
| Full audit | An explicit all-pages/complete first scan of defined sources and filters | Enumerate every reachable scoped page/batch with no age cutoff unless requested. Review depth can be bounded separately. Neither 25 reviews nor eight recommendations completes an unfinished scan. Save continuation when interrupted. |

For an initial request to search all reachable results, use Full audit. Do not silently downgrade it to Targeted. An ordinary shortlist need not trigger an exhaustive scan. Keep the user's roles, location, sources and time constraints explicit; none of these modes guarantees every vacancy in the market.

Track discovery coverage, detailed reviews and reported recommendations separately. A budget may limit elapsed time, source scopes, tool calls or detailed reviews; configure it to the request and available tools. If enumeration stops early, record partial/blocked/failed and keep that scope's successful watermark unchanged. If enumeration finishes but assessment does not, record complete coverage with pending assessments still in the ledger. Successful fallback coverage never advances a blocked board's watermark.

Group queries by role family and close title variants. Reserve a small exploration slice for adjacent duties, then expand only if results warrant it. Screen known hard eligibility conflicts before detailed fit work. Unknown language, work rights, tool capability or commute stays unknown; use possible/deferred rather than rejected solely for missing evidence. Keep skills fit, eligibility and application readiness separate.

## Reduce repeated reading

Read the profile/evidence once, then optionally write a private compact profile brief containing profile revision, hard constraints, preferences, role families, relevant claim IDs and capability levels, key unknowns and file pointers. This is a derived working aid, not a replacement for the sources. Refresh it after material corrections. Do not copy a whole CV, transcript, chat history or evidence archive into every worker prompt.

For browser work, request current result cards and pagination/filter state, or the relevant posting sections. Avoid repeated full-page dumps and long snapshots after every action. A full snapshot or screenshot remains appropriate when required by the tool or needed to resolve layout/loading ambiguity. Accumulate stable IDs while progressively scrolling virtualized lists; a final bottom snapshot or End key is not evidence of the intervening cards. Follow the host browser's documented operations.

Use compact helper reads: current-batch membership for search state, filtered/paginated ledger lists and `get` only for a selected vacancy. Save observations once and reuse them. Do not reopen an unchanged vacancy already checked by another worker without a stale cache, material change, contradictory source, unresolved decision or application recheck that needs it.

## Delegate distinct work

Delegate only when independent work is likely to help. Give each worker a specific source/query or employer set, budget, profile revision/brief, shared private workspace, output fields and stopping condition. Assign browser tabs or source scopes explicitly; workers must not navigate the same tab or scan the same scope concurrently.

The coordinator assigns each canonical vacancy a verification owner before detailed work. Discovery workers can add aliases and return IDs; one owner verifies/assesses each vacancy and shares the result. Reconcile overlap through the ledger before opening postings, and hand off rather than duplicate an active verification. The ledger lock protects writes, not browser ownership or task assignment. Keep worker returns to compact findings, canonical IDs, decisions, uncertainty, coverage and resume evidence. Expand source excerpts only when needed to resolve a decision.

## The optional vacancy ledger

`scripts/vacancies.py` is an offline Python 3.10+ standard-library helper. It stores private `vacancies.json` with schema version 1 and uses `.vacancies.lock` plus atomic writes. It makes no network requests and does not infer vacancy identity, assess candidates, prove verification or operate a browser. Invalid writes preserve the existing ledger. Do not remove a lock while a writer is active or discard damaged state to proceed.

Keep the explicit absolute private workspace outside the skill and public repository. Resolve SCRIPT to this skill's `scripts/vacancies.py` and PRIVATE to that workspace; replace the explanatory placeholders below with appropriately quoted paths. Use python3 or py if that is the host's interpreter name. Write UTF-8 JSON input files with file tools, never interpolate posting text into shell commands.

~~~text
python SCRIPT --workspace PRIVATE upsert --input VACANCY_JSON
python SCRIPT --workspace PRIVATE upsert-batch --input BATCH_JSON
python SCRIPT --workspace PRIVATE pending --profile-revision PROFILE_REVISION --limit 20
python SCRIPT --workspace PRIVATE list --unreported --profile-revision PROFILE_REVISION --limit 20
python SCRIPT --workspace PRIVATE get --id VACANCY_ID --profile-revision PROFILE_REVISION
python SCRIPT --workspace PRIVATE verification --id VACANCY_ID --max-age-hours 24
python SCRIPT --workspace PRIVATE assess --input ASSESSMENT_JSON
python SCRIPT --workspace PRIVATE verify --input VERIFICATION_JSON
python SCRIPT --workspace PRIVATE report --input REPORT_JSON
python SCRIPT --workspace PRIVATE summary --profile-revision PROFILE_REVISION
~~~

`upsert-batch` takes `{"vacancies": [UPSERT_OBJECT, ...]}` with 1–100 upsert objects and records a page/batch with one lock/write. It returns received/created/changed counts plus compact records; any invalid item leaves the batch unapplied. Use this before checkpointing a result batch.

`list` and `pending` return compact pages, with `--limit` 1–100 (default 20), `--offset`, and optional `--source`, `--employer`, `--query`, `--profile-revision` and `--unreported`. `get` explicitly returns the full selected record. Pass the current candidate profile revision on assessment/reporting reads so an old profile's decision is not reused silently. Read-only commands do not initialize state.

### Identity and discovery

Minimal fictional upsert:

~~~json
{
  "employer": "Example Company",
  "title": "Research Coordinator",
  "summary": "Coordinates market research projects.",
  "discovered_at": "2026-10-13T12:00:00+00:00",
  "provenance": "Fictional board result; source ID shown on the card. Posting date unknown.",
  "aliases": [{"source": "example-board", "posting_id": "EX-42"}]
}
~~~

Required: employer, title, summary, discovered_at and nonempty provenance text, plus at least one identity: aliases, requisition_id or official_url. Optional details is an object whose supported text fields are location, work_arrangement, salary, deadline, requirements and description. Omit unknown optional fields. Use a compact stable factual summary; do not rewrite it merely because another board uses different promotional wording. A newer capture date does not make board text more authoritative than an employer posting. Resolve conflicting material facts before upsert, preserve the evidence pointer/uncertainty and avoid replacing verified requirements with a weaker snippet. Store observation dates, raw relative date labels, source scope IDs and source uncertainty in provenance; do not invent exact posting dates or alter substantive details only to refresh a checked time.

Identity is explicit source+posting ID, normalized employer+exact requisition ID, or a verified official HTTP(S) posting URL. Known tracking parameters are stripped; meaningful identifiers remain. Attach cross-board aliases only when evidence establishes the same vacancy. Company/title similarity is insufficient. Separate requisitions remain separate. An unambiguous new alias joins an existing record; identities that match multiple existing records fail for review rather than auto-merge. Flag that unresolved duplicate group, share authoritative verification within it where justified, and avoid redundant deep reviews. Disclose unresolved reconciliation; do not hand-edit the ledger or force a guessed alias. An alias-only discovery may precede an official URL; `official_url` is not a place to disguise an unverified aggregator as the employer source.

An update preserves omitted optional details/identity, and adds explicit aliases. Changed title, summary, details or canonical identity increments the material revision; mere alias/provenance/discovery-time updates do not. New or materially changed records are pending assessment. The returned vacancy_id and revision must be used in dependent writes. The helper keeps current records, not a full source-snapshot archive; preserve any required posting evidence in the candidate's private sources directory.

### Assessment, verification and reporting

Each input below requires vacancy_id and expected_revision. A stale revision is rejected: reread the vacancy and reconcile changed facts before writing again. Older discovery cannot change newer material facts, and older assessment/verification/reporting cannot replace newer observations. Timestamps must be ISO 8601 with an explicit time zone.

| Command | Additional required fields |
|---|---|
| assess | status: recommended / possible / rejected / deferred; reason; skills_fit: strong / partial / weak / unknown; eligibility: eligible / ineligible / unknown; readiness: ready / needs_work / blocked / unknown; profile_revision; assessed_at; provenance |
| verify | status: verified_open / verified_closed / unavailable / blocked / unverified; checked_at; source_url; provenance |
| report | profile_revision; reported_at; report_ref describing where the decision was actually shown |

A recommended record usually maps to apply, possible/deferred to investigate, and rejected to skip; keep the reasons and unresolved facts visible. An alias or search snippet does not establish `verified_open`. A blocked retrieval is not closure. `report` requires a current assessment for the stated profile and must follow the actual report, not a plan to show it. A crash or interrupted scan leaves unreported work discoverable even if its source IDs are already seen.

Material vacancy changes invalidate the current assessment, reporting state and verification cache by revision. A candidate profile revision change makes an old assessment/report stale for that profile, even if the posting is unchanged; it does not invalidate independent source verification. Always pass the current profile revision when reading pending work. There is no automatic destructive migration from discoveries.json, tracker.json or search_state.json. Preserve legacy files and recover pending/unreported legacy discoveries through supported validated inputs when needed; never equate legacy seen IDs with completed assessment.

### Verification cache

`verification --id VACANCY_ID --max-age-hours N` returns the cached status, its age and `reusable`. Optional `--at` accepts an aware ISO timestamp for reproducible checks. Reuse is true only for verified_open/verified_closed at the current material revision with age between zero and N. The 24-hour example is a configurable research window, not a claim that job availability remains unchanged for a day.

Choose freshness for the action. A fresh shared check may support search comparison; recheck the specific posting before tailoring an application and before a consequential external action. A deadline near expiry, contradiction or changed content warrants a fresh check regardless of age. Blocked, unavailable, unverified, stale, future-dated and older-revision checks are never reusable confirmations. Report the actual successful checked time, not the time the cache was read. The helper validates structure and cache age; it cannot certify the source evidence.

## Measure actual work, not promised savings

If usage information is available, record elapsed agent time, browser/tool calls, unique observed vacancies, duplicates reused, detailed reviews, verified postings, recommendations and coverage status. Keep candidate active time separate. Record tokens or cost only when the host exposes attributable actual usage and its basis; otherwise mark unavailable. Do not estimate token savings from text length or invent costs, speedups or hiring benefits.

A comparison is meaningful only with comparable scopes, access conditions, budgets and output quality. State whether a run was a fixture test or live search, and whether usage includes parallel workers or retries. Do not change model, speed/effort, account limits, subscriptions or host settings as an optimization. Any claimed benefit must come from observed measurements, not the existence of this workflow.
