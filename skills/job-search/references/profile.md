# Candidate profile and evidence

## Minimal onboarding

Use the current request, candidate-provided résumé/portfolio and authorized professional sources. Do not scan unrelated files, accounts or memories simply because they are accessible. Explain which sources you used. Start with enough context for the task; optional fields can stay null.

### First use

For a new ongoing search, start a short intake when no usable profile exists or the user asks to set up again. Installation alone does not start a conversation; intake begins when the user invokes the skill for setup/search. A one-off posting review still needs only enough context to assess that posting.

First read documents or facts already supplied in this chat or its designated candidate workspace. Invite a CV/résumé and an optional portfolio, work samples or professional profile link in ordinary chat. Never claim access to a friend's prior chats, CV or work history unless actually available. They can skip documents, redact details, paste text or describe their background. Do not make a portfolio, paid account or certification a prerequisite.

Ask at most three concise questions per round, omitting answered topics. A useful first round is:

1. What experience and skills should the search build on? Share a CV and any work samples, or briefly describe your work, education and what you can do independently.
2. Which roles or industries interest you, and are there employers you want to target or avoid? If unsure, offer to suggest directions from their background.
3. Where can you work, do you prefer remote/hybrid/onsite, and what commute limit should apply? Clarify driving distance, straight-line radius or travel time when relevant.

Use a short second round only for unanswered facts that materially affect the search: earliest start date, full-time/part-time/contract and work-hour limits; any firm pay floor (currency and pay period), commission preference or relevant authorization/sponsorship restriction; and how much human job-search time they have plus the desired scope/time limit for this agent run. Keep optional preferences skippable and hard exclusions distinct. Do not ask every subtopic mechanically or repeat facts extracted from a supplied CV. Clarify remote country/region eligibility rather than interpreting remote as worldwide.

Summarize the working profile, supported strengths, uncertain capabilities and hard limits in a few lines, invite corrections, and proceed with the authorized search once enough is known. This summary is not an extra approval gate. If an answer is essential to choosing a country or enforcing a constraint, keep that part pending while progressing on independent work. Optional omissions stay unknown. A short initial shortlist uses Targeted mode unless the user requests a full audit; do not make the first trial an exhaustive scan by default.

Save the profile only in an explicit private workspace when file access is available. Optional onboarding metadata may be `not_started`, `in_progress` or `ready_with_unknowns`, with a review date; it records intake state, not proof that every field is known. On return, reuse the profile and ask only about material changes. A different person gets a separate workspace and fresh intake; never inherit the package author's preferences or another tester's records.

For an ongoing search, establish:

- Target functions, plausible level and acceptable adjacent work.
- Search country/region; remote eligibility; office and travel constraints. Ask whether a distance limit means road distance, straight-line distance or travel time before enforcing it mechanically. A neighborhood or nearby intersection is usually enough; no home address is required.
- Work arrangement preferences and hard exclusions, kept separate.
- Work authorization constraints as reported by the candidate. Do not infer citizenship or immigration status from name, education or location. If role-specific eligibility is unclear, flag it and consult authoritative wording; do not invent a legal exclusion.
- Start date and employment types; languages relevant to target roles.
- Compensation preferences only if they affect screening. Keep currency, pay period, base pay, commission and total compensation distinct.
- Preferred sources and named target employers, if any; search time zone for inclusive-day checkpoints.
- Any stated application submission preference, especially a candidate-performed final review/Send/Submit step. Save it in the private profile and reuse it across channels; see [selected-job applications](submit-applications.md).
- For repeated applications, the chosen working tracker, material catalogue and preferred document layout/length. Reuse existing paths and candidate-approved examples; do not make these optional workflow preferences a new intake requirement.
- Search time available, date range, and whether setup, networking and interview preparation share that allowance.

Ask unanswered essentials together in a few concise questions. Do not demand personality assessments, salary history, identification documents or demographic data. For a one-off posting, uncertainty notes may be sufficient.

## Broaden a returning search

Ask when an answer can change an actual search scope, eligibility decision or evidence mapping. Reuse established answers; do not repeat onboarding or make a new questionnaire a condition of continuing. Explain briefly which role family the answer could unlock, ask at most three concise questions per round, and continue independent searches. Optional omissions stay unknown; silence does not relax a hard limit.

Choose from these topics rather than asking all of them:

