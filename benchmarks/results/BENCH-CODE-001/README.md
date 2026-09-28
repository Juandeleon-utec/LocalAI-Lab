# BENCH-CODE-001 Results

Formal and engineering run artifacts for BENCH-CODE-001 are stored here after protocol inputs are frozen.

## Completed series

- `C001-A-SUMMARY.md` — OpenCode + Qwen3-Coder-30B-A3B-Instruct Q3_K_M, 32K, three runs.
- `C001-B-SUMMARY.md` — OpenCode + Qwen3.6-35B-A3B Q4_K_M, 32K, three runs.
- `C001-A-vs-B.md` — benchmark-scoped comparison of the completed A and B series.

Run-level records are stored under `C001-A01` … `C001-A03` and `C001-B01` … `C001-B03`.

## Evaluation hygiene

Large candidate repositories, raw high-frequency telemetry and hidden evaluator archives may be stored outside normal Git when necessary. They must be checksummed and referenced from each run manifest when hashes are available.

The executable hidden evaluator must never be placed in a participant-visible workspace.

For B01 and B02, initial diagnostic evaluations were later found to have occurred while a residual candidate-created MySQL service was present on host port 3306. Those diagnostic scores are preserved for forensic traceability but are explicitly superseded by clean redeployment results and are excluded from A/B functional comparison.
