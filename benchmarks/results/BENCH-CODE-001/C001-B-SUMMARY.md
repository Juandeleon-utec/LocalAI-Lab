# C001-B — Aggregate Result

Configuration:

- OpenCode 1.18.27
- Qwen3.6-35B-A3B Q4_K_M
- model id: `local/qwen3.6`
- configured context: 32768
- MTP: disabled
- BENCH-CODE-001 v1.0
- three independent formal agent runs
- clean redeployment performed after removal of residual candidate-created services

## Aggregate functional outcome

| Run | Wall time (s) | Agent termination | Clean deployment | Hidden evaluator |
|---|---:|---|---|---|
| C001-B01 | 1641 | agent declared completion | FAIL — DB connection resolved to 3306 | not run |
| C001-B02 | 3600 | formal timeout | FAIL — tracked dotenv configuration forced 3306 at startup | not run |
| C001-B03 | 781 | agent declared completion | FAIL — SQL migration error during db:init | not run |

Across the three clean deployments:

- successful clean deployments: **0/3**
- human interventions during formal agent generation: **0**
- total wall time: **6022 s**
- mean wall time: **2007.3 s** (33 min 27.3 s)
- median wall time: **1641 s**
- minimum wall time: **781 s**
- maximum wall time: **3600 s**
- sample standard deviation: **1444.8 s**

The hidden evaluator did not run after the clean deployment failures because each candidate failed before reaching a healthy evaluable application state.

## Superseded diagnostic evaluations

Before runtime contamination was discovered, B01 and B02 were evaluated while a residual candidate-created MySQL service (`mysql-record`) was listening on host port 3306 with persistent state.

Those diagnostic outputs are preserved for forensic purposes:

- B01 diagnostic: 13/16 total, 11/14 critical
- B02 diagnostic: 12/16 total, 10/14 critical

They are **not formal functional scores** and must not be combined with the clean evaluation outcome.

## Failure diversity

The three clean failures were not identical:

1. **B01**: the frozen artifact attempted database initialization against host port 3306 instead of the harness-provided 3307. Repository inspection later confirmed that `.env` was tracked.
2. **B02**: a tracked `.env` specified `DB_PORT=3306`, while `src/config/index.js` used `dotenv.config({ override: true })`, replacing the harness-provided environment.
3. **B03**: environment handling was improved; `.env` was ignored and excluded from the archive, and the candidate connected successfully to MySQL at 3307. Deployment still failed because the migration sent a multi-statement schema block through `connection.execute(schema)`.

This shows three independent artifact/deployment defects under the same benchmark configuration rather than one repeated evaluator fault.

## Inference throughput

| Run | Prompt tokens | Cached prompt tokens | Generated tokens | Prompt time (s) | Generation time (s) | Prompt tok/s | Decode tok/s | Cache ratio |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| C001-B01 | 144697 | 1277791 | 48154 | 203.802 | 1153.161 | 709.99 | 41.76 | 89.83% |
| C001-B02 | 42912 | 903511 | 21177 | 67.175 | 504.826 | 638.81 | 41.95 | 95.47% |
| C001-B03 | 92019 | 805455 | 24049 | 131.901 | 574.349 | 697.64 | 41.87 | 89.75% |

Combined counter totals:

- uncached prompt tokens: **279628**
- cached prompt tokens: **2986757**
- generated tokens: **93380**
- prompt processing time: **402.878 s**
- generation time: **2232.336 s**
- aggregate prompt throughput: **694.08 tok/s**
- aggregate decode throughput: **41.83 tok/s**
- aggregate prompt cache ratio: **91.44%**
- total measured inference time: **2635.214 s**
- inference share of total wall time: **43.76%**

The decode rate was highly stable across the three runs (41.76–41.95 tok/s). Large wall-time variation therefore arose primarily from agent behavior, token volume, self-verification/debugging and the B02 timeout rather than a major change in raw decode speed.

## Interpretation

For BENCH-CODE-001 v1.0, this exact hardware/software/model/quantization profile produced **0/3 successful clean deployments**. This is a result for the tested configuration and three-run sample, not a general reliability claim about Qwen3.6.