| Unknown that matters | Useful question or input | Search consequence |
|---|---|---|
| Preferred work beyond familiar titles | Which duties would you enjoy or accept: customer training, sales follow-up, scheduling/dispatch, order support, event coordination or hands-on operations? | Adds adjacent families based on tasks rather than senior-sounding titles |
| Sales conditions | Are outbound calls, targets, variable pay, store sales or field visits acceptable? Is the pay floor guaranteed base? | Separates a sales opportunity from an unsuitable commission arrangement; preserve the saved base floor |
| Physical or driving requirements | Do you hold the specific licence, drive the required transmission, and meet the stated lifting or vehicle-task requirements? | Licence, clean driving record, physical work and mechanical knowledge are separate facts; one answer does not prove the others |
| Job-specific tool depth | What have you personally done in the named CRM, email platform, spreadsheet or design tool, and which steps can you perform unaided? | Maps transferable tools honestly and identifies a demonstrable gap rather than inventing proficiency |
| Languages or regulated credentials | Which relevant languages and current licences/certificates can you use at work? | Tests explicit role requirements without inferring ability or eligibility from a name or background |
| Contract or training route | Would a paid fixed-term, seasonal, trainee or apprenticeship role work, and is a mandatory training schedule feasible? | Opens routes at major employers without assuming all training is remote or waiving required student/degree status |
| Geographic expansion | If the current area produces too few roles, would you change the cities or attendance limit? | Ask only when useful or invited; show the tradeoff and keep the existing boundary until explicitly changed |
| Employer priorities and relationships | Which supplied companies matter most, and do you have a referral or previous application there? | Prioritizes effort and checks history; a referral is not contact permission or a promise of access |

A useful input is a short example of doing a relevant task, a redacted work sample, or an existing portfolio link. No new CV, paid account, referral, home address or assessment is required. Keep proposed learning separate from demonstrated ability. Use [search angles](search-angles.md) to turn answers into bounded searches.

For a continuing campaign, use the [live-requirement feedback loop](answer-bank.md#learn-from-live-requirements) to retain dated answers, refine searches and avoid asking the same compatible question again.

## Private files

Use a user-designated private directory outside the public repository and skill installation. Suggested layout:

~~~text
private-job-search/
  profile.json
  evidence.json
  tracker.json
  search_state.json
  vacancies.json
  candidate-brief.json
  application-answers.json
  run_metrics.json
  employer-targets.json
  company-coverage.json
  search-plan.json
  sources/
  research/
  interviews/
  applications/<attempt-id>/
~~~

Copy [profile.template.json](profile.template.json) there when structured preferences help. It is a starter, not a required exhaustive questionnaire. Preserve unknown values as null and empty arrays as unspecified, not proof of inability. Profile changes must reflect user statements or reconciled evidence. Never personalize the shipped template or examples in place.

All files are optional. Use [answer-bank.md](answer-bank.md) for repeated application questions and [interviews.md](interviews.md) for reusable stories and practice notes; these are derived drafts, not new evidence or submission. Keep employer research separate from candidate claims. The compact candidate brief is a dated working summary with a profile revision and pointers to evidence, not a second independent source of truth. Refresh it when the candidate corrects a claim or changes constraints. Read detailed evidence only when a match needs it; an unchanged supplied workbook can reuse its extraction after file identity/hash checks. Reusing candidate evidence does not refresh a job posting's availability. See [efficiency.md](efficiency.md) for the vacancy ledger and run metrics and [tracking](tracking.md#working-tracker-and-reconciliation) for working-view ownership. Preserve older `discoveries.json` records and consult pending/unreported entries during upgrades; a seen ID does not prove assessment or delivery.

## Evidence register

Each reusable claim should contain:

| Field | Meaning |
|---|---|
| claim_id | Stable local identifier |
| claim | Specific task, result or skill |
| source | File/page/section or user statement and date |
| personal_contribution | What the candidate actually did |
| assistance | Team, AI or other support; unknown if unresolved |
| capability_level | independent / assisted / exposure / learning / unknown |
| outcome | Observed result, with units and scope; no invented metrics |
| permitted_wording | Accurate résumé wording and limitations |
| verified_at | Date of the evidence review, not an assertion it remains current forever |

The register is optional for small tasks; the distinctions are not. Do not turn all a course's learning outcomes into the candidate's skills. A completion certificate supports completion, while practical competence needs separate evidence. A company-wide metric is not automatically the candidate's achievement. Private client/employer details require appropriate redaction in public samples.

If the candidate corrects a capability claim, keep the correction and reconsider affected matches. For example, “I use spreadsheets but cannot write formulas unaided” overrides a broad spreadsheet-proficiency inference. Invite a short practical demonstration when it would resolve a material gap, rather than inventing a skill level.

## Refreshing and portability

Keep the reusable skill unchanged when a different person uses it. Read that person's workspace explicitly. Do not merge two candidates' profiles or silently reuse the last candidate's preferences. Date-stamp changes in goals and constraints; ask only about stale facts that matter to a current decision.

Use a new profile revision after a material change. Reassess affected cached matches against that revision; do not reuse an old fit assessment just because the employer's posting is unchanged.
