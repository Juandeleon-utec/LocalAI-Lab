# Academic RAG current status — 2026-09-13

This document supersedes `current-status-2026-09-11.md` as the current academic-screening/RAG status snapshot. Older dated status files remain historical records and should not be rewritten to match later results.

## Platform

- host: `ia-server`
- CPU: Intel Core i5-14600KF
- RAM: 64 GB
- GPU: AMD Radeon RX 9060 XT 16 GB (`gfx1200`)
- OS: Ubuntu Server 24.04.4 LTS
- kernel: `7.0.0-30-generic`
- ROCm: 10.0
- HIP: 7.15.26333
- `llama.cpp`: tag/build `b10752`
- `llama.cpp` commit: `b96806d96061049a5b574269b049bf6241d63d46`
- serving: manual `llama-server`, OpenAI-compatible API
- operating rule: one large GPU model at a time

Persistent storage:

```text
/srv/models  -> model artifacts
/srv/data    -> datasets, papers, Qdrant, benchmarks, backups
```

## Academic model

Formal screening model:

- Qwen3-30B-A3B-Instruct-2507
- quantization: Q3_K_M
- GGUF: `Qwen_Qwen3-30B-A3B-Instruct-2507-Q3_K_M.gguf`
- model path: `/srv/models/academic/qwen3-30b-a3b-instruct-2507/Qwen_Qwen3-30B-A3B-Instruct-2507-Q3_K_M.gguf`
- recorded size: 14,070,833,152 bytes
- alias: `qwen3-academic`
- context: 8192

The exact GGUF SHA-256 was not captured in A001/A003 manifests and is now a tracked reproducibility requirement for future formal runs.

## Corpus and preprocessing

Pipeline:

```text
PDF corpus
  -> inventory + SHA-256
  -> page-aware extraction
  -> metadata normalization
  -> duplicate detection + manual overrides
  -> frozen screening dataset
  -> ground truth
  -> LLM-only baseline / calibration
  -> future retrieval / reranking / RAG
```

Validated v0.1 corpus state:

- 25 PDFs extracted successfully
- 0 extraction errors
- 274 pages
- 1,158,398 extracted characters
- 24 unique READY papers
- 1 excluded duplicate: P024 duplicates P023
- 0 unresolved duplicate documents

The extractor recognizes spaced headings such as `A B S T R A C T`, which recovered abstracts for P011, P012, P015 and P021.

## Ground truth

Academic Screening v0.1 contains 24 evaluated papers:

- class 0 / NOT_RELEVANT: 0
- class 1 / TANGENTIAL: 5
- class 2 / RELEVANT: 11
- class 3 / HIGHLY_RELEVANT: 8

There are 19 papers with ground-truth relevance `>= 2`.

Ground truth is human-supervised / AI-assisted. This provenance must be reported in research outputs.

The lack of class-0 papers is an important limitation. v0.2/hold-out should add clearly irrelevant and borderline papers.

## Formal A001

Run:

`A001-20260912T122718Z`

Prompt:

`prompts/academic-screening-v0.1.txt`

Fingerprints:

- dataset SHA-256: `f0f43a52042a791b9a341011b7bf831a9d82f754f02f0d66f16e5172301bccb2`
- prompt SHA-256: `2d63833dcf5e3a2cbbea8ddc6296dd040ed73b63f261fd10e7b4d3b8537e670d`

Execution:

- 24/24 successful
- 0 invalid
- 0 errors
- wall time: 136.522189 s
- throughput: 632.864 papers/hour
- total tokens: 41,488

Quality:

- exact 4-class accuracy: 0.417
- macro F1: 0.276
- relevant recall: 1.000
- relevant precision: 0.864
- FNR: 0.000
- class-3 recall: 1.000
- MAE: 0.708
- quadratic weighted kappa: 0.281
- model-generated reading reduction: 0.000

Binary confusion at `class >= 2`:

- TP 19
- FP 3
- FN 0
- TN 2

A001 is a high-recall but strongly upward-biased ordinal classifier.

## A002 deterministic policy

A002 reused frozen A001 relevance predictions and mapped relevance deterministically:

