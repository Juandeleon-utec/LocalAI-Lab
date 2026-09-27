# C001-A01 — Formal Result

## Outcome

System:

- OpenCode 1.18.27
- local/qwen3-coder
- Qwen3-Coder-30B-A3B-Instruct Q3_K_M
- configured context: 32768
- llama.cpp build 10752
- llama.cpp commit: `b96806d96061049a5b574269b049bf6241d63d46`

Execution:

- started: `2026-09-27T13:33:41Z`
- ended: `2026-09-27T13:40:58Z`
- wall time: 436 s
- human interventions: 0
- agent log ended with a normal OpenCode `step_finish` reason `stop`
- launcher failed to retain the numeric OpenCode exit code, so its derived `agent_process_error` label is treated as an instrumentation defect rather than candidate failure

## Hidden evaluator

BENCH-CODE-001 v1.0 evaluator result:

```text
tests_passed=16
tests_total=16
critical_tests_passed=14
critical_tests_total=14
all_tests_passed=true
all_critical_tests_passed=true
```

All hidden tests passed, including:

- health and database readiness;
- registration/login/password hashing;
- authenticated CRUD;
- per-user record isolation;
- cross-user retrieve/update/delete denial;
- invalid payload handling;
- persistence after application restart;
- representative injection-style authentication/ownership checks.

## Engineering interpretation

C001-A01 is a **fully successful autonomous functional run** under the BENCH-CODE-001 v1.0 primary engineering outcome:

> independent hidden functional tests passed without human intervention.

The OpenCode exit-code capture bug does not change the hidden-evaluator result and must be corrected before A02 so that termination metadata is captured reliably without changing the participant prompt, evaluator, model, staging environment, or primary outcome.

## Still to archive

Before closing A01 completely, preserve:

- candidate commit SHA;
- candidate archive SHA-256;
- OpenCode event-log SHA-256;
- server log SHA-256;
- telemetry CSV/log hashes;
- before/after llama metrics hashes;
- summarized telemetry statistics.
