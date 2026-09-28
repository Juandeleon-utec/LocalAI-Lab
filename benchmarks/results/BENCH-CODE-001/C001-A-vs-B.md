# BENCH-CODE-001 — C001-A vs C001-B

This document compares the completed three-run samples under BENCH-CODE-001 v1.0.

## Configurations

| Series | Agent | Model | Quantization | Context | MTP |
|---|---|---|---|---:|---|
| C001-A | OpenCode 1.18.27 | Qwen3-Coder-30B-A3B-Instruct | Q3_K_M | 32768 | no |
| C001-B | OpenCode 1.18.27 | Qwen3.6-35B-A3B | Q4_K_M | 32768 | no |

The series differ in model and quantization and therefore should be interpreted as configuration-level benchmark results, not an isolated architecture-only comparison.

## Functional result

| Metric | C001-A | C001-B |
|---|---:|---:|
| Independent repetitions | 3 | 3 |
| Successful clean deployments | **3/3** | **0/3** |
| Hidden tests after clean deployment | **48/48** | not run: deployment failed first |
| Critical hidden tests | **42/42** | not run: deployment failed first |
| Human interventions during formal generation | 0 | 0 |

C001-A reproduced the full functional outcome in all three runs. C001-B produced no candidate that completed the clean deployment contract.

The earlier B01/B02 scores obtained in the presence of a residual MySQL service are explicitly superseded and are excluded from this comparison.

## Runtime and inference

| Metric | C001-A | C001-B |
|---|---:|---:|
| Total wall time | 1589 s | 6022 s |
| Mean wall time | 529.7 s | 2007.3 s |
| Median wall time | 567 s | 1641 s |
| Uncached prompt tokens | 70603 | 279628 |
| Cached prompt tokens | 1493402 | 2986757 |
| Generated tokens | 32364 | 93380 |
| Prompt processing time | 84.779 s | 402.878 s |
| Generation time | 693.917 s | 2232.336 s |
| Aggregate prompt throughput | **832.79 tok/s** | **694.08 tok/s** |
| Aggregate decode throughput | **46.64 tok/s** | **41.83 tok/s** |
| Aggregate cache ratio | **95.49%** | **91.44%** |

Relative to C001-A, C001-B used:

- **3.96x** as many uncached prompt tokens;
- **2.89x** as many generated tokens;
- **3.79x** the total wall time;
- approximately **16.7% lower** aggregate prompt throughput;
- approximately **10.3% lower** aggregate decode throughput;
- a prompt cache ratio lower by about **4.05 percentage points**.

Because B02 hit the 60-minute stop condition, mean wall time is strongly affected by the timeout. Median wall time is also substantially larger (1641 s vs 567 s).

## Benchmark-scoped conclusion

Under BENCH-CODE-001 v1.0 and these exact evaluated configurations:

- OpenCode + Qwen3-Coder-30B-A3B-Instruct Q3_K_M achieved **3/3 successful repetitions**, passing all **48/48 hidden tests** and **42/42 critical tests**.
- OpenCode + Qwen3.6-35B-A3B Q4_K_M achieved **0/3 successful clean deployments**. Hidden functional tests were not run after the clean redeployments because each artifact failed before the healthy-application gate.

This evidence supports a configuration-level comparison for this benchmark only. It should not be generalized into a population-level reliability estimate or a universal claim about either model family.
