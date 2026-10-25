# Validation and limits

## 0.6.0 update — 25 October 2026

This release selectively merges a supplied skill revision into the existing installed and sharing editions. New [writing craft](skills/job-search/references/documents.md), [message guidance](skills/job-search/references/messages.md), [mock interviews](skills/job-search/references/mock-interviews.md) and [Ontario posting observations](skills/job-search/references/ontario-postings.md) complement the retained final-document checker, source-import diagnostics, reply interpretation and shared setup.

- **89 offline unit tests passed locally** on macOS/Python 3.12.14. No helper executable code changed. Public distribution/privacy checks pass for **54 allowlisted files**, and **167 internal file/heading links** were checked, together with JSON and Python syntax. The public and installed skill scaffold validators passed.
- Five independent fictional requests were completed using only the staged skill and supplied records: unknown language versus an explicit driving exclusion, qualitative interview evidence omitted from a résumé, a focused edit and broken-scheduler draft, a requested counteroffer, and Ontario rounds spaced apart. Actual responses were inspected separately from the unit tests; these cases bring the behavior fixture to 21 cases, not 21 automatically executed tests.
- The responses preserved unknowns, personal contribution, the private pay minimum and the candidate's final action boundary. Date arithmetic was checked for the notification example. The draft-email case included a nonblocking recipient-address question imposed by the host's writing format; no address was invented and the full requested draft was delivered. The local skill did not impose that question.
- Four new guides and the shared behavioral changes were applied to both editions while preserving their existing setup differences. Existing executable helpers, final-file checks, confirmed-event reply rules and pinned notices were retained. The ZIP and an isolated install were compared with the explicit public manifest before publication.

The Ontario note uses dated official guidance with coverage and interview definitions, pay exceptions and separated-round timing. Current facts were checked against accessible indexed official sources; direct page retrieval was blocked in this environment. The independent exercise did not browse or establish an actual employer's compliance.

Hosted workflow results belong to the published commit's Actions run. These local checks do not establish discovery in every host, complete live board coverage, general ATS acceptance, real application/delivery outcomes or hiring improvement. No real accounts, candidate records or applications were used in the fictional tests.

## 0.5.0 update — 25 October 2026

This release merges the ten-repository workflow review into the shared edition while retaining first-use setup, the 241-company priority seed, private context/answer reuse and candidate-controlled final submission. It adds evidence selection and scoped writing, concrete final-document checks, source-import diagnostics, focused interview drills and next-action/reply interpretation. Source revisions and retained notices are in [adaptation provenance](skills/job-search/references/third-party-notices.md).

- **89 offline unit tests passed locally** on macOS/Python 3.12.14: the existing 68 tests plus 21 material-checker tests. A real fictional PDF was checked with an already installed parser; absent-parser behavior is separately tested. On hosts without a PDF extractor, that optional integration test is explicitly skipped.
- The skill frontmatter/scaffold validator and **50-file public distribution check** passed. **139 internal file/heading links** and the JSON files were checked. An identifying-term scan and a separate review of newly included content found no private candidate material or machine-specific paths.
- The material checker covers wrong/missing text, placeholders, Unicode and technical-term boundaries, changed attachment hashes, text order, byte/page limits when measurable, DOCX split runs/headers and answer limits. A sentence-ending-punctuation false negative was found in independent testing, corrected and covered by regression tests.
- Four additional fictional cases cover evidence-limited application writing, focused typed interview coaching, a partial import with defaults/errors/caps, and mixed-stage next actions. Independently produced responses were inspected against the supplied facts. These cases now appear in the behavior fixture; they are not counted as unit tests. The prior sharing-edition first-use trial remains dated evidence below.
- The release ZIP and isolated installation are checked against the explicit manifest before publication. Existing stateful programs and their previous tests are retained. Public source files contain only reusable guidance, notices, tools and fictional examples.

