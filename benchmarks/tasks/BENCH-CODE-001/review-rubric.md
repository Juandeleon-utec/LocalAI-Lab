# BENCH-CODE-001 v1.0 — Blinded Human Review

Functional correctness is determined by the independent evaluator. Human review is a separate qualitative outcome and must not override failed critical tests.

When practical, present candidates as anonymous Candidate A/B/C.

## Review dimensions

Use a 1–5 ordinal rating for each dimension and add short evidence notes.

| Dimension | Review question |
| --- | --- |
| Usability | Can a normal reviewer register, log in and manage records without confusion? |
| Readability | Are names, functions and modules understandable without excessive mental effort? |
| Maintainability | Could another developer modify the application without first rewriting it? |
| Structure | Are responsibilities separated reasonably without unnecessary architecture? |
| Error handling | Are ordinary failure cases handled clearly and consistently? |
| Documentation | Can the reviewer install, configure and run the project from README instructions? |
| Code compression | Is code excessively condensed, dense or merged in ways that harm maintainability? |
| Unnecessary complexity | Did the implementation introduce abstractions/dependencies that are disproportionate to the task? |

## Reviewer prompts

Record short answers:

1. What is the strongest aspect of this implementation?
2. What is the most important maintainability problem?
3. Is any part of the code unnecessarily compressed?
4. Is any part unnecessarily complex?
5. Would you be comfortable making a small feature change in this codebase?
6. Were README/setup instructions sufficient?

## Blinding

Do not reveal model/agent identity before the initial review form is completed.

After review, candidate identities may be disclosed for interpretation, but the original blinded ratings must remain unchanged.
