# Local AI coding benchmark — executive scorecard

**As of 2026-10-16.** Source runs: [Qwen aggregate](./C001-A-SUMMARY.md), [Gemma closure](./GEMMA4-LAB-001-FINAL-REPORT.md), [Gemma records](./GEMMA4-LAB-001-2026-10-16.md). Scores are original BENCH-CODE-001 v1.0; Qwen has three repetitions, Gemma one per configuration except two Q3 OFF attempts.

## At a glance

| Model/profile | GGUF | Thinking | Wall time (s) | OpenCode exit | Functional tests | Critical | Human interventions |
|---|---|---|---:|---:|---|---|---:|
| Qwen3-Coder-30B-A3B (A01) | Q3_K_M | Qwen baseline | 436 | — | **16/16** | 14/14 | 0 |
| Qwen3-Coder-30B-A3B (A02) | Q3_K_M | Qwen baseline | 567 | — | **16/16** | 14/14 | 0 |
| Qwen3-Coder-30B-A3B (A03) | Q3_K_M | Qwen baseline | 586 | — | **16/16** | 14/14 | 0 |
| **Qwen mean** | Q3_K_M | — | **529.7** | — | **3/3 fully passing** | 3/3 fully passing | 0 |
| Gemma 4 26B-A4B Q3 OFF (attempt 1) | Q3_K_M | OFF | 337 | 0 | Not evaluated | — | 0 |
| Gemma 4 26B-A4B Q3 OFF (attempt 2) | Q3_K_M | OFF | 205 | 0 | Unscored: db:init hangs | — | 0 |
| **Gemma 4 26B-A4B Q3 ON** | **Q3_K_M** | **ON** | **377** | **1** | **16/16 PASS** | **14/14** | 0 |
| Gemma 4 26B-A4B IQ4 OFF | IQ4_XS | OFF | 758 | 0 | Unscored: missing mysql2 | — | 0 |
| Gemma 4 26B-A4B IQ4 ON | IQ4_XS | ON | 392 | 0 | **13/16 FAIL** | 11/14 | 0 |

**Interpretation:** only Gemma Q3 ON fully passed. Its 377 s generation took 28.8% less wall time than the Qwen three-run mean (529.7 s), but a single Gemma result is not a speed or reliability generalization. Gemma Q3 ON OpenCode exit=1 despite functional PASS. Unscored cases are not 0/16.

## Memory, context, tokens and throughput

| Metric | Qwen3-Coder baseline | Gemma Q3 OFF | Gemma Q3 ON | Gemma IQ4 OFF | Gemma IQ4 ON |
|---|---|---|---|---|---|
| GPU | AMD RX 9060 XT 16 GB (reported lab configuration; historical hardware confirmation required) | RX 9060 XT 16 GB | RX 9060 XT 16 GB | RX 9060 XT 16 GB | RX 9060 XT 16 GB |
| GGUF file size | **not verified in comparison records** | ~12.7 GB | ~12.7 GB | ~13.6 GB | ~13.6 GB |
| Serving context in benchmark | 32,768 | 32,768 | 32,768 | 32,768 | 32,768 |
| Production Qwen configured context | 114,688 (separate operational profile, **not benchmark**) | n/a | Long-context extension **not yet validated** | n/a | n/a |
| Windows Docker allocation | 16 CPU / ~16.71 GB | 16 CPU / ~16.71 GB | 16 CPU / ~16.71 GB | 16 CPU / ~16.71 GB | 16 CPU / ~16.71 GB |
| Measured formal decode speed | **46.64 tok/s** aggregate across A01–A03 | **not collected** | **not collected** | **not collected** | **not collected** |
| Exploratory generation rate | not comparable | ~54.13 tok/s | ~52.82 tok/s | ~52.02 tok/s | ~51.45 tok/s |
| Reported VRAM use (exploratory) | not directly measured in comparable Gemma test | ~13,608 MB | not separately verified | ~14,375 MB | not separately verified |
| Exact peak VRAM, per formal run | **not available in compared records** | not available | not available | not available | not available |
| Energy per task | not available | not available | not available | not available | not available |

**Do not compare 46.64 tok/s (Qwen run-isolated formal Prometheus metric) directly with ~52.82 tok/s (Gemma exploratory single-task generation).** Different protocols/sampling. GGUF model weight size is not total VRAM; KV cache, compute buffers and GPU offload increase consumption. Report 16 GB VRAM as physical capacity, not automatically model allocation. Where metrics were not captured, write **N/D**, never zero or guessed.

Qwen formal token telemetry:

| Run | Prompt (uncached) | Cached prompt | Generated | Prompt tok/s | Decode tok/s | Cache hit ratio |
|---|---:|---:|---:|---:|---:|---:|
| A01 | 10,101 | 472,226 | 11,270 | 732.65 | 46.41 | 97.91% |
| A02 | 10,253 | 477,957 | 10,451 | 708.44 | 46.68 | 97.90% |
| A03 | 50,249 | 543,219 | 10,643 | 889.07 | 46.85 | 91.53% |
| **Aggregate** | **70,603** | **1,493,402** | **32,364** | **832.79** | **46.64** | **95.49%** |

## Environment / reproducibility

- Local server: Ubuntu 24.04.4; AMD Radeon RX 9060 XT 16 GB; ROCm 10.0. Gemma dedicated llama.cpp, Linux endpoint `192.168.2.237:8088`; operational Qwen endpoint :8080 (do not simultaneously pressure VRAM).
- Windows: OpenCode 1.18.27; Node 24.19.0, npm 11.17.0, Python 3.11.9; Docker 29.8.0; Compose v5.5.1. Gemma Windows build 10.0.26300 vs historical Qwen 10.0.26200.
- Frozen repo `23bed848a1467225a0858dbdb27e57ef2e9aa474`, prompt SHA256 `e1ec6e63a2a603a4d5591158a262d66de1f838a93e72d03ae2a158827e35dbac`, seed SHA256 `a1d24686ddf69b8d5eb69b956b1500fafa92aac8658270deff33ba3e2c1eadc7`.
- Hidden evaluator v1.0.0 located off-repository and never committed. All test outcomes reported by user from original evaluator.
- Gemma IQ4 ON errors: T10 and T12 malformed dynamic UPDATE SQL, T15 absence of expected updated title after restart; T15 is derivative of failed update, not evidence of lost MySQL rows. npm reported three high-severity vulnerabilities.
- Resume paths and commands: [operations index](./GEMMA4-LAB-001-OPERATIONS-INDEX.md). [Gemma long-context guide](./GEMMA4-Q3-THINKING-ON-CONTEXT-SETUP.md).

## Recommendation for next contest

Use independently versioned `SERENOS-CODE-001` benchmark, comparing **Qwen3-Coder vs Gemma Q3 Thinking ON** module by module, with identical starting repos and prompts, fixed acceptance tests, frozen test evidence, and explicit metrics for required corrections. See the protocol document in this repository.