The hosted workflow runs the package checks on Linux, macOS and Windows with Python 3.10/3.13. Actual results for the published commit belong to its Actions run; the local results above do not claim a hosted result in advance. These checks do not establish universal ATS compatibility, native discovery in every host, live board coverage, external account persistence, application success or improved hiring outcomes. The ten upstream apps/test suites were not installed or run.

## 0.4.0 update — 25 October 2026

This update synchronizes the later shared skill workflows: personal setup and context snapshots, a scoped answer bank, selected-job draft preparation, company priorities/coverage, profiles, interviews and offers. The bundled company seed has 241 distinct names from 173 global-list and 74 Canadian-list rows with 6 overlaps. It contains public company labels only, with no personal profiles, answers, search outcomes or application files.

Local checks were run on macOS with Python 3.12.14. Fictional behavioral checks and offline tests do not establish native installation on another person's device, permanent ChatGPT memory, live board coverage, successful applications or improved hiring outcomes.

- **68 offline unit tests passed:** 29 tracker (including 13 later regressions), 16 search-state, 13 vacancy-ledger and 10 distribution tests.
- The skill frontmatter/scaffold validator passed.
- The public distribution check passed for **46 allowlisted files**; **125 local reference links/anchors** and JSON files were checked.
- The company seed contains **241 names**, with source memberships of 173 and 74 and 6 shared names. Candidate data and creator-specific paths/defaults were checked separately and excluded.
- Private-state distribution regressions cover the answer bank, context snapshot, company/search records and evidence/identity pointers in addition to existing tracker protections.
- Release ZIP and isolated install contents are compared with the public manifest before publication. Remote CI, native installation on friends' machines, live searches and persistent account memory are separate from these offline checks.

An independent fictional first-use/answer-reuse trial on the synchronized sharing edition adapted to a Halifax hospitality candidate and retained unanswered screening details. It identified a seed-resource path ambiguity, which was corrected: template paths are explicitly relative to the skill root, and setup resolves an accessible source pointer. The trial did not browse, submit, alter accounts or modify candidate data.

The installed-source tracker regression suite is included in the repository tests. Distribution guards now also exclude reusable-answer files, context snapshots and candidate-specific company/search registers. Historical checks below remain dated evidence, not current live guarantees.

## Historical 0.3.2 validation

# Validation scope

Release: 0.3.2 public preview. Checked on 13 October 2026 with Python 3.12.14 on macOS. This is a tested initial version, not a claim of universal job-board compatibility or production reliability.

## Checks completed for 0.3.2

- **55 offline unit tests passed:** 16 tracker, 16 search-state, 13 vacancy-ledger and 10 distribution tests.
- An independent publication review found and fixed two state-preservation defects. The tracker now rejects serialized UTF-8 data above its reader's 10 MB limit before replacing the previous file. Search checkpoints reject cumulative scopes above 100,000 posting IDs before changing memory or disk. Regressions cover preserved, reopenable files, multibyte text, multiple runs, the exact ID limit and known-ID reuse.
- The public manifest contains 31 explicitly allowlisted files, including sanitized bug-report and trial-feedback templates. The distribution checker passed. No other blocking privacy, licensing-notice or functionality-claim issue was found in the bounded independent review; this was not a full upstream code-provenance audit.
- The installation and first-use instructions remain those checked for 0.3.1 below. Hosted CI results, when available, are visible in the repository's Actions tab; the local test result above does not establish Windows or Linux execution.

Prior results below describe the stated release and date, not newly repeated live searches.

## Checks completed for 0.3.1

This release adds first-use intake instructions, an extended blank profile, a beginner setup guide and a manual feedback template. The Python helpers and their unit tests are unchanged from 0.3.0; its 53-test result below is retained as the last code-suite result, not counted as a new execution for this documentation update.

