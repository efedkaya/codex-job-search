# Live boards, employers and repeat searches

This is an agent workflow using the host's supported browser tools, not a bundled scraper or an API integration. Read the current browser tool instructions. Use only available, documented operations. Search through visible UI and inspect results after navigation; do not extract cookies, call hidden endpoints, bypass restrictions or install a browsing dependency silently.

## Define the search before counting coverage

Reuse the candidate's profile, chosen sources and named employers. Establish role queries, country/location, work arrangement, experience constraints and IANA time zone. Candidate preferences are not automatically hard filters. When a site's radius or remote filter is coarser than the candidate's rule, search a safe superset and verify individual roles. Report the actual site filters. Never infer that a search centered on a city proves a measured commute.

For user-supplied open tabs, inspect the current tab inventory and bind the matching tabs. A Jobs home page or “For you” feed is personalized discovery, not the complete result set for a query. Open the site's actual search and verify its heading, query, location and active filters. Location suggestions can resolve to the wrong city or country; inspect the selected suggestion and resulting heading. Do not silently reuse another candidate's account preferences as profile facts.

Use a stable scope for each source plus query, location, employer, constraints and time zone; see [search-state.md](search-state.md). Keep the rolling date window and resume page outside stable filters, otherwise every repeat search becomes a new baseline. A new target employer or materially changed search scope gets a fresh baseline; unchanged scopes retain their checkpoints.

## Compact observation and source fallback

Use the smallest supported browser read that answers the current question: result cards plus query/filter and Next/load-more state for discovery; identity, eligibility, requirements and apply/closure state for verification. Keep summaries in the ledger and output only the current batch or requested fields. Do not repeatedly emit whole-page snapshots, account sidebars, navigation trees or full HTML when targeted reads suffice. Use a full snapshot or screenshot when it is necessary to locate controls, resolve loading/layout ambiguity or obey the browser tool contract; then return to focused reads. Never invent a selector or an unsupported read operation.

If LinkedIn, Indeed or Glassdoor requires unavailable access, is blocked, or cannot be searched reliably, record that scope as blocked/partial and continue on official employer sites and their linked public ATS, public web search, and suitable regional or specialist boards. Independently confirm official link chains. Web snippets establish discovery only; an accessible actual posting is needed for verification. Give each fallback its own coverage scope. Do not treat fallback findings or completion as successful coverage of the blocked board, bypass restrictions, extract sessions or call hidden endpoints.

## First full scan: all reachable matching results

An explicitly requested full first scan uses Full audit mode; a bounded Targeted shortlist does not silently become an exhaustive baseline. Start a full baseline with no posting-age cutoff unless the user explicitly requested one. Follow every accessible results page or loaded batch for that scope. “All pages” means the results the site exposes for the stated query and filters, not every job that exists. Treat a site-imposed result cap as a coverage limit and record it; do not promise complete market coverage.

1. Read the current results and record unique listing IDs/direct URLs, employer, title, visible location, raw posting-date label and checked time. Save compact discovery facts in the shared [vacancy ledger](efficiency.md) before checkpointing IDs or moving on. Retrieve scope membership only for the current batch; seen does not mean assessed/reported. Do not open every clearly irrelevant role for a deep review.
2. Use the observed Next/page/Show more control, or a documented scroll action on the actual results pane. Reacquire the page state after each action. If the view is still loading or observations disagree, use the supported refreshed snapshot/screenshot to establish the completed state before continuing. Lazy-loaded and virtualized lists can replace earlier cards: accumulate each visible batch before it disappears, scrolling progressively through the actual result pane. Do not press End, jump straight to the bottom or take only a final snapshot: those actions can skip cards that were never observed.
3. Check progress through new IDs, a changed page indicator or newly rendered cards. Deduplicate sponsored/repeated cards. Do not count clicking Next as proof it changed pages.
4. Checkpoint every page/batch with cumulative pages seen, stable IDs and a human-readable resume hint. In resume_locator, include the clean search URL, observed page/batch, visible continuation control, last batch IDs, whether loading settled and whether a terminal state was observed. Save observed evidence, never session tokens or DOM element indexes.
5. Finish only with observed coverage evidence: terminal page/disabled Next, explicit no-results state, or an equivalent verified end. No new IDs after one action is not an end signal. Inspect once for loading/blockers and try one supported continuation; if still inconclusive, record partial coverage and the reason.

A user stop, stopping at an agreed budget before enumeration ends, login/CAPTCHA, rate limit, failed navigation, unknown end or inaccessible results makes this scope partial/blocked/failed. A full shortlist is not a terminal-page signal. Report enumerated and assessed counts separately; pending assessments remain recoverable even when enumeration has completed. Keep the last successful checkpoint unchanged and report where to resume. Continue independent accessible sources. Do not create a background automation merely to finish later. On resumption, recheck the newest/front pages before continuing from the saved hint because page numbers and rankings shift.

## Later runs: only new findings since the last successful search

Update mode first checks pending/unreported ledger entries and changed profile requirements, then discovers the delta for each established scope. Reuse current assessments and verification according to [efficiency.md](efficiency.md); do not repeat deep verification of unchanged reported roles without a reason. Use the inclusive local calendar day returned as requested_since, not the last time the skill was invoked for any purpose. Fetch from fetch_since (one preceding day by default) to cover coarse dates and boundary overlap. Choose the narrowest site date filter that fully contains that interval; if the last scan was ten days ago, a past-week filter is too narrow. If no offered filter reaches far enough, use All dates and compare results locally.

