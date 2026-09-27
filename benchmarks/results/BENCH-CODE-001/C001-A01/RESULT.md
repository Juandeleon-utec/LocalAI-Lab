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


## Frozen artifacts

Candidate commit:

```text
00156c7a0bdb783ec55e7b930c693dd5b388b96b
```

Candidate archive SHA-256:

```text
fa3b507710cc951014c0ab357498e69806cdfb710a58c3dd70007d6cca96442a
```

OpenCode event log SHA-256:

```text
54bd951fa1366aff2b8b595f927b2c17a39c93ec2793ad08ab030654fa7873ae
```

OpenCode stderr SHA-256:

```text
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

The stderr hash is the SHA-256 of an empty file.

Evaluation JSON SHA-256:

```text
60923e4bbb87e1cd3d43984e97d36120cc477080511ac45bac2aee9b79dc76fd
```

Inference/telemetry artifacts:

```text
llama-server.log
02c835c7cafd0d384f00d48b655f6a0c79f1baa6bca9592d8fa3b935fbef1378

llama-metrics-before.prom
033056262d2dfed7ee1a6103733a5e445b13fb53daaa6de97304ae73a95d0f36

llama-metrics-after.prom
feb4fa86f575674697093f5db10f32ca76c01474425ec9682f45a13d3c90b292

amd-smi.csv
6ea6debd63d75b23dc412fac7fb235df597acd4cc718896c7bd855e635719122
```

Observed workspace measurement after generation:

- files: 1156
- total bytes: 7,126,210

This workspace measurement includes installed dependencies such as `node_modules`; it is not used as the canonical source-artifact size. The Git candidate archive is the canonical frozen candidate artifact.
