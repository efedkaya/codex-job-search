# Prepare, practise and debrief interviews

Use the specific posting, exact application materials and the candidate's current evidence. Reuse prior role research and practice notes when relevant. For a simple question, work directly in chat; no story bank, transcript or full intake is required. Respect employer assessment-assistance rules. An AI-written answer or solution does not establish the candidate's ability.

## Reusable stories without invented evidence

For repeated preparation, optionally maintain `interviews/story-bank.json` in the candidate's designated private workspace. A minimal structure is `{"schema_version": 1, "stories": []}`; this is agent-maintained data, not a helper command. Keep a small useful set rather than generating a quota of stories per posting.

Each story can record:

| Field | Purpose |
|---|---|
| story_id / version | Stable identity and retained revisions |
| situation / task / action / result / reflection | Context, responsibility, personal steps, supported outcome, and what was learned or would change |
| competency_tags | Questions or duties this story can help address |
| evidence | Claim IDs/source pointers, with metric units, time period, scope and attribution |
| contribution / assistance / capability_level | Personal versus team work, support received and independence |
| unresolved / review_status | Missing facts and draft / reviewed / stale / retracted state |
| profile_revision / reviewed_at | The actual evidence revision and review date |

The bank organizes narrative; it cannot verify its own facts. Trace figures and scope to the evidence register or a dated candidate statement in the correct context. A matching number in another story is insufficient. Unknown results can remain qualitative; ask for missing facts without suggesting a number to confirm. Separate past actions from hypothetical approaches. Reflection must come from the candidate's experience or stay a draft prompt.

Reviewed means checked against evidence, not candidate-approved or submitted. A material correction makes affected unsubmitted stories, answers and prep stale. Retain the correction and previous versions, mark retracted claims so they are not reused, and preserve what was actually submitted. Do not convert a withdrawn claim into a skills judgment or overwrite application history.

## A plan that fits the actual round

Use the known round format, interview date/time/time zone and candidate's available active preparation time. Ask only for missing details that materially change the plan; useful generic preparation can proceed without a confirmed date. Calendar time until an interview is not all available study time. Respect work, rest and other commitments, and prioritize interview preparation within the existing search budget.

Choose a few blocks appropriate to the round: a concise background/role narrative, the most consequential task or demonstrated difficulty, selected stories, company questions, and a brief final review. Match depth to recruiter screening, hiring-manager discussion, practical/domain exercise, case presentation or panel; a round label is a clue, not proof of the questions or difficulty.

Use the [detailed requirement review](search.md#detailed-requirement-review) to select risks and evidence, rather than producing a second contradictory fit matrix. Previously demonstrated difficulties can deserve practice, but one omitted point or an unsupported résumé inference is not an established skills gap. Map relevant stories to questions and include honest answers for partial/unknown requirements.

Label question sources: employer-provided format, dated candidate/interview report with citation, or inferred from the posting/round. Publicly reported questions do not guarantee repetition. Use [company research](company-research.md) for facts that help answer “why this role” or form useful questions. Do not invent company intelligence or treat an interviewer's public biography as evidence of private preferences.

When helpful, finish with a short review card: the main fit message, a few evidence-backed examples, questions to ask, unresolved logistics and compensation already discussed. Preserve the source/date and currency/base-versus-total basis of any prior stated expectation; a market estimate is not a commitment made by the candidate.

## One-question practice

Ask one realistic question and wait for the candidate's answer. A natural follow-up can test an unclear claim or a deeper decision before feedback. Keep role-play clearly simulated; do not imply the real interviewer said something.

Give concise feedback on what worked, the most useful change and a tighter opening/ending that preserves the facts. Distinguish explanation, missing evidence and demonstrated task difficulty. For a behavioral answer, prompt for the candidate's own actions, supported result and reflection when missing. Help vary examples when useful without declaring a reused story inherently wrong.

For a practical question, explain what the task tests, let the candidate attempt it, then discuss reasoning, checks and tradeoffs. Do not coach unsupported metrics into a polished answer. Resolve a disputed factual claim against its actual source; mark unresolved facts instead of defending the prep file's wording. In typed practice, assess structure and relevance; do not claim to have measured spoken duration, delivery, accent or filler words.

## Debrief the real interview

Use a supplied transcript or notes before asking the candidate to reconstruct the same material. Label the input as transcript, contemporaneous notes or later recall; partial transcripts and recollections remain incomplete. Do not invent missing questions, speaker labels, reactions or tone. Preserve original supplied material; do not record an interview or collect unrelated communications under this workflow.

Capture questions asked, the candidate's answer, any explicit feedback/process details, what worked, one useful improvement and next-round actions. Keep the candidate's interpretation of a reaction separate from an observed statement; neither establishes a hiring probability or employer motive. Separate candidate statements from questions or hypothetical examples when assessing evidence.

Optional practice/question notes can retain the role/round, source, question, answer summary, demonstrated difficulty and next exercise. New factual candidate claims still need the normal evidence review before reuse. Add genuine new experiences to the story bank; do not infer competence from fluent phrasing alone.

When the interview contradicts an earlier employer/role fact, update the current research/prep summary with the dated new source and preserve the previous observation. Keep this separate from candidate-claim corrections and exact submitted versions. Record only supported tracker events using [tracking](tracking.md); a practice session is not an interview_completed event. A debrief or due follow-up grants no permission to contact anyone.
