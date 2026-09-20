# Academic Screening reproducibility record — 2026-09-13

This document records the reproducibility state of the Academic Screening A001/A003 experiments after the original result artifacts were synchronized from `ia-server` into the repository.

## Scope

Formal runs covered here:

- A001: `A001-20260912T122718Z`
- A003: `A003-20260913T133722Z`

The two runs evaluate the same 24-paper Academic Screening v0.1 corpus with the same model and research objective. A003 changes the screening prompt from v0.1 to v0.2.

## Hardware and runtime environment

Server:

- host: `ia-server`
- CPU: Intel Core i5-14600KF
- RAM: 64 GB
- GPU: AMD Radeon RX 9060 XT 16 GB
- ROCm target: `gfx1200`
- OS: Ubuntu Server 24.04.4 LTS
- kernel: `7.0.0-30-generic`
- ROCm: 10.0
- HIP: 7.15.26333

Inference stack:

- `llama.cpp` repository: `ggml-org/llama.cpp`
- commit: `b96806d96061049a5b574269b049bf6241d63d46`
- tag/build: `b10752`
- llama.cpp version: `0.3.0-dev`
- backend: ROCm/HIP
- server: OpenAI-compatible `llama-server`
- model alias: `qwen3-academic`
- context: 8192 tokens

Academic model:

- family: Qwen3-30B-A3B-Instruct-2507
- quantization: Q3_K_M
- GGUF filename: `Qwen_Qwen3-30B-A3B-Instruct-2507-Q3_K_M.gguf`
- server path: `/srv/models/academic/qwen3-30b-a3b-instruct-2507/Qwen_Qwen3-30B-A3B-Instruct-2507-Q3_K_M.gguf`
- recorded size: 14,070,833,152 bytes

The exact GGUF SHA-256 was not captured inside the original A001/A003 manifests. The preserved model artifact was hashed post hoc on 2026-09-20:

```text
327c6e0826bee8f19172e96c94bb7bba385f7a39d08314803652df9942401c4f
```

This closes model-artifact identification for the preserved file, but the documentation must continue to state that the hash was captured after the formal runs rather than recorded contemporaneously in their manifests.

## Server launch profile

The academic model was served manually. The validated profile is:

```bash
cd ~/llama.cpp
source ~/rocm10-devel/bin/activate
export ROCM_ROOT="$(rocm-sdk path --root)"
export ROCM_BIN="$(rocm-sdk path --bin)"
export HIP_PATH="$ROCM_ROOT"
export HIP_PLATFORM=amd
export PATH="$ROCM_BIN:$PATH"
SP="$HOME/rocm10-devel/lib/python3.12/site-packages"
export LD_LIBRARY_PATH="$SP/_rocm_sdk_core/lib:$SP/_rocm_sdk_libraries/lib:${LD_LIBRARY_PATH:-}"

./build-rocm/bin/llama-server \
  -m /srv/models/academic/qwen3-30b-a3b-instruct-2507/Qwen_Qwen3-30B-A3B-Instruct-2507-Q3_K_M.gguf \
  --host 0.0.0.0 \
  --port 8080 \
  --alias qwen3-academic \
  --fit on \
  --fit-target 1024 \
  -c 8192 \
  --jinja \
  --api-key localai-dev-key
```

The development API key shown above is part of the historical experiment configuration and should not be reused as a production secret.

## Frozen research objective

Both formal runs used exactly:

> Evaluate scientific literature relevant to predictive maintenance and fault diagnosis of rotating machinery and induction motors, with emphasis on vibration-based condition monitoring, machine learning or deep learning, edge AI deployment, embedded sensing, low-cost hardware, and experimentally validated methods applicable to resource-constrained systems.

## Dataset fingerprint

Both A001 and A003 manifests record the same dataset:

```text
/srv/data/benchmarks/academic-rag/datasets/academic-screening-v0.1/papers-v0.1.csv
```

SHA-256:

```text
f0f43a52042a791b9a341011b7bf831a9d82f754f02f0d66f16e5172301bccb2
```

The preserved repository copy at `results/academic-screening/inputs/v0.1/dataset/papers-v0.1.csv` was independently verified on Windows and matches this hash exactly.

