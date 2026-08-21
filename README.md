# Journal V2 — fixes applied

This build fixes the confirmed application bugs found during review:

- `ai_prompt_reflection()` now returns its generated prompt.
- `ai_prompt_compass()` now returns its generated prompt.
- Markdown export now handles missing/invalid mood values safely and produces a clearer export structure.
- Relationship mood lookup condition corrected.
- Calendar helper imports/undefined date handling corrected where applicable.
- Journal deletion route is protected with login and changed to POST.
- Removed obvious debug `print()` calls.
- Removed redundant mood-count initialisation.
- Trends mood axis corrected to 10.

Before deploying, review database migrations and enable CSRF protection as a separate hardening step.