An independent agent used the updated instructions for three fictional requests before reading any expected outputs: a new user with no attachments, a new user with substantial background already supplied, and a returning user changing to part-time work. It asked a short first round with optional documents, skipped known facts, distinguished assisted spreadsheet work, retained material unknowns and reused the returning profile while revising affected assessments. These were offline behavior checks, not live searches or automated unit tests.

The skill validator, JSON parsing, public-file/link checks and identifying-term scan passed for the 29 allowlisted files. Release packaging includes START_HERE.md and FEEDBACK.template.md. The ZIP and installed copy were compared to the allowlisted source files; no candidate files or personal defaults were included. Host-specific installation UI and browser access on friends' computers remain to be tried.

## Checks completed for 0.3.0

- **53 offline unit tests passed:** 15 tracker, 15 search-state, 13 vacancy-ledger and 10 distribution tests. These cover atomic writes, batch rollback, locks, private-workspace boundaries, exact identity/alias matching, profile and vacancy revisions, timestamp regression, verification cache age, separate assessment/reporting, compact reads, successful-only coverage checkpoints and the earlier tracker/distribution invariants.
- The bundled Codex skill validator passed. Its temporary YAML dependency is not a runtime dependency of this package.
- The distribution checker validated all 27 explicitly allowlisted public files, including internal Markdown links. New vacancy-state, lock, candidate-brief and run-metrics filenames are excluded from distribution.
- A read-only compatibility check loaded four existing version-1 search checkpoint files containing 13 scopes. The stored format and imported search-state API remain compatible; compact output changes the CLI presentation only. Legacy discovery files are preserved inputs, not automatically migrated or treated as assessed.
- On a synthetic stored scope with 2,000 fictional posting IDs, the same pretty-printed JSON status response was **64,873 bytes with full history and 1,482 bytes by default**. This measures serialized output size only. It does not measure model tokens, credits, elapsed time, complete search cost or hiring outcomes.
- An independent search-state review ran the 15 targeted tests and additional read-only/output compatibility checks. It found one misleading error message about creating a new scope; the wording was corrected.
- A separate identifying-term scan found no development-user names, employers, neighborhood or machine identifiers in the 27 public files. Hash comparison confirmed all 125 files in the existing private search workspace were unchanged by the update.
- An isolated installation successfully ran the new vacancy batch command and profile-aware pending summary against a fictional private workspace, without creating or changing tracker/search-checkpoint state.

## Independent 0.3.0 behavior check

An independent agent read the skill and relevant references before evaluating a supplied fictional search scenario. Three boards were blocked, an employer-linked ATS had three pages, and the 12-minute budget ended after page one. It retained Full audit mode, recommended the supported remote role, investigated the role with unknown commute/start date, excluded explicit skill/start and remote-region conflicts, and treated a proven cross-board alias as one vacancy. The response did not invent missing URLs or checked times.

It kept all three blocked board watermarks unchanged and the ATS scan partial with a page-two continuation, saved discoveries before coverage IDs, and separated assessment from actual reporting. In the follow-up, a later candidate start date made old assessments stale while allowing independently fresh source verification to be reused. With no internet tools, it assessed only supplied text and claimed no live verification or completed coverage.

This was an offline instruction-following check, not a live job search, an additional unit test or execution of every scenario in the behavior fixture file.

## Earlier behavior and live evidence

The observations below describe earlier releases and their stated test dates. They are retained as historical evidence, not a claim that those live searches were repeated for later releases.

## Agent behavior scenarios

An independent agent used the skill to complete the original three requests in [behavior_cases.json](tests/behavior_cases.json), using only fictional candidates and supplied postings. Its outputs were read and checked separately; these are behavior checks, not additional unit tests.

| Scenario | Observed result |
|---|---|
| Canadian commercial candidate with assisted technical work | Kept formula/programming gaps, preserved personal versus team attribution, flagged unknown commute, rejected a known distance conflict, and ignored instructions embedded in a posting |
| UK career changer seeking part-time onsite work | Used that candidate's constraints; flagged unknown language/work eligibility; rejected required driving, qualification and hours mismatches |
| Experienced US designer seeking remote work | Preserved senior-level positioning, distinguished US and UK remote scope, did not discard an explicitly open older posting, and kept a future follow-up planned rather than sent |

