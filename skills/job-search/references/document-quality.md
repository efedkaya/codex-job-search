# Check the actual application document

Use for a finished résumé, cover letter, application answer or a requested document audit. Scale the checks to the requested output; a short chat edit does not need a file pipeline. Keep content review, exported-file checks and submission verification separate.

## Three independent questions

| Check | What establishes it | What it does not establish |
|---|---|---|
| Grounding | Compare each changed claim with candidate evidence in its employer/project/period context | A number or keyword appearing somewhere in the source is not proof of this claim |
| Targeting and writing | Compare selected examples, emphasis and wording with this posting and the candidate's requested voice | A fluent letter or a high similarity score is not evidence of capability or hiring odds |
| File integrity and readability | Inspect the final saved file, render its pages and extract its text using available tools | Source text, a successful compile or one parser does not prove every employer system will accept it |

## Review content, then export

First fix factual drift, wrong company/role/contact information, unresolved placeholders and consequential omissions. Then improve the clearest role-specific evidence and remove repetition. Treat style suggestions as suggestions; do not erase accurate assistance, qualitative outcomes, names or meaningful non-English characters to satisfy a generic writing rubric.

Compare relevant posting terms with the actual text. Classify each useful term as present, supported but absent, unsupported, or unresolved. Add only supported wording that fits naturally, with its real capability level. Keep abbreviations/expanded forms where useful, but do not treat distinct concepts as synonyms, such as unit testing and test-driven development. Preserve genuine gaps instead of forcing coverage.

## Inspect the final export

Use the available format-specific document tools. Check the saved result after the latest edit, not a previous preview:

- Open every exported page. Look for clipped content, overlapping lines, stranded headings, an employer/title separated from its bullets, unreadably small text, accidental blank pages and excessive gaps caused by unbreakable blocks. A page limit comes from the task, employer or chosen layout; there is no universal one-page résumé rule.
- Read back extracted text. Check the name and required contact details, critical employer/title/date associations, section order and important evidence. Compare with the intended source to find missing text, mixed columns, broken ligatures, replacement characters or icon-only contact details. A two-column design is a risk to inspect, not an automatic failure.
- Check actual file type, size and page count against the employer's stated requirements. Check visible link labels and destinations with available tools. Inspect the target before making a public or private link claim; a local path alone does not prove another person can access it.
- Check Word files for unintended tracked changes/comments and exports for unwanted template instructions, sample data or hidden keyword stuffing when the available tools expose these. Do not silently remove the candidate's meaningful review history from their working original.
- For form answers, count the final text against the actual character/word rule, then inspect what the form retained. A local counter is not proof that the platform uses the same counting convention.

Repair the observed problem and repeat affected checks. If a converter/parser is unavailable, report that part as not checked and still complete independent content work. Do not install a tool, alter the candidate's system, or upload private documents to a public checker solely to obtain a score. Stop and explain an unresolved tool/layout limit rather than claiming readiness after repeated failed exports.

Record a compact final check with the material ID/version, path, relevant file hash, the checks actually performed, remaining issues and reviewer/source pointers. Hashes identify bytes; they do not certify their contents. Keep the exact version attached to an application consistent with that record.

## Optional offline mechanical helper

`scripts/check_materials.py` uses the Python standard library for text/DOCX and optionally an already installed `pypdf` or `pdftotext` for PDFs. It reads files and prints JSON; it does not change them, contact a service, render pages, judge facts, calculate an ATS score or authorize submission.

Write its UTF-8 input in the designated private workspace. File paths are absolute; the input can contain `files`, `answers`, or both. Example values below are fictional and must be replaced with the actual requested checks:

~~~json
{
  "files": [{
    "label": "Selected-role resume",
    "path": "/absolute/private/applications/attempt-id/resume.pdf",
    "required_text": ["casey@example.test", "Example Company", "Research Assistant"],
    "expected_order": ["Experience", "Education"],
    "forbidden_text": ["Wrong Employer"],
    "max_pages": 2
  }],
  "answers": [{
    "label": "Why this role?",
    "text": "The actual final answer to check.",
    "max_characters": 500
  }]
}
~~~

~~~text
python /absolute/skill/scripts/check_materials.py --input /absolute/private/material-check.json
~~~

Optional file checks are `max_bytes` and `expected_sha256`; optional answer limit is `max_words`. Expected text/order checks normalize Unicode compatibility forms, whitespace, curly quotes and dash variants, but do not invent semantic equivalence. Select meaningful anchors rather than dumping the whole evidence register into the input. An absent anchor may be extraction damage, a wording change or an intentional omission: resolve it against the actual file.

Exit 0 means the requested mechanical checks passed; 1 means an observed check failed; 2 means invalid input or a requested check could not be completed. Read the findings and `not_checked` fields, not only the exit code. DOCX XML order is not rendered page order, PDF reading order still needs comparison, and neither pass nor failure establishes general ATS compatibility. Character counts are Unicode code points; word counts are whitespace-delimited. The final factual, visual and attachment reviews remain separate.
