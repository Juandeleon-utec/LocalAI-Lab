# Academic Corpus Extraction Evidence

This directory contains text extraction and initial metadata artifacts synchronized from the Academic Screening v0.1 corpus-processing stage.

## Contents

- `P001.txt` ... `P025.txt`: page-aware text extracted from the 25 source PDFs;
- `pdf-inventory-v0.1.csv`: source-file inventory used by the extraction pipeline;
- `papers-metadata-v0.1.csv`: initial extraction metadata and measurements.

These files are evidence from the preprocessing stage, not the final 24-paper screening dataset.

## Duplicate handling

P023 and P024 have identical normalized extracted text. P024 was excluded by manual override and P023 was retained as the canonical paper. Therefore both extracted text files may be present here even though only 24 papers entered the frozen Academic Screening v0.1 dataset.

## Important distinction

The formal A001/A003 screening runs used a derived frozen dataset:

```text
/srv/data/benchmarks/academic-rag/datasets/academic-screening-v0.1/papers-v0.1.csv
```

with SHA-256:

```text
f0f43a52042a791b9a341011b7bf831a9d82f754f02f0d66f16e5172301bccb2
```

The exact frozen dataset CSV, its manifest, full ground-truth CSV, manual overrides and normalized validation artifacts are not currently all present in this Git tree. They remain required for complete repository-only end-to-end reproduction and are tracked in `docs/academic-rag/reproducibility-record-2026-09-13.md`.

## Extraction implementation

The extraction and normalization code is under `scripts/academic-rag/`.

The extractor version currently in the repository includes support for spaced abstract headings such as `A B S T R A C T`, which was necessary to recover abstracts for P011, P012, P015 and P021.

Historical extraction summary:

- source documents: 25
- successful extraction: 25
- empty/error: 0
- total pages: 274
- extracted characters: 1,158,398
- READY after normalization and duplicate review: 24
- excluded: 1

Do not treat this directory as a substitute for the frozen dataset manifest or ground truth.
