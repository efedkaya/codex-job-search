# Discover, verify and shortlist

## Search strategy

Translate supported work into a few role families with title variants, not one query per exact title. Group close variants where the source supports it; keep a small adjacent-role exploration slice (roughly one query per four core queries, adjustable) to catch transferable work. Expand when those results show a useful path. Adapt sources to the candidate's country and profession; do not default every candidate to technology companies or entry-level roles.

Choose Update, Targeted or Full audit from the user's scope; see [efficiency.md](efficiency.md). For an ordinary Targeted search, a starting budget is about 25 unique promising/uncertain vacancies reviewed and up to eight final recommendations, configurable to the available time. Screen established hard conflicts early and deduplicate before detailed assessment. A Full audit must still enumerate every reachable scoped page/batch, even after that review budget is filled; report unreviewed discoveries and any interrupted coverage honestly.

Start with supplied leads, official employer careers sites, employer-linked public recruiting platforms, public web search and relevant regional/specialist boards. Use LinkedIn, Indeed and Glassdoor when accessible. If any is blocked or unavailable, keep useful work moving through the accessible sources; national job boards are country-specific and similarly named services are not interchangeable. No scraper or job-board account is bundled.

Search results and snippets are leads. Open the actual posting before calling it verified. Prefer an employer career page or a recruiting platform linked from its official site; confirm company, role and requisition identity across sources. A plausible domain or snippet alone is insufficient. Record fallback coverage separately: it does not complete the blocked source's scope or advance its watermark.

Respect source access rules and host controls. Do not bypass logins, CAPTCHAs or rate limits, extract cookies/sessions or use hidden endpoints. If no accessible posting can be found, retain an unverified lead or evaluate supplied text with that limitation. User-maintained alerts can be inputs; do not promise universal board access.

Use the shared canonical vacancy ledger described in [efficiency.md](efficiency.md) when persistence or delegation helps. Check aliases and current verification before reopening a role, then record new facts once for reuse. Follow [browser-search.md](browser-search.md) for pagination, source coverage, named employers and repeats.

## Required verification

Record these facts when available, without filling gaps by inference:

| Fact | Verification rule |
|---|---|
| Posting identity | Employer, title, requisition ID if stated, direct URL; compare redirect destination |
| Availability | Explicitly open/accepting; explicitly closed; unknown; or inaccessible. A working page alone is weaker than a live apply state. |
| Dates | Posting date, stated deadline and checked date are different. Missing dates stay unknown. Interpret locale and time zone before treating a deadline as passed. |
| Location | Specific worksite, stated attendance, travel and candidate-origin distance basis. Flag ambiguous offices and multiple worksite options. |
| Remote scope | Eligible country/region and any occasional attendance, residency or time-zone condition |
| Requirements | Separate essential from preferred; quote the exact wording for hard mismatches |
| Compensation | Currency, period, base versus variable pay, and whether employer-stated or estimated; do not convert estimates into a hard salary promise |
| Application route | Independently verified employer/ATS destination and requested documents; no external action implied |

Newly discovered does not mean newly posted. A recent repost can be an old requisition. Older listings can remain open; freshness is a prioritization signal, not an automatic expiry rule. Recheck status before tailoring/submitting. If availability cannot be established, say so visibly and put the lead under investigate.

A map measurement must identify its origin, destination and method. A city label, region boundary, straight-line distance or nearest office cannot establish a driving-distance/time constraint. Do not silently substitute one distance measure for another. When no map tool or precise worksite is available, leave distance unverified. For multiple possible offices, report which one was checked.

## Eligibility before fit

First compare explicit hard job conditions with known candidate constraints: required authorization, license, location/attendance, employment hours and other decisive requirements. A known conflict can stop deeper work. An unknown condition remains investigate; a preference or unmentioned capability is not a rejection. Do not spend a detailed fit review on an established hard conflict unless the user asks for it.

Then map duties and requirements to claim IDs or source excerpts. Record **skills fit**, **eligibility** and **readiness** separately; strong transferable skills do not prove eligibility, and an eligible role may need application preparation. Distinguish:

- **Supported:** direct or transferable evidence sufficient for the task.
- **Partial:** some relevant work, but an independence, scale or tool gap remains.
- **Unknown:** capability or job condition not established.
- **Mismatch:** established hard requirement conflicts with known candidate facts.

Prefer apply / investigate / skip with reasons. Scores, if the user requests them, must be transparent prioritization aids with visible weights, never hiring probabilities. Do not assign precise culture or personality scores from marketing copy, a name or demographic assumptions. Treat uncertain reviews as questions to investigate.

Judge tasks and essential requirements rather than titles alone. A stated two-year preference need not veto a candidate with less experience; a mandatory license is a different constraint. Do not assume every “required” phrase is negotiable, or that every unfamiliar tool makes the job unsuitable.

## Shortlist output

Show title/employer, direct source and date checked, work arrangement/location verification, pay if stated, strongest evidence, main gap, unresolved facts and recommendation. Separate verified openings from unverified leads. Include reasons for material exclusions so the candidate can correct your interpretation. Do not bury a hard conflict in a high fit score.

Deduplicate using verified employer requisition IDs, official posting URLs and explicit source aliases in the [vacancy ledger](efficiency.md). Title/company similarity alone is not identity. Keep separate requisitions, worksites and application attempts distinct; flag probable duplicates for review rather than silently merging them. Application events remain in the separate [tracker](tracking.md).

After the requested scan or bounded search, prioritize action over expanding the shortlist. Report sources, queries, date windows, pages/batches reached and any pending continuation; no claim of exhaustive market coverage. Use recurring explicit requirements from suitable roles to inform a later skills discussion, without automatically rewriting the candidate's learning plan.