Additional frozen-input fingerprints:

```text
manifest-v0.1.json
495aff80d68e05583bed8495f32b67b50d5fcc1725c6a4191752920fc0580747

ground-truth-v0.1.csv
63b9d499c52884f343ac69d66cde16627c785fc1b53735b6c805b900c62cf56d
```

These files are versioned under `results/academic-screening/inputs/v0.1/`.

Corpus state used to build the dataset:

- source PDFs: 25
- successfully extracted PDFs: 25
- pages: 274
- extracted characters: 1,158,398
- READY unique papers: 24
- excluded duplicate: P024, duplicate of P023
- unresolved duplicates: 0

Ground-truth distribution:

- class 0: 0
- class 1: 5
- class 2: 11
- class 3: 8

Ground truth is human-supervised / AI-assisted and must not be described as an independent human-only annotation set.

## Prompt fingerprints

### A001

Repository prompt:

`prompts/academic-screening-v0.1.txt`

Run-manifest SHA-256:

```text
2d63833dcf5e3a2cbbea8ddc6296dd040ed73b63f261fd10e7b4d3b8537e670d
```

### A003

Repository prompt:

`prompts/academic-screening-v0.2.txt`

Run-manifest SHA-256:

```text
04dbcc97f7b1d604746a47ff295181eaa61c678b3673190fedbfa12bfb943539
```

Future reruns should verify these hashes before inference rather than relying only on filenames.

## Common inference parameters

Both formal runs used:

- model alias: `qwen3-academic`
- endpoint: `http://127.0.0.1:8080/v1`
- temperature: 0.0
- maximum completion tokens: 1200
- seed: 42
- one paper per request
- no RAG
- no embeddings
- no reranker
- no OCR during screening
- no external model API

Runner:

`scripts/academic-rag/run_screening_baseline.py`

Evaluator:

`scripts/academic-rag/evaluate_screening_run.py`

Deterministic reading-policy evaluator:

`scripts/academic-rag/evaluate_reading_policy_a002.py`

## Formal A001

Repository artifacts:

`results/academic-screening/A001/A001-20260912T122718Z/`

Execution:

- papers: 24
- successful: 24
- invalid: 0
- errors: 0
- wall time: 136.522189 s
- throughput: 632.864 papers/hour
- prompt tokens: 32,808
- completion tokens: 8,680
- total tokens: 41,488

Primary results:

- exact four-class accuracy: 0.416667
- macro F1: 0.276191
- relevant-paper precision: 0.863636
- relevant-paper recall: 1.000000
- false-negative rate: 0.000000
- class-3 recall: 1.000000
- MAE: 0.708333
- quadratic weighted kappa: 0.281250
- model-generated active-reading reduction: 0.000000

Binary confusion at threshold `class >= 2`:

- TP: 19
- FP: 3
- FN: 0
- TN: 2

## Formal A003

Repository artifacts:

`results/academic-screening/A003/A003-20260913T133722Z/`

Execution:

- papers: 24
- successful: 24
- invalid: 0
- errors: 0
- wall time: 150.521573 s
- throughput: 574.004 papers/hour
- prompt tokens: 50,088
- completion tokens: 8,824
- total tokens: 58,912

Primary results:

- exact four-class accuracy: 0.541667
- macro F1: 0.407857
- relevant-paper precision: 0.863636
- relevant-paper recall: 1.000000
- false-negative rate: 0.000000
- class-3 recall: 0.500000
- MAE: 0.458333
- quadratic weighted kappa: 0.488372
- active-reading reduction: 0.083333

Binary confusion at threshold `class >= 2`:

- TP: 19
- FP: 3
- FN: 0
- TN: 2

A003 therefore improved ordinal calibration but did not improve binary screening precision/recall or the number of papers selected for active reading beyond the deterministic A002 policy applied to A001.

## Failed and smoke runs

A previous A003 execution `A003-20260913T131407Z` failed before inference because the model server was unavailable. It produced 0 successful papers, 24 errors, and 0 tokens. It is infrastructure evidence only and must not be included in scientific comparisons.

