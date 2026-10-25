# Codex Job Search

Find relevant opportunities, explain the fit, and keep an honest application history.

A reusable skill for OpenAI Codex. It adapts to the candidate's country, career stage, work preferences and available time. Personal information lives in a separate private workspace. Each person starts with their own location, pay, experience and skills. A configurable 241-company list gives discovery a large-employer priority without overriding those facts.

**Status: preview release, 0.5.0.** An independent community project, not an official OpenAI or Anthropic product. The skill runs in your local Codex setup; no hosted service, user database or background search is included.

[Download the preview ZIP](https://github.com/efedkaya/codex-job-search/releases/latest) · [Get started](START_HERE.md) · [Send feedback or report a problem](https://github.com/efedkaya/codex-job-search/issues/new/choose)

## New in 0.5.0

- More deliberate evidence selection before résumé rewriting, scoped letter edits and a separate review of factual grounding and effectiveness.
- [Final-document checks](skills/job-search/references/document-quality.md) for the actual saved file, with an optional read-only [material checker](skills/job-search/scripts/check_materials.py) for text, placeholders, hashes, limits and supported extraction. PDF checking uses an already installed parser when available; it does not render pages or establish ATS acceptance.
- Interview story mapping with primary/backup examples, focused drills based on observable answers and preparation tied to the materials actually sent.
- [Imported-job guidance](skills/job-search/references/source-adapters.md) that preserves raw values, source defaults, errors and partial coverage; no scraper is bundled.
- A concise next-action queue and evidence-based interpretation of application replies, preserving the candidate's final-send boundary.
- Selected workflow ideas from ten reviewed repositories, with pinned revisions and notices in [adaptation provenance](skills/job-search/references/third-party-notices.md).

## New in 0.4.0

- Background-led setup with a dated private profile and portable context snapshot.
- A [241-company priority seed](skills/job-search/references/priority-employers.json), configurable by each candidate, with honest company-by-company coverage.
- A [reusable answer bank](skills/job-search/references/answer-bank.md): real job requirements surface useful questions; confirmed replies refine searches and future drafts without repeated intake.
- Selected-job application preparation with candidate-final-review-and-submit as the default, including email, employer ATS and job-board routes.
- Profile audits, materials/tracker reconciliation, interview preparation and offer comparison, alongside the existing search/checkpoint helpers.
- A [ChatGPT conversation starter](CHATGPT_STARTER.txt) with an explicit context-file fallback. This is not a native web-plugin installation or a promise of account memory.

## What it does

- Builds a profile from evidence, keeping independent ability, assisted work and coursework distinct.
- Searches accessible LinkedIn, Glassdoor, Indeed and Canada Job Bank pages where regionally relevant through supported host browser tools, with official employer sites, employer-linked public recruiting platforms, public web and regional/specialist boards as useful fallbacks.
- Offers Update, Targeted and Full audit modes. An explicitly requested full first scan covers all reachable scoped pages; repeat runs use each source’s last successful scan and interrupted coverage stays resumable.
- Keeps newly posted, newly discovered and updated/reposted roles distinct, and verifies promising leads against actual postings.
- Screens established eligibility conflicts before deeper fit work; keeps unknowns open for investigation and explains apply / investigate / skip decisions.
- Shares canonical vacancies, board aliases and current verification in a private ledger, so repeated queries and workers can reuse the same evidence.
- Checks location, remote eligibility and commute constraints without pretending a city label is a measured commute.
- Helps tailor résumés, answer application questions, practice interviews and draft follow-ups.
- Tracks vacancies, coverage, separate application attempts, confirmed events and human time with optional offline Python helpers.

It does not ship job-board scrapers, automatically apply, send messages, bypass access restrictions, guarantee interviews, or claim a universal ATS score. A skill runs when invoked or selected by Codex; unattended runs require a separately configured automation requested by the user.

## Quick start

Trying this from a friend? Start with [START_HERE.md](START_HERE.md) for the ChatGPT starter or guided local Codex installation. Use [the feedback template](FEEDBACK.template.md) after your trial; nothing is collected or sent automatically.

You need Codex with skill support. A supported browser connection and permitted site access are needed for live signed-in board searches. Web access is needed for current job discovery; without it, the skill can review pasted postings. Python 3.10+ is needed only for the optional helpers. The tracker, packaging tool and text/DOCX material checks use the Python standard library. PDF material checks optionally use an already installed pypdf or pdftotext; unavailable checks are reported explicitly. Calendar search checkpoints require IANA time-zone data; some systems, especially Windows, need the Python tzdata package. No paid search service, API key, Bun or LaTeX installation is required. Host AI usage and optional third-party services follow their own plans and limits.

From the extracted package directory:

~~~sh
python tools/distribute.py check
python tools/distribute.py install
~~~

On macOS/Linux the interpreter may be named python3; on Windows it may be py. The installer copies only the skill folder into ~/.agents/skills/job-search, following the current documented global skill location. It refuses to overwrite a different installation and leaves existing files untouched. It can be pointed at another supported skills directory with --skills-dir, including ~/.codex/skills for hosts using that location. No configuration permissions are modified.

Alternatively, copy the entire [skills/job-search](skills/job-search) folder into a supported skill location. For a project-only skill, use .agents/skills/job-search in that project. See [OpenAI's skill documentation](https://learn.chatgpt.com/docs/build-skills). If the skill does not appear, refresh or restart the host and check its supported discovery paths.

Then ask Codex:

> Use $job-search to help me search for work. Ask only for missing information that changes the search, and keep my profile outside this public package.

Or use it for a smaller task:

> Use $job-search to assess this posting against my résumé. Explain the evidence, gaps and unknowns before preparing any application documents.

> Use $job-search to find a shortlist for this week's two-hour search session. Verify the actual openings and prioritize the best next actions.

Choose the mode that matches the request:

| Mode | Starting point |
|---|---|
| Update | Review pending/new/changed findings in established search scopes |
| Targeted | Review roughly 25 unique promising/uncertain vacancies and return up to eight recommendations; adjust these budgets to the session |
| Full audit | Enumerate every reachable page/batch in agreed scopes, saving honest partial progress if the budget ends |

For a full first scan followed by repeat searches:

> Use $job-search with my LinkedIn, Glassdoor and Indeed tabs. Search all reachable results for my agreed roles and location, then save progress. On future runs, show new jobs since the last successful search for each source. Also check the official careers sites of my named target employers.

A broad first scan can span several sessions. Site limits and blocked or unfinished sources remain visible; a full shortlist does not complete an unfinished scan. Date filters use a small overlap and ID deduplication. Accessible fallbacks keep the search useful but cannot advance a blocked board’s checkpoint. See the [browser workflow](skills/job-search/references/browser-search.md), [checkpoint guide](skills/job-search/references/search-state.md) and [focused-search/ledger guide](skills/job-search/references/efficiency.md).

No universal slash commands or specific connector names are assumed. Use the skill selector available in your Codex host, or invoke $job-search explicitly.

## A private workspace for each candidate

Have Codex create or use a private directory outside both this public repository and the installed skill. Copy the blank [profile template](skills/job-search/references/profile.template.json) there. Do not replace public examples with your real résumé or edit candidate facts into SKILL.md.

On first use for an ongoing search, [personal setup](skills/job-search/references/first-run.md) runs a short intake in rounds of up to three questions. It invites a CV/portfolio or written background, asks about roles and employers, location/work arrangement, and material limits such as commute, start date and time budget. It reads supplied information before asking and skips known or optional details. Returning users reuse their private profile instead of repeating setup. A single posting review does not force full onboarding.

The profile separates hard constraints from preferences. Unknown language, salary, work rights, tools and commute details remain unknown. Only ask for information relevant to a decision. Exact home addresses and demographic data are not needed.

[Toronto commercial-work example](examples/toronto_fictional.json) and [Leeds career-change example](examples/leeds_fictional.json) are entirely fictional. They demonstrate different countries, functions, work arrangements and budgets; neither should silently become the next user's profile.

The [first-use guide](skills/job-search/references/first-run.md) defines how to save profile/evidence, the answer bank and a dated PROFILE_CONTEXT.md outside the public package. Without persistent files, the assistant should provide a copyable context snapshot and state the limit; account memory is separate and requires an actual authorized feature. The [employer priority guide](skills/job-search/references/employer-priorities.md) explains the bundled company seed. Names are not vacancies, and copying the seed does not inherit another candidate's search status.

Optional local helpers keep different facts separate:

- [Vacancy ledger](skills/job-search/references/efficiency.md): canonical opportunities, explicit source aliases, assessment, reporting and reusable verification; compact filtered reads.
- [Search checkpoints](skills/job-search/references/search-state.md): per-scope coverage, seen IDs, pending continuation and current-batch membership; compact output by default, `--full` when needed.
- [Application tracker](skills/job-search/references/tracking.md): separate application attempts, confirmed events and human time; CSV exports contain job rows while full event history remains in JSON.

They do not browse or contact anyone. Existing tracker/search-state files stay separate; no automatic destructive migration is required. Recover any older unreported discoveries before treating the new ledger as complete. An optional compact profile brief can help workers share relevant facts without repeatedly loading a full CV or transcript.

## Evidence before confidence

| Situation | Expected behavior |
|---|---|
| A portfolio contains an AI-generated script | Record assisted work; do not assert independent programming |
| “Remote” requires monthly attendance | Check location and attendance against that candidate's constraints |
| A posting is blocked or unavailable | Seek accessible official/public sources; retain the blocked scope and unverified availability until a posting is checked |
| A role appears on several boards | Reconcile verified identity and aliases once; do not duplicate a current verification |
| A virtualized list only shows its final cards | Continue progressive traversal and save each batch; a bottom snapshot does not establish complete coverage |
| A candidate plans to send a follow-up | Record planned, not sent |
| Two requisitions share the same title | Preserve separate opportunities and attempts |
| A course is in progress | Describe it as learning, not a completed credential |
| A profile does not mention a required language | Ask or flag unknown; do not invent proficiency or inability |

## Testing and limits

~~~sh
python -m unittest discover -s tests -v
python tools/distribute.py check
~~~

Tests exercise baseline/incremental coverage, interrupted scans, compact checkpoint reads, vacancy identity/cache/revision handling, tracker state, time-zone boundaries, data preservation, CSV escaping and distribution boundaries. [Behavior scenarios](tests/behavior_cases.json) support independent agent evaluation with fictional candidates; they are not silently counted as unit tests. [Validation notes](VALIDATION.md) distinguish checks actually run from untested environments.

Measure efficiency only from actual available usage and comparable scope; synthetic output-size tests are not token, credit or cost savings. No promised speedup or savings is included, and the workflow does not change model, speed or account settings. No tests establish current coverage of every job board or improved hiring outcomes. Search quality still depends on accessible sources, truthful candidate information, the host model and human judgment. A successful PDF text extraction check does not certify all ATS systems. Regional résumé and eligibility conventions require current authoritative sources where material.

## Privacy and sharing

Only explicit files in [distribution.json](distribution.json) enter the generated ZIP or local install. The distribution checker rejects common private-state filenames, credentials, machine paths and unsafe links/paths. This catches common mistakes, not every possible personal detail; inspect the contents before publishing.

~~~sh
python tools/distribute.py package --output ../codex-job-search.zip
~~~

The downloadable release ZIP contains only the allowlisted public package. Review the complete file list before sharing your own modified copy. Keep real profiles, source documents, application histories, screenshots, session logs and credentials out of public commits and issues. .gitignore is a convenience, not protection for data already tracked.

The helper itself makes no network requests. Codex may send material it reads to its configured model, and enabled connectors follow their own data policies. Local files do not mean entirely offline processing. No automatic upload, analytics or telemetry is implemented by the Python helpers.

## Contributing

Use fictional examples and reserved .example URLs. Run the tests and package check. Useful improvements include better evidence handling, accessible output formats and verified regional guidance. Any source integration should state its access rules, dependencies, cost, failure behavior and live-test status. Avoid adding a scraper or dependency without a demonstrated need. Share reproducible sanitized reports, never a real candidate's tracker.

## Credit and license

Inspired by [Mads Lorentzen's AI Job Search](https://github.com/MadsLorentzen/ai-job-search), especially its structured application workflow and emphasis on evidence. The upstream project already includes Codex-compatible components; this project does not claim to be the first Codex job-search tool.

This package uses an original implementation focused on configurable candidate profiles, explicit uncertainty, accurate event records and minimal dependencies. Selected later workflow adaptations and their retained license are described in [third-party notices](skills/job-search/references/third-party-notices.md). No upstream executable code or external services are bundled. New contributions are offered under the [MIT license](LICENSE). If upstream code is incorporated later, preserve its applicable copyright and license notices.
