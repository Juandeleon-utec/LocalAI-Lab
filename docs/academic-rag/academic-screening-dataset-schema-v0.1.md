# Academic Screening Dataset Schema v0.1

**Project:** LocalAI-Lab  
**Module:** Academic Reviewer / Bibliographic Screening  
**Version:** 0.1

## 1. Purpose

This document defines the minimum dataset and human ground-truth structure used by Academic Screening Benchmark v0.1.

The objective is to ensure that all model and RAG configurations are evaluated against the same frozen corpus and the same human reference labels.

---

## 2. Dataset Files

The first benchmark dataset is represented by two tabular files:

```text
papers-v0.1.csv
ground-truth-v0.1.csv
```

The first stores bibliographic and document metadata. The second stores human judgments.

Large PDFs must not be committed to the Git repository. They should be stored under the benchmark data area, for example:

```text
/srv/data/benchmarks/academic-rag/datasets/v0.1/papers/
```

---

## 3. Paper Metadata Schema

Required columns:

| Field | Type | Required | Description |
|---|---|---:|---|
| paper_id | string | yes | Stable internal identifier such as P001 |
| title | string | yes | Paper title |
| authors | string | yes | Authors as exported or normalized |
| year | integer | yes | Publication year |
| doi | string | no | DOI when available |
| scopus_id | string | no | Scopus identifier when available |
| source | string | no | Journal, conference, or source title |
| abstract | text | recommended | Abstract used by Configurations B and C |
| keywords | text | recommended | Author/index keywords used by Configuration C |
| filename | string | no | Local PDF filename |
| document_type | string | no | Article, conference paper, review, etc. |
| language | string | no | Document language |
| notes | text | no | Dataset-curation notes only |

### Stable identifier rule

`paper_id` must never depend on filename, DOI availability, or model output.

Recommended format:

```text
P001
P002
P003
...
```

Once dataset version `v0.1` is frozen, IDs must not be reassigned.

---

## 4. Human Ground-Truth Schema

Required columns:

| Field | Type | Required | Description |
|---|---|---:|---|
| paper_id | string | yes | Must match papers-v0.1.csv |
| relevance_class | integer | yes | 0–3 human relevance label |
| relevance_label | enum | yes | NOT_RELEVANT, TANGENTIAL, RELEVANT, HIGHLY_RELEVANT |
| reading_decision | enum | yes | DISCARD, REFERENCE_ONLY, READ_SECTIONS, READ_FULL |
| evaluator | string | yes | Stable evaluator identifier |
| evaluation_date | date | yes | ISO date YYYY-MM-DD |
| confidence | number | recommended | Human confidence from 0.0 to 1.0 |
| topic_match | integer | no | Optional 0–3 dimension score |
| methodology_match | integer | no | Optional 0–3 dimension score |
| hardware_or_sensor_match | integer | no | Optional 0–3 dimension score |
| dataset_match | integer | no | Optional 0–3 dimension score |
| edge_ai_relevance | integer | no | Optional 0–3 dimension score |
| machine_learning_method_match | integer | no | Optional 0–3 dimension score |
| experimental_design_value | integer | no | Optional 0–3 dimension score |
| state_of_the_art_value | integer | no | Optional 0–3 dimension score |
| rationale | text | recommended | Short reason for human classification |
| recommended_sections | text | no | Sections that appear worth reading |
| notes | text | no | Additional evaluator comments |

---

## 5. Relevance Scale

| Value | Label | Interpretation |
|---:|---|---|
| 3 | HIGHLY_RELEVANT | Directly supports the research problem, methodology, implementation, experimental design, or state of the art |
| 2 | RELEVANT | Useful related evidence, but not central |
| 1 | TANGENTIAL | Partial overlap with limited direct value |
| 0 | NOT_RELEVANT | No meaningful contribution to the defined research objective |

---

## 6. Reading Decision

| Decision | Meaning |
|---|---|
| READ_FULL | Full manual reading is justified |
| READ_SECTIONS | Selected sections should be read |
| REFERENCE_ONLY | Primarily useful as background/supporting citation |
| DISCARD | No meaningful value for the current objective |

The reading decision is related to, but not mechanically determined by, the relevance class.

---

## 7. Dataset Construction Procedure

For the initial benchmark:

1. Select approximately 30–50 Scopus-derived papers.
2. Include a realistic mixture of highly relevant, relevant, tangential, and non-relevant results.
3. Assign stable `paper_id` values.
4. Normalize metadata without changing scientific content.
5. Record available PDF filenames separately from bibliographic identifiers.
6. Create human ground truth before running comparative model experiments.
7. Freeze the corpus as `dataset_version = v0.1`.
8. Record any later additions or removals as a new dataset version.

---

## 8. Ground-Truth Procedure

The evaluator should classify papers without seeing model predictions from the benchmark configuration being evaluated.

For each paper, record:

```text
relevance_class
reading_decision
confidence
rationale
```

Optional dimension scores may be added when they provide useful diagnostic information.

If the evaluator cannot confidently classify a paper from title/abstract alone, the evaluator may inspect the full paper. That fact should be recorded in `notes` so the human-reference process remains auditable.

---

## 9. Research Objective Versioning

Relevance is conditional on a research objective.

The exact research objective used for a benchmark must be stored and versioned. A change in research objective creates a different ground-truth task even if the same papers are reused.

Recommended identifier:

```text
research_objective_version = RO-v0.1
```

The benchmark run metadata should always record this value.

---

## 10. Data Separation

During initial development, the first 30–50 papers may be used as a development corpus.

Before publication-level claims, create at least:

```text
development set
held-out validation/test set
```

Prompt tuning, chunking parameters, retrieval Top-N, reranker Top-K, and threshold selection must be performed only on the development set.

---

## 11. Data Integrity Rules

- Do not silently modify abstracts or keywords.
- Preserve original bibliographic values when possible.
- Record normalization decisions.
- Do not overwrite a frozen dataset version.
- Do not modify human labels after inspecting final test results without creating a revised ground-truth version.
- Missing data should remain missing rather than being inferred.

---

## 12. Suggested Server Layout

```text
/srv/data/benchmarks/academic-rag/
├── datasets/
│   └── v0.1/
│       ├── papers-v0.1.csv
│       ├── papers/
│       └── dataset-manifest.json
├── ground-truth/
│   └── ground-truth-v0.1.csv
├── runs/
└── reports/
```

The repository contains only schemas, prompts, documentation, and lightweight templates. The research corpus and large benchmark outputs remain in `/srv/data`.

---

## 13. Versioning Rule

A new version is required if any of the following changes materially:

- corpus membership,
- paper IDs,
- research objective,
- human labels,
- label definitions,
- required schema fields.

Examples:

```text
dataset v0.1 + ground truth v0.1

dataset v0.1 + ground truth v0.2

dataset v0.2 + ground truth v0.2
```

Every benchmark run must store both versions explicitly.
