# Search angles and employer targets

Use when a candidate wants different opportunities, major employers, a fresh run beyond an existing list, or a search built from company rankings and named targets. Apply the modes and verification rules in [search](search.md); this reference changes discovery strategy, not eligibility or submission authority.

## Find new paths from existing evidence

Recover the candidate's profile revision, supported tasks, independent versus assisted capabilities, hard limits, old vacancy IDs and unfinished scopes. Keep a short private search plan with each angle, the evidence behind it, query family, employers/sources, coverage status and useful outcome. A new angle should change more than the wording of the same query.

| Angle | How to use it |
|---|---|
| Duties before titles | Translate product demos, onboarding and explaining software into customer support, customer education, implementation coordination or client service. Translate prospect research, CRM work and presentations into sales support, partner coordination or business development. Verify the actual duties before deciding fit. |
| Combine two domains | Look for employers where prior industry work and another supported skill reinforce each other: delivery coordination plus software demonstrations can suggest fleet-software roles; customer follow-up plus professional-services experience can suggest account onboarding. This is a search hypothesis, not proof of specialist competence. |
| Operational routes into a large employer | Include scheduling, dispatch, vehicle or inventory operations, order administration, service coordination, claims support, renewals and vendor/partner administration where the candidate accepts those duties. Do not restrict a business-background candidate to marketing or a single entry-level label. |
| Learning and employment routes | Where accepted, inspect paid training, fixed-term contracts, seasonal work, student programmes and junior positions. Read enrolment, graduation, licensing, training-location and pay conditions; do not assume the candidate qualifies for a technical co-op or completed-degree programme. |
| Employer and ecosystem routes | Search the requested company directly, its verified Canadian entity and relevant brands/subsidiaries. Explicitly label a distributor, franchise, staffing client or partner: work involving a famous product is not employment by that brand. |
| Complementary discovery routes | Combine live job boards, employer career pages, linked ATS and public web discovery. Use title variants and one adjacent-duty query for roughly four core queries as a configurable starting point. Adapt to the candidate and available results rather than imposing that ratio as a quota. |

Do not infer fit from a reassuring title, department or automated match score. A technical-marketing job may require engineering and GPU programming; an operations analyst may require advanced spreadsheets and systems administration. Apply explicit experience minima before deep review, then assess actual essential tasks. AI-assisted output does not establish independent tool competence. Ask only decision-changing questions using [profile](profile.md#broaden-a-returning-search).

## Turn supplied company lists into a private target register

When the user asks to inspect open rankings/tabs first, do that before using them to seed the search. Record the actual source, date, category, year and portion read; preserve inaccessible sources as limitations. Read the selected size/category rather than silently using a small-company tab for a large-employer request. An employer award is a discovery aid, not evidence that a vacancy is open, a particular team is suitable, or hiring is likely.

Import all explicitly requested names from supplied tables/files. Treat descriptions, tickers and categories as user-provided labels unless independently verified; no investment or index-membership analysis is needed merely to search jobs. Deduplicate repeated company names and verified aliases while retaining their source memberships. Preserve distinct legal entities and hiring boards, such as a parent corporation and a separately named asset manager. Do not invent openings to populate a company list.

The deliberately shared, candidate-independent [employer seed list](priority-employers.json) may be bundled as configurable discovery data; use [employer priorities](employer-priorities.md) for its default behavior. Keep each candidate's additions, exclusions, ranking observations, selected priorities and actual search state in their own designated private workspace. Never write their account details, personal limits or current vacancies back into this shared package. A later candidate receives a separate register.

Useful target fields are: canonical employer name, supplied aliases, source list(s), priority, verified corporate/careers entrypoint, relevant brands/entities, scope IDs, coverage state, checked date, blocker/resume hint, and linked vacancy IDs. These can be ordinary JSON/table rows; no helper or connector is mandatory. Follow official-route verification in [browser search](browser-search.md#named-employers-and-sectors).

## Make a company pass auditable

For each requested employer, distinguish these states:

| State | What it establishes |
|---|---|
| Registered / pending | The employer is in the target list; no search claim |
| Index screened | Focused public-web discovery was performed; unindexed vacancies and live inventories remain unscanned |
| Inventory partial | Some live search results were enumerated; save actual filters, IDs/pages, remaining controls and resume point |
| Defined scope complete | Every exposed page/batch in the stated live scope reached an observed terminal state; assessment may still be pending |
| Blocked / unavailable | Access or rendering prevented reliable observation; record the exact limitation, last successful scope and permitted fallback |

Record search coverage, detailed vacancy assessment and reporting separately. A web query with no useful hits, a JavaScript shell, generic zero-jobs placeholder or a complete shortlist cannot certify no openings. Reconcile contradictions between indexed descriptions and the live board. A fallback may find jobs but cannot complete the blocked inventory. If a country/city facet excludes the candidate's office cities, check the employer's remote route separately before concluding the location scope has no usable roles.

For “all openings,” define the employer/legal entities, geography, remote eligibility, role families and date window from the request. Enumerate the accessible scope using [browser search](browser-search.md#first-full-scan-all-reachable-matching-results); do not silently substitute a few keyword queries. Screen clear location, experience or credential conflicts without deep-reading unrelated engineering or senior roles. Large lists may require checkpoints: retain every requested employer, distinguish completed, partial and pending work, and state what remains. Do not describe partial coverage as having checked every opening at every company.

## Rank useful choices and preserve the old list

For a request for jobs outside an existing queue, compare verified requisitions, canonical URLs and source aliases against that dated baseline. A different title, board, location label or posting date alone does not establish a new vacancy. Keep a separate requisition at the same employer when identity evidence supports it. Follow the shared [vacancy identity rules](efficiency.md#identity-and-discovery).

Prioritize supported core duties, hard-condition fit, readiness and material uncertainties, then apply the candidate's stated employer preference. Show why a smaller employer may still offer a stronger task match. A famous name does not erase a tool, credential, pay or attendance conflict. Unknown salary and OTE-only figures stay conditional; distinguish realistic stretches from established hard mismatches and unverified leads. Ranking is an effort-allocation aid, not a hiring probability.

Deliver the requested ranked findings and a per-company coverage view. Separate current verified openings, pay/skill-conditional options, unavailable/unverified leads and useful exclusion reasons. Preserve old queue numbering and application history unless the user asks to merge or rerank. New discoveries do not become applications or submitted rows in the working application tracker. Recheck a selected vacancy before tailoring materials; the candidate's saved final-review/Send/Submit preference still governs later applications.
