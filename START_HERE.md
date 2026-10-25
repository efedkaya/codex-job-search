# Try Codex Job Search

**Preview version 0.4.0 · A short guide for friends testing the package**

This skill helps you describe the work you want, find relevant openings and understand why a job might fit. You choose the search size and decide what to apply for.

This is a local skill package with an optional ChatGPT conversation starter, not a published marketplace plugin. The Codex steps below use local file access; attaching the ZIP to a chat does not install a native plugin or create account memory. See [validation notes](VALIDATION.md) for the checks performed and environments still untested.

## Start in a ChatGPT conversation

Attach the package to your own chat and paste [CHATGPT_STARTER.txt](CHATGPT_STARTER.txt). If the chat cannot read archives, extract and attach skills/job-search/SKILL.md plus references/first-run.md, references/employer-priorities.md and references/priority-employers.json from that skill folder. Supply further references only when needed. The assistant must say which files it could actually read.

It will ask a few background questions, then refine the search using your answers and real job requirements. The 241 shared companies are prioritized unless you change that preference. Your constraints still govern fit. A résumé or portfolio is optional.

Keep the updated PROFILE_CONTEXT.md it produces. When private file storage is unavailable, this is a copyable handoff rather than a promise of permanent memory; supply the context and workflow in a future chat when needed. The assistant may use host memory only on your explicit request with an available authorized feature. It must distinguish in-chat context, saved files and actual account memory.

## 1. Open the package in Codex

Extract the ZIP into a folder on your computer. Open that extracted folder as a project in Codex. Opening the ZIP itself is not enough.

You will need:

- **Local file access** to read the package, install the skill and save your private search files.
- **Web access** to find and verify current vacancies. Without it, you can still review postings you paste in.
- **A supported browser connection**, if you want to use signed-in job-board pages. Public employer sites can also be useful. Sign in yourself if needed; do not paste passwords or access tokens into chat.

You do not need terminal experience. Python is optional for the copy-based installation route; it is needed for the included installer and tracking helpers. Your Codex account's normal usage limits still apply.

## 2. Ask Codex to install it

Copy this into the Codex chat opened in the extracted folder:

```text
Read START_HERE.md and README.md in this folder, then install the included job-search skill locally for this Codex host. Use the included tools/distribute.py installer if a suitable Python is available; otherwise copy the entire skills/job-search folder into a skill directory supported by this host. Follow the current documented skill location, and do not change broad app permissions or configuration.

If job-search is already installed, compare it first. Keep an identical installation as it is. Before replacing a different installation, preserve the entire existing folder in a dated backup outside active skill directories and verify the backup. If you cannot preserve it safely, leave it unchanged and explain the issue.

Verify the installed files and tell me how to select the skill in this host. Keep all personal information outside the package and installed skill.
```

The installer defaults to `~/.agents/skills/job-search` and refuses to overwrite a different installation. Codex may need to handle a backup before updating. A project-only installation can use `.agents/skills/job-search`. The [README](README.md) has the optional terminal commands and other supported-location guidance.

Codex normally detects new skills. If `job-search` does not appear in the host's skill selector, restart Codex and try again. See [OpenAI's skill documentation](https://developers.openai.com/codex/skills) for current host support and discovery locations.

## 3. Set up your search

Select `job-search` using the host's skill selector, or copy this prompt with `$job-search` included:

```text
Use $job-search to help me look for work. First help me set up a private profile outside both this package and the installed skill. Ask two or three useful questions at a time, skip information I have already provided, and let me answer in plain language.

Start with the roles I want, my location and where I can work. Then gather only the missing information you need about my experience, skills, CV, portfolio, work preferences and hard job limits. My CV is optional: I can describe my background in chat. If I share portfolio work, distinguish what I did independently from assisted work or coursework.

Use the bundled 241-company seed as a configurable priority, while applying my own country, location, pay, experience and skills. Save my scoped answers and keep a dated context snapshot in my private workspace; reuse compatible current answers and ask again only about material missing or changed details. Leave final application Send/Submit to me.

Before searching, agree a session budget and shortlist size with me. Suggest a manageable first trial, and let me choose a different budget. Explain any missing web or browser access and what you can still do with the access available. Do not invent candidate details or submit applications or send messages for me.
```

Useful details include your preferred roles, city or region, remote/on-site preference, commute limits, hours, salary needs and any relevant work-eligibility constraints. Share what changes the search; an exact home address is unnecessary. A CV or portfolio can help, but neither is required to begin.

## 4. Try one small search

A 20–30 minute trial is a useful starting point. You can choose a shorter or longer session. Once your basic profile is ready, try:

```text
Use $job-search for a targeted trial within our agreed budget. Return up to five strong, verified matches, with the job link, fit evidence, important gaps or unknowns, and the best next action for each. Return fewer if you cannot justify five. Avoid duplicate vacancies and tell me which sources you checked, which were blocked and what remains unfinished. Save enough private progress to continue later.
```

You can also paste one posting and ask the skill to assess it before doing a search. A full audit of every reachable results page is a separate choice and can take several sessions.

Check whether the recommendations respect your hard limits and whether the explanation matches your actual experience. On a second run, ask for new or changed opportunities since the last successful search and watch for repeated vacancies.

## 5. Share feedback

Copy [FEEDBACK.template.md](FEEDBACK.template.md), fill in the useful parts and send it manually to the friend who shared this ZIP. One good match and one poor match, with a short explanation, are especially helpful.

You can also use [GitHub Issues](https://github.com/efedkaya/codex-job-search/issues/new/choose) to send sanitized feedback or report a problem publicly.

The package does not collect or send feedback automatically. Remove personal details, CV text, private profile or tracker files, account information and credentials before sharing. Use fictional examples if you need to illustrate a problem. Keep your real search files in your private workspace.