The evaluator did not browse, send, submit, change the package or modify real candidate data. One-off reviews correctly did not force tracker creation.

## Bounded live pilot

A separate agent used the fictional Toronto configuration and available web tools for an approximately two-minute read-only search, capped at two results. It followed employer websites to the actual postings and accessible blank application forms:

- [Maple Customer Support Coordinators](https://jobs.lever.co/getmaple/15d3f92b-1e52-4247-b800-52134986c4c7), reached from the employer's careers page.
- [Cardata Customer Success Associate](https://job-boards.greenhouse.io/cardata/jobs/4417657009), reached through the careers board linked from the employer's website.

Both were presented as investigate, with actual skill/schedule/compensation questions. The report identified a material Excel evidence gap and conflicting evening-hours wording instead of hiding them. It distinguished agent processing time from unmeasured candidate time. No account, résumé upload, submission, message or paid service was used. These links record what was checked on the stated date; their future availability is not guaranteed. Detailed pilot output remains outside the public package to avoid presenting a dated shortlist as a current job feed.

## Live browser checks for 0.2.0

The developer inspected user-authorized Chrome tabs on 13 October 2026. Only generic UI mechanics are recorded here; no account data, raw snapshots, listing dumps or browser identifiers ship in the package.

- LinkedIn: verified keyword/location results, available posting-date ranges, and a successful move to page 2 with different job cards.
- Indeed Canada: verified query/location results, date ranges and the date-sort link, then moved to another results page and observed different cards.
- Glassdoor Canada: moved from For you to Search, resolved a location mismatch, verified the correct resulting query/location heading, inspected date ranges, and loaded an additional batch (30 to 60 job cards). Initial DOM observations lagged visible navigation; refreshed state was required before declaring success.
- Official careers entrypoints for Google, IBM, Amazon, NVIDIA, AMD and RBC were researched. Several search pages only exposed shells through text retrieval. They are documented as discovery routes, not fully tested live integrations.

These were bounded navigation tests, not exhaustive searches or a completed baseline for any candidate. No application, message, alert, account-preference change or paid action occurred. Newest sorting was not applied end-to-end on every board; future runs must verify actual active controls. Live incremental behavior across calendar days has not yet been observed.

An independent offline review exercised a baseline stopped after three pages, resumption two days later, adding a new employer, repeated IDs and unknown dates. It confirmed separate source checkpoints and conservative coverage dates. It found an oversized-state defect: a valid checkpoint could create a file larger than the reader's limit. The helper now rejects that write before replacing the prior state, with ASCII and UTF-8 regression coverage. The review also prompted explicit durable discovery records and pending/reported status outside the ID checkpoint file.

## What remains unverified

- GitHub Actions includes Windows, Linux and macOS with Python 3.10/3.13, but those hosted runs have not been executed here. Local execution used macOS/Python 3.12.14 only.
- Automatic skill discovery in every Codex host/version has not been tested. The installer verifies files, not the host's UI state.
- There is no live regression suite against job boards, automatic geocoding, universal résumé exporter or autonomous application submission.
- The tracker validates records, the search helper validates checkpoints, and the vacancy helper validates supplied identities, revisions and cache age. None can prove an external event, correct candidate assessment, official source identity or complete UI traversal. Extraction and evidence interpretation still require the agent. Conflicting late duplicate identities fail for review; no automatic merge or destructive migration is provided.
- Privacy checks catch known patterns and unsafe package paths, not every possible personal detail. Read the public contents before publishing.
- The five added fictional behavior scenarios in the fixture file are specifications for evaluation, not automatically executed unit tests.
- No test establishes exhaustive vacancy coverage, access to every board, employer ATS compatibility, time savings for every user or improved hiring outcomes.
