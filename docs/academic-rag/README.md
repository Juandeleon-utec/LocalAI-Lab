# Academic RAG documentation index

This directory contains design, benchmark protocol, result interpretation and reproducibility records for the LocalAI-Lab academic workflow.

## Current status

Current snapshot:

- `current-status-2026-09-13.md`

Historical snapshot:

- `current-status-2026-09-11.md`

Dated status files are historical records. New state should be recorded in a new dated snapshot rather than rewriting old snapshots.

## Benchmark specification

- `academic-screening-benchmark-v0.1.md` — frozen benchmark design/specification;
- `academic-screening-dataset-schema-v0.1.md` — dataset and ground-truth schema;
- `a003-prompt-calibration-plan.md` — pre-run motivation and controlled intervention for A003.

## Results

- `a001-results-2026-09-12.md` — formal A001 baseline interpretation;
- `a003-results-2026-09-13.md` — formal A003 result and A001 comparison;
- `reproducibility-record-2026-09-13.md` — environment, fingerprints, evidence locations and current reproducibility gaps.

Machine-readable and raw run evidence is under:

- `results/academic-screening/A001/A001-20260912T122718Z/`
- `results/academic-screening/A003/A003-20260913T133722Z/`

Artifact semantics and run fingerprints are summarized in `results/academic-screening/README.md`.

## Prompts

- `prompts/academic-screening-v0.1.txt` — A001 prompt;
- `prompts/academic-screening-v0.2.txt` — A003 calibrated prompt, frozen as a development candidate after A003.

Do not continue tuning v0.2 on Academic Screening v0.1. Future validation should use independent/expanded hold-out material.

## Experimental sequence

```text
A001  LLM-only screening, prompt v0.1
A002  deterministic reading policy over A001 predictions
A003  LLM-only screening, calibrated prompt v0.2
B001  dense retrieval + LLM
C001  hybrid dense+sparse retrieval + LLM
D001  hybrid retrieval + reranker + LLM
E001  citation-aware full RAG
```

## Research interpretation rule

Keep these dimensions separate:

- ordinal relevance calibration;
- binary relevant/non-relevant screening;
- reading-workload reduction;
- retrieval quality;
- generation/citation quality;
- computational efficiency and energy.

Improvement in one dimension must not be reported as improvement in another without supporting measurements.
