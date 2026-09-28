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

## Inference throughput

The formal runs also captured llama.cpp Prometheus counters before and after each run. Throughput below is calculated from those run-isolated deltas.

| Run | Prompt tokens | Cached prompt tokens | Generated tokens | Prompt tok/s | Decode tok/s | Cache ratio |
|---|---:|---:|---:|---:|---:|---:|
| C001-A01 | 10101 | 472226 | 11270 | 732.65 | 46.41 | 97.91% |
| C001-A02 | 10253 | 477957 | 10451 | 708.44 | 46.68 | 97.90% |
| C001-A03 | 50249 | 543219 | 10643 | 889.07 | 46.85 | 91.53% |

Across the three runs, the combined counter totals were 70603 uncached prompt tokens, 1493402 cached prompt tokens and 32364 generated tokens. Dividing total tokens by total measured llama.cpp time gives an aggregate prompt throughput of **832.79 tok/s** and aggregate decode throughput of **46.64 tok/s**. The aggregate prompt cache ratio was **95.49%**.

The decode rate was notably stable across the three independent repetitions (46.41–46.85 tok/s).