Select newest/date order when available and verify it took effect. Preserve query/location filters if changing sort resets them. Do not stop at the first old or sponsored card. Prefer enumerating the entire filtered result set; when no trustworthy date filter/order exists, compare IDs across all reachable results in scope. The helper cannot judge UI completeness or parse posting dates; the agent must do that.

Classify findings explicitly:

| Finding | Treatment |
|---|---|
| Unseen ID with reliable posting date within requested window | Newly posted; assess for the main shortlist |
| Unseen ID with missing, ambiguous or relative date crossing the cutoff | Newly discovered, freshness uncertain; separate from verified new postings |
| Unseen ID dated before requested window, including overlap-only or late-indexed items | Older newly discovered; separate optional note, not a “new today” claim |
| Known ID with changed date/title/description | Updated or reposted; surface only meaningful changes, not a new vacancy by default |
| Same employer requisition found on another board | One opportunity with multiple sources; preserve source coverage and URLs |

Preserve raw relative labels such as “24h,” “3d” or “30d+,” observation time and uncertainty. Do not turn them into invented exact timestamps. An “updated” date is not necessarily the original posting date. An unseen ID is not enough to establish freshness. Work found in an interrupted run remains in the private ledger as pending until assessed/reported; do not discard it just because a resumed checkpoint calls it already seen.

Only successful coverage advances that scope's date boundary. The helper conservatively carries the earliest unfinished coverage start across resumed attempts. A later fresh incremental run catches it up, with deduplication preventing repeated recommendations. A genuinely checked empty result set can complete; a loading spinner, page shell or blocked view cannot.

## Board-specific guidance

These are UI observations from 13 October 2026, not permanent selectors. Discover the current controls each run. Country versions and accounts differ.

| Source | Observed search behavior | Operating rule |
|---|---|---|
| [LinkedIn Jobs](https://www.linkedin.com/jobs/) | Keyword/location search, Date posted choices and numbered pages/Next; the current page warns of a transition from classic search | Check the active search mode and filters; do not assume classic URL parameters or old element names remain valid |
| [Indeed Canada](https://ca.indeed.com/) | Search has Date posted (24h/3/7/14 days), date sorting and Next page; homepage uses “Show more jobs” | Verify the local country's site, applied date/sort/radius and actual pagination; “New” is not an exact posting date |
| [Glassdoor](https://www.glassdoor.com/Job/index.htm) | Search is separate from For you; date, relevance, distance controls, relative date labels and Show more jobs were exposed | Resolve location suggestions carefully, verify actual results, and inspect the current load-more/pagination mechanism rather than assuming one |

Do not click Save, Dismiss, Create alert, Apply, Express interest or account-setting controls during discovery. These can change the account or communicate interest. Handle any requested external action under the user's authorization and current host policy. When access fails, use an independently found employer posting or report the lead as unverified; a fallback does not complete the blocked board's scope.

## Named employers and sectors

When the user names an employer, add its official careers site as a separate source alongside boards. Start at its corporate website, follow Careers/Jobs, then verify any onward recruiting domain from that link chain. Record the official entrypoint, current destination, employer/legal entity and checked date. Do not infer an ATS hostname or hardcode stale application URLs. No application submission is implied.

Apply the candidate's role, location and eligibility criteria independently to each employer. Separate corporate, retail, franchise, subsidiary, contractor, student and hourly hiring where relevant. A brand match alone does not establish the hiring entity. An employer may expose several boards; disclose which were searched.

For a sector such as “banks,” use an already-known market and propose a clearly labelled initial employer list. Ask for region/priorities only if needed. Do not describe a seed list as coverage of every employer in that sector.

Official starting points checked on 13 October 2026:

| Employer | Official route | Verification limit |
|---|---|---|
| Google | [Careers search](https://www.google.com/about/careers/applications/jobs/results/) | Search controls exposed; not an exhaustive vacancy scan |
| IBM | [Careers](https://www.ibm.com/careers) → [search](https://www.ibm.com/careers/search) | Live fetch exposed a shell; browser result traversal still required |
| Amazon | [Amazon Jobs](https://www.amazon.jobs/en/) → [search](https://www.amazon.jobs/en/search) | Search discovery checked; corporate/hourly/student scope must be explicit |
| NVIDIA | [Corporate careers](https://www.nvidia.com/en-us/about-nvidia/careers/) → [current careers destination](https://jobs.nvidia.com/careers) | Follow the current corporate link; do not assume an old Workday URL |
| AMD | [Corporate careers](https://www.amd.com/en/corporate/careers.html) → [external careers](https://careers.amd.com/) | Corporate link checked; result extraction not verified; avoid internal-only employee links |
| RBC | [RBC Jobs](https://jobs.rbc.com/ca/en) → [search](https://jobs.rbc.com/ca/en/search-results) | Live fetch exposed a shell; interactive coverage not tested |

These examples are optional discovery aids, not the supported-employer list. Resolve any other requested employer the same way. Reverify link chains at search time.

## Report and time budget

Summarize per source/query: baseline or incremental, requested date window, pages/batches and unique IDs observed, completion status, limitation and next resume action. Then show a small evidence-based shortlist and a separate section for uncertain freshness or material updates. “No new verified matches” is narrower than “no jobs.”

Keep candidate review/application hours separate from agent browsing time, tool-call and host usage limits. Use the [efficiency guidance](efficiency.md) for configurable budgets and actual-use measurements. Broad first scans can require several sessions. If a scan cannot fit, save its progress rather than pretending completion or quietly shrinking the user's scope. Reuse stored results for deeper assessment, applications and interview preparation.
