# Academic Screening Result Artifacts

This directory contains versioned evidence from formal LocalAI-Lab academic-screening runs. These files are intentionally kept in Git because they are small, human-inspectable, and directly support reproducibility and auditability.

## Formal runs currently preserved

| Run | Prompt | Papers | Status | Repository path |
| --- | --- | ---: | --- | --- |
| A001 | `prompts/academic-screening-v0.1.txt` | 24 | formal baseline | `A001/A001-20260912T122718Z/` |
| A003 | `prompts/academic-screening-v0.2.txt` | 24 | formal prompt-calibration run | `A003/A003-20260913T133722Z/` |

Both runs used the same frozen Academic Screening v0.1 dataset and the same research objective. The model alias was `qwen3-academic`, serving Qwen3-30B-A3B-Instruct-2507 Q3_K_M through `llama-server`.

## Artifact contract

Each formal run directory contains:

- `manifest.json` — immutable run metadata, dataset/prompt SHA-256 fingerprints, generation parameters, wall time, throughput, and token totals;
- `responses.jsonl` — raw OpenAI-compatible API responses for every paper;
- `predictions.csv` — parsed structured model predictions;
- `comparison.csv` — prediction/ground-truth joins used by the evaluator;
- `evaluation.json` — machine-readable metrics and confusion matrix;
- `evaluation.md` — concise evaluator report.

The raw response file is the closest record to the original model output and should be preserved unchanged. Derived metrics can be regenerated from `predictions.csv`, the frozen ground truth, and `scripts/academic-rag/evaluate_screening_run.py`.

## Run fingerprints

### A001

- run: `A001-20260912T122718Z`
- dataset SHA-256: `f0f43a52042a791b9a341011b7bf831a9d82f754f02f0d66f16e5172301bccb2`
- prompt SHA-256: `2d63833dcf5e3a2cbbea8ddc6296dd040ed73b63f261fd10e7b4d3b8537e670d`
- temperature: `0.0`
- max completion tokens: `1200`
- seed: `42`
- wall time: `136.522189 s`
- throughput: `632.864 papers/hour`
- prompt tokens: `32,808`
- completion tokens: `8,680`
- total tokens: `41,488`

### A003

- run: `A003-20260913T133722Z`
- dataset SHA-256: `f0f43a52042a791b9a341011b7bf831a9d82f754f02f0d66f16e5172301bccb2`
- prompt SHA-256: `04dbcc97f7b1d604746a47ff295181eaa61c678b3673190fedbfa12bfb943539`
- temperature: `0.0`
- max completion tokens: `1200`
- seed: `42`
- wall time: `150.521573 s`
- throughput: `574.004 papers/hour`
- prompt tokens: `50,088`
- completion tokens: `8,824`
- total tokens: `58,912`

## A001 vs A003

| Metric | A001 | A003 |
| --- | ---: | ---: |
| Exact 4-class accuracy | 0.417 | 0.542 |
| Macro F1 | 0.276 | 0.408 |
| Relevant-paper recall (`GT >= 2`) | 1.000 | 1.000 |
| Relevant-paper precision | 0.864 | 0.864 |
| False-negative rate | 0.000 | 0.000 |
| Class-3 recall | 1.000 | 0.500 |
| Relevance-class MAE | 0.708 | 0.458 |
| Quadratic weighted kappa | 0.281 | 0.488 |
| Model-policy reading reduction | 0.000 | 0.083 |
| Relevant retention | 1.000 | 1.000 |

A003 improves ordinal calibration but does not improve the binary relevant/non-relevant confusion matrix: both runs have 19 TP, 3 FP, 0 FN, and 2 TN at the `class >= 2` threshold.

## Reproducibility boundary

The repository now preserves the formal run outputs and prompts. The original PDFs are not duplicated into the Git repository. The user also maintains a separately checksummed evidence archive containing the full experiment snapshot.

For exact end-to-end reproduction, the frozen dataset CSV, dataset manifest, frozen ground-truth CSV, manual metadata overrides, normalized metadata, exact model artifact checksum, and Python dependency versions should also be retained or referenced. See `docs/academic-rag/reproducibility-record-2026-09-13.md` for the current reproducibility audit and remaining gaps.
