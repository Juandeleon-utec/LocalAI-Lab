# BENCH-CODE-DEV-002 — Existing-code feature development

BENCH-CODE-DEV-002 evaluates autonomous coding agents on a realistic modification of an existing Node.js/Express/MySQL application. The task is to add full administrative CRUD management for vehicles associated with existing transporters while preserving current behavior.

## Benchmark objective

The benchmark measures whether a coding agent can inspect an unfamiliar repository, integrate a non-trivial feature across persistence, backend routes and frontend UI, preserve regressions, and leave the application in an executable state without corrective human prompting.

Unlike BENCH-CODE-001, this is an **existing-code development task** rather than a greenfield application build.

## Frozen protocol

- protocol: one shot per model
- human interventions during a valid run: 0
- context budget: 49,152 tokens
- output budget used in OpenCode model definitions: 8,192 tokens
- agent: OpenCode through an OpenAI-compatible `llama-server` endpoint
- benchmark freeze: v1.8
- seed commit: `d429be34cab51ae58b5237ef6e0c296e2c5b67f0`
- seed SHA-256: `df80c1d7186342dead10fba07fa25d018eea56c5e49652421928868351995d55`
- prompt SHA-256: `3c44852d92d34278171e3a04ae76b208946cb7bd15ff39b2ce3f37477a9cf18f`
- freeze timestamp: `2026-10-08T00:13:53.4014957Z`

The exact participant prompt is in `prompt.md`. The frozen harness/evaluator fingerprints are in `freeze-v1.8.json`.

## Evaluation layers

The benchmark records three independent functional layers:

1. **Main API evaluator** — 18 tests, 15 marked critical.
2. **Restart evaluator** — 2 critical persistence/restart tests.
3. **Playwright E2E** — 6 frontend contract/workflow tests.

A complementary **Semantic Audit v2** was added after the runs. It does not change or overwrite official results. It removes vacuous PASS cases where a generic `404 Ruta no encontrada` accidentally satisfied a negative test even though the vehicle route itself was never implemented.

## Scoring policy

Official evaluator output is preserved verbatim. For comparative interpretation, use the audited score alongside the official score.

Primary quality ordering:

1. audited critical functionality;
2. audited total functionality;
3. restart/persistence evidence;
4. E2E completion;
5. regressions/startup integrity.

Efficiency metrics such as wall time, prompt tokens and generation throughput are reported separately from quality.

## Run-validity rules

- Do not modify candidate code during evaluation.
- A failure before inference due to infrastructure is invalid infrastructure and does not consume the model attempt.
- A failure after inference in post-processing may be recovered without rerunning the model.
- A candidate-generated startup/migration error is a candidate failure, not infrastructure failure.
- A completed model run is not rerun merely because the candidate failed tests.
- Context-overflow retries must be documented explicitly rather than hidden.

## Current experiment set

| Run | Model | Quantization | Status |
| --- | --- | --- | --- |
| `DEV002-CODER-NEXT-Q3` | Qwen3-Coder-Next ~80B-A3B | Q3_K_M | completed |
| `DEV002-CODER30-Q3` | Qwen3-Coder-30B-A3B-Instruct | Q3_K_M | completed; post-agent evidence recovery documented |
| `DEV002-CODER30-Q4` | Qwen3-Coder-30B-A3B-Instruct | Q4_K_M | candidate startup failure |
| `DEV002-QWEN36-35B-Q4-R2` | Qwen3.6-35B-A3B | Q4_K_M | completed after one documented context-overflow attempt |

Results and interpretation are under `benchmarks/results/BENCH-CODE-DEV-002/`.