```text
3 -> READ_FULL
2 -> READ_SECTIONS
1 -> REFERENCE_ONLY
0 -> DISCARD
```

Result:

- active-reading papers: 22/24
- potential active-reading reduction: 0.083
- relevant retention: 1.000

A002 demonstrated that unconstrained model-generated reading decisions were not necessary, but the three binary false positives still limited reading reduction.

## Formal A003

Run:

`A003-20260913T133722Z`

Prompt:

`prompts/academic-screening-v0.2.txt`

Fingerprints:

- dataset SHA-256: `f0f43a52042a791b9a341011b7bf831a9d82f754f02f0d66f16e5172301bccb2`
- prompt SHA-256: `04dbcc97f7b1d604746a47ff295181eaa61c678b3673190fedbfa12bfb943539`

Execution:

- 24/24 successful
- 0 invalid
- 0 errors
- wall time: 150.521573 s
- throughput: 574.004 papers/hour
- prompt tokens: 50,088
- completion tokens: 8,824
- total tokens: 58,912

Quality:

- exact 4-class accuracy: 0.542
- macro F1: 0.408
- relevant recall: 1.000
- relevant precision: 0.864
- FNR: 0.000
- class-3 recall: 0.500
- MAE: 0.458
- quadratic weighted kappa: 0.488
- active-reading reduction: 0.083
- relevant retention: 1.000

Binary confusion remains identical to A001:

- TP 19
- FP 3
- FN 0
- TN 2

Conclusion: A003 improves ordinal calibration but does not improve binary screening efficiency.

## Development-set decision

A003 was designed after inspecting A001 errors on the same 24-paper corpus. Prompt v0.2 is now frozen as a development candidate.

Do not continue iterative prompt tuning on v0.1. The next prompt evaluation must use an independent or expanded hold-out corpus.

## Formal result evidence in Git

A001:

`results/academic-screening/A001/A001-20260912T122718Z/`

A003:

`results/academic-screening/A003/A003-20260913T133722Z/`

Each contains:

```text
manifest.json
responses.jsonl
predictions.csv
comparison.csv
evaluation.json
evaluation.md
```

The repository also contains both versioned prompts and the scripts used for runner/evaluation.

A separately checksummed full evidence archive is retained outside Git.

## Reproducibility status

The project now has strong run-output traceability but not yet complete repository-only end-to-end reproduction.

Still to preserve/version or immutably reference:

- exact frozen `papers-v0.1.csv`;
- exact `manifest-v0.1.json`;
- full frozen `ground-truth-v0.1.csv`;
- `manual-overrides-v0.1.csv`;
- normalized clean metadata and corpus validation outputs;
- exact academic-model SHA-256;
- Python/dependency environment snapshot;
- automatic run telemetry;
- repository commit field in future run manifests.

Full audit: `docs/academic-rag/reproducibility-record-2026-09-13.md`.

## Known parser cleanup

The parser logic used to create the frozen dataset is preserved. Two non-dataset-changing cleanup items remain for a separate change:

- replace deprecated `import fitz` with `import pymupdf`;
- remove the unnecessary escaped bracket in the extractor DOI `rstrip` string.

Parser changes must not silently redefine the already frozen A001/A003 inputs.

## Retrieval direction

Planned controlled progression:

```text
A001  LLM-only prompt v0.1
A002  deterministic reading policy
A003  calibrated prompt v0.2
B001  dense retrieval + LLM
C001  hybrid dense+sparse + LLM
D001  hybrid + reranker + LLM
E001  citation-aware full RAG
```

Retrieval quality will be evaluated independently with Hit Rate@K, Precision@K, Recall@K, MRR and nDCG before interpreting end-to-end RAG performance.

## Immediate next steps

1. Close the exact-input reproducibility gaps for v0.1.
2. Capture exact model SHA-256 and Python environment.
3. Add hardware/resource telemetry and integrated-energy logging.
4. Build v0.2/hold-out with class-0 and borderline papers.
5. Define structure-aware chunking and citation metadata.
6. Benchmark embedding candidates.
7. Run B001 dense retrieval.
8. Only after retrieval quality is characterized, proceed to hybrid retrieval/reranking/full RAG.
