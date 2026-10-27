# BENCH-GEMMA4-CODE-002 — coding output evaluation

**Documented:** 2026-10-27. **Evidence status:** partial reconstructed transcript, not a frozen complete experiment.

## Model and task

- Reported model file: `gemma-4-26B-A4B-it-UD-IQ4_XS.gguf` (26B MoE, IQ4_XS).
- Engineering task: JavaScript function to compute worked time per employee from IN/OUT logs, including ordering events, unmatched events and no input-array mutation.
- Local run directory: `/srv/data/benchmarks/BENCH-GEMMA4-CODE-002/`.
- Response artifact observed: `response.txt`. The submitted excerpt begins with `calculateWorkedHours(records)` and uses Node.js `assert`; the complete output has **not** been imported to Git.
- Prompt SHA256 reported in the test discussion: `432cf924ee62ea5d7bb3243851154d3f4b0ee96a5644ed5e887b0f486c766e69`.

## Available measurements (reported, not independently re-run)

| Metric | Recorded value |
|---|---:|
| Elapsed time | 83.61 s |
| Tokens reported | 3,995 |
| Generation rate | 48.62 tok/s |
| Finish reason | stop |
| Reported model identifier | gemma4 |
| Reasoning text length | 6,326 characters |
| Final answer length | 6,177 characters |

**Measurement caveat:** token counts and throughput are transcribed from previous terminal analysis and not independently reconstructed from a versioned raw API response. The token counter definition and sampling/ROCm/server build used for this specific run have not been preserved here. Do not derive a new throughput from elapsed time and token count, or compare this directly to BENCH-CODE-001 formal decode metrics.

## Verification gaps

1. Copy prompt, response, request JSON, timing/usage JSON, llama-server metrics and `/props` snapshot from the server.
2. Hash all uploaded artifacts (SHA256), confirm effective GGUF path, active context and reasoning mode for this run.
3. Execute deterministic Node.js tests for multiple employees, out-of-order logs, unmatched events, ties and cross-midnight intervals; record pass/fail. **No test PASS is asserted here.**
4. Capture a reproducible model-independent scoring rubric before comparing with other candidate outputs.
5. Keep the earlier BENCH-CODE-001 results intact; these tasks and throughput definitions differ.

## Reproduction / safe capture (run on `ia-server`)

```bash
cd /srv/data/benchmarks/BENCH-GEMMA4-CODE-002
pwd
find . -maxdepth 2 -type f -printf '%p\n' | sort
sha256sum response.txt
```

No model weights, credentials or hidden evaluator should be committed.
