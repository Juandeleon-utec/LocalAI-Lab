# C001-B01 — Formal Result

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

- started: `2026-09-27T19:18:52Z`
- ended: `2026-09-27T19:46:12Z`
- wall time: 1641 s
- termination reason: `agent_declared_completion`
- OpenCode exit code: 0
- OpenCode final step reason: `stop`
- human interventions: 0

## Hidden evaluator

BENCH-CODE-001 v1.0 evaluator result:

```text
tests_passed=13
tests_total=16
critical_tests_passed=11
critical_tests_total=14
all_tests_passed=false
all_critical_tests_passed=false
```

Failed tests:

- T01 — health endpoint and database readiness: health returned 200 but evaluator observed `fk_count=0`.
- T04 — password storage/database inspection: evaluator could not inspect `bench_code_001.users`.
- T12 — cross-user modification/deletion: cross-user DELETE was denied, but cross-user PUT returned 400 rather than the evaluator's expected ownership-denial response.

The run completed autonomously and normally, but did not satisfy the complete hidden functional contract.

## Frozen artifacts

Candidate commit:

```text
36e3ca647954b8291d4dfdb11447d1dfb330ac03
```

Candidate archive SHA-256:

```text
6141ec8794e1360bfe4e29a1aac9c90ab82622d4a5df6f3d596ebb3ad002918e
```

OpenCode event log SHA-256:

```text
2bebdc77d51297115e4285b9819aba53fc101852c9179a6bd59b497650ac23f0
```

OpenCode stderr SHA-256:

```text
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

Evaluation JSON SHA-256:

```text
68da6978dd3cdfe74777564420b9bc6b0329c6212eb86db3e7edfa56c06a13bc
```

Inference/telemetry artifacts:

```text
llama-server.log
98df3c7881eb319b534b180380dfcab4322fefb113473085d43a34000ed1a745

llama-metrics-before.prom
3f0ccacb4e9bf70dba3dc48bb09b12cd779d75b2db18f784a02d87310b0ee01b

llama-metrics-after.prom
d3a1fb57d5a073c979c74319beda499f83260af6a182760b6b39e7ad1ce73c60

amd-smi.csv
6aa4ad6c96180a4b7bf6c2d91cf894662bea697d3b55237f4f1f5572b85916f7
```

## Throughput instrumentation

Run-isolated values calculated from the delta between the pre-run and post-run llama.cpp Prometheus counters:

| Metric | C001-B01 |
|---|---:|
| Uncached prompt tokens | 144697 |
| Cached prompt tokens | 1277791 |
| Generated tokens | 48154 |
| Prompt processing time | 203.802 s |
| Generation time | 1153.161 s |
| Prompt throughput | 709.99 tok/s |
| Decode throughput | 41.76 tok/s |
| Prompt cache ratio | 89.83% |

The end-of-run gauges were consistent with the counter-delta calculation:

- `llamacpp:prompt_tokens_seconds = 709.988`
- `llamacpp:predicted_tokens_seconds = 41.6846`

Inference time (prompt processing + generation) was 1356.963 s, or 82.69% of the 1641 s end-to-end wall time. The residual wall time outside these llama.cpp inference counters was approximately 284.04 s.