One-paper smoke tests were also used to validate the runner and academic endpoint. Smoke runs are validation artifacts, not formal benchmark results.

## Repository evidence now present

The repository contains:

- versioned prompts v0.1 and v0.2;
- extraction, normalization, dataset-builder, runner, policy, and evaluator scripts;
- extracted paper text and initial corpus metadata under `results/academic-rag/`;
- the exact frozen `papers-v0.1.csv` used by A001/A003 and its dataset manifest;
- the exact frozen `ground-truth-v0.1.csv` used by the evaluator;
- `manual-overrides-v0.1.csv`, normalized metadata, duplicate-candidate output, and corpus-validation output used to build v0.1;
- formal A001 raw responses, predictions, manifest, comparison, and evaluation artifacts;
- formal A003 raw responses, predictions, manifest, comparison, and evaluation artifacts;
- a post-run Python dependency snapshot captured on 2026-09-20;
- the SHA-256 of the preserved academic GGUF artifact;
- methodological interpretation documents.

The frozen-input/evidence bundle was committed directly to `main` as commit `bf4ce062d403605bef04f96d519bf45f34ff1a74` with message `Preserve Academic Screening v0.1 frozen inputs`.

## Current reproducibility status

A001/A003 now have a substantially complete provenance chain from the frozen screening dataset onward:

```text
frozen papers-v0.1.csv
  -> frozen ground-truth-v0.1.csv
  -> versioned prompt
  -> preserved GGUF artifact
  -> fixed llama.cpp build
  -> raw responses
  -> parsed predictions
  -> evaluation outputs
```

The dataset CSV is cryptographically linked to the original A001/A003 manifests through the same SHA-256. The manifest and ground-truth files now also have recorded SHA-256 fingerprints.

Remaining limitations should still be stated explicitly:

1. the academic GGUF hash was captured post hoc on 2026-09-20 rather than inside the original A001/A003 manifests;
2. the preserved dependency snapshot was captured on 2026-09-20 and confirms Python 3.12.3 and PyMuPDF 1.28.2 at that date, but does not independently prove that every installed package version was identical during A001/A003;
3. the current kernel snapshot on 2026-09-20 is `7.0.0-31-generic`, whereas the formal A001/A003 environment was documented as `7.0.0-30-generic`;
4. automatic per-run VRAM/RAM/CPU/GPU telemetry and integrated-energy logs were not captured for A001/A003;
5. the LocalAI-Lab repository commit was not embedded directly in the original run manifests.

The separate checksummed evidence archive created after the experiments should continue to be retained independently from Git for audit/reviewer use.

## Post-run environment snapshot

A dependency snapshot was preserved as `results/academic-screening/environment/academic-environment-20260920.txt`.

Observed on 2026-09-20:

- Python: 3.12.3
- PyMuPDF: 1.28.2
- OS: Ubuntu 24.04.4 LTS
- kernel: `7.0.0-31-generic`
- GPU: AMD Radeon RX 9060 XT
- ROCm target: `gfx1200`

This snapshot is intentionally described as post-run evidence and must not be substituted for the contemporaneous A001/A003 environment record.

## Known code cleanup items

The repository extractor already contains the spaced-`A B S T R A C T` recovery required for P011, P012, P015, and P021. Two cleanup items remain:

- migrate deprecated `import fitz` usage to `import pymupdf`;
- remove the unnecessary escaped bracket in the extractor DOI `rstrip` string to avoid the historical invalid-escape warning.

These cleanup changes should be versioned separately because changing parser code after a frozen dataset exists must not silently redefine the inputs used by A001/A003.

## Reproduction policy going forward

Every new formal experiment should preserve, before analysis:

1. exact dataset and ground-truth artifacts;
2. prompt and dataset SHA-256;
3. exact model file SHA-256;
4. server launch arguments;
5. inference engine commit/build;
6. OS/kernel/ROCm/HIP versions;
7. Python environment snapshot;
8. raw responses;
9. parsed predictions;
10. evaluation outputs;
11. telemetry logs where applicable;
12. repository commit used for the run.

A formal result is not considered fully reproducible merely because its final metrics are documented; the complete provenance chain must be preserved.
