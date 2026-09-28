# C001-B02 — Formal Result

## Outcome

System:

- OpenCode 1.18.27
- local/qwen3.6
- Qwen3.6-35B-A3B Q4_K_M
- configured context: 32768
- llama.cpp build 10752
- llama.cpp commit: `b96806d96061049a5b574269b049bf6241d63d46`
- MTP: disabled

Execution:

- started: `2026-09-28T01:11:09Z`
- ended: `2026-09-28T02:11:09Z`
- wall time: 3600 s
- termination reason: `timeout_60_minutes`
- OpenCode exit code: 124
- OpenCode final step reason: unavailable because run was terminated at the formal timeout
- human interventions: 0

## Hidden evaluator

BENCH-CODE-001 v1.0 evaluator result:

```text
tests_passed=12
tests_total=16
critical_tests_passed=10
critical_tests_total=14
all_tests_passed=false
all_critical_tests_passed=false
```

Failed tests:

- T01 — health endpoint and database readiness: health returned 200 but evaluator observed `fk_count=0`.
- T02 — valid user registration: registration returned 409 because the benchmark username already existed.
- T04 — password storage/database inspection: evaluator could not inspect `bench_code_001.users`.
- T10 — owner update: GET succeeded but PUT returned 500.

T12 passed in this run: cross-user PUT and DELETE both returned 404.

The run did not complete before the 60-minute stop condition. The candidate was frozen exactly at timeout and evaluated without manual edits.

## Runtime behavior at timeout

The final OpenCode events show the agent repeatedly attempting to start and verify the application server. A residual `node src/server.js` process remained after timeout and was terminated only after the candidate archive and evaluation had already been frozen/completed. This cleanup did not modify the evaluated candidate.

## Frozen artifacts

Candidate commit:

```text
725e16faf2bb93bbb33e361b74ae0b1f8745609b
```

Candidate archive SHA-256:

```text
36e5a8464cda168be201f93e9d9877072aca4af7d56b2dfbfea0d1988170e71f
```

OpenCode event log SHA-256:

```text
30b085126f65b43d9c1f57af5a582b8022e1be57fc70d8e724a73633043d0c0f
```

OpenCode stderr SHA-256:

```text
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

Evaluation JSON SHA-256:

```text
d30d8c7dddbecc37023ce6dfbd2bb0c186198f48e09ded4b6534e70ce957bbb3
```

Inference/telemetry artifacts:

```text
llama-server.log
626791cf20747edf3c8340145ede7b9c639ac8364abfa3a3184e82c85a169dc3

llama-metrics-before.prom
033056262d2dfed7ee1a6103733a5e445b13fb53daaa6de97304ae73a95d0f36

llama-metrics-after.prom
63f4e99e77c5386b1784c31f0ff5c3af270d537649c1abc32fa19f99b2d058f7

amd-smi.csv
8f349f6e0235e9f0c3fa622835f7a9811a700a68a27bb617e9bd0741a3e2aa57
```

## Throughput instrumentation

Run-isolated token counts and throughput will be calculated from the before/after llama.cpp Prometheus counters and recorded separately.
