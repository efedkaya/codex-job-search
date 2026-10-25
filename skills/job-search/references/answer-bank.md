# Reusable application answers

Use only when repeated questions make a private answer bank useful. For one form, the per-attempt record in [applications.md](applications.md) is sufficient. This is an optional agent-maintained JSON record, not a new helper command, factual authority or authorization to autofill/submit.

## Private record

Store `application-answers.json` in the candidate's designated private workspace. A simple structure is `{"schema_version": 1, "answers": []}`. Give each answer a stable local `answer_id` and preserve versions rather than replacing reviewed/submitted wording.

| Field | Record |
|---|---|
| answer_id / version | Stable answer identifier and incrementing version |
| question | Exact original wording, relevant help text, choices and limits |
| answer | Reusable draft wording; do not turn unresolved facts into assertions |
| origin | Application attempt ID, employer, role and source/form reference |
| scope | Applicable employer/role/country, language, question meaning and any other restriction; global only when the evidence supports reuse across contexts |
| evidence | Claim IDs/source pointers or dated explicit candidate statements; company research and job requirements do not establish candidate facts |
| profile_revision / reviewed_at | Candidate profile revision and actual review date; use null if not reviewed |
| status | draft / reviewed / stale; reviewed means checked against evidence, not candidate-approved or submitted |
| unresolved | Missing facts, ambiguity, changed conditions or needed candidate decisions |
| supersedes | Prior version reference where applicable; retain older versions and attempt snapshots |

## Reuse procedure

1. Inspect the new question and its context. Similar words can ask different things: current authorization versus future sponsorship, total versus tool-specific experience, base salary versus total compensation. Compare country, employer, role, language, choices and field limits before selecting an answer.
2. Check the current evidence and profile revision. A revision change triggers reassessment, not blind reuse; a relevant correction makes affected answers and unsubmitted drafts stale. Recheck changeable facts such as authorization/sponsorship, salary expectations, start date, notice period, availability and work arrangement. Ask only for missing facts or decisions that change the answer; never derive these from a name, location, model confidence or market midpoint.
3. Adapt the answer as a new draft/version and measure applicable limits. Preserve reviewed versions when a form is reread or recaptured. Optional unresolved fields can remain unanswered when the form permits; required unresolved facts follow the application submission rules. Sensitive self-identification and attestations require the candidate's own supplied choices; do not infer them or reuse them outside their stated scope.
4. Save the exact question and final answer used under the specific application attempt. Bank review, candidate approval, form entry and successful submission remain distinct; a corrected reusable answer must not rewrite earlier submitted history.

No full CV, private account sidebar, credentials or unrelated form data belongs in an answer record. Store only what supports the answer and its reuse.

## Learn from live requirements

Use actual posting requirements and screening questions to identify material unknowns. Before asking, check the private profile and answer bank; ask only what could change search scope, fit or a selected application's answer. Preserve the source question and the candidate's exact reply alongside any proposed wording. A reply to one part of a bundled question leaves the other parts unknown.

When the candidate answers, update the relevant private facts/preferences and reusable answer record, then reconsider affected search queries, exclusions and unsubmitted drafts. Keep the change's source and date. A correction supersedes conflicting current wording without rewriting submitted history. Reuse compatible, current facts in future drafts; ask again only for missing, ambiguous or materially stale information. Reusable facts do not authorize sensitive attestations, selecting new jobs or performing a reserved final Send/Submit.
