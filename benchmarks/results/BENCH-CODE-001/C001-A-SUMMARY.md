# C001-A — Aggregate Result

Configuration:

- OpenCode 1.18.27
- Qwen3-Coder-30B-A3B-Instruct Q3_K_M
- model id: `local/qwen3-coder`
- configured context: 32768
- BENCH-CODE-001 v1.0
- three independent clean runs

## Aggregate functional outcome

| Run | Wall time (s) | Tests | Critical tests | Human interventions |
|---|---:|---:|---:|---:|
| C001-A01 | 436 | 16/16 | 14/14 | 0 |
| C001-A02 | 567 | 16/16 | 14/14 | 0 |
| C001-A03 | 586 | 16/16 | 14/14 | 0 |

Across the three runs:

- successful runs: **3/3**
- hidden tests passed: **48/48**
- critical hidden tests passed: **42/42**
- human interventions: **0**
- mean wall time: **529.7 s** (8 min 49.7 s)
- median wall time: **567 s**
- minimum wall time: **436 s**
- maximum wall time: **586 s**
- sample standard deviation: **81.7 s**

## Interpretation

For this benchmark, hardware/software profile and three-run sample, the local OpenCode + Qwen3-Coder configuration reproduced the primary functional outcome in all three independent executions.

This should be reported as **3/3 successful repetitions**, not as a general 100% reliability claim. The sample size is intentionally small and supports repeatability evidence for BENCH-CODE-001, not a population-level reliability estimate.

All three candidate archives, evaluator outputs, OpenCode event logs and inference telemetry streams were fingerprinted independently.
