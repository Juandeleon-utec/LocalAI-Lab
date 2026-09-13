# Publications and Research Outputs

This directory tracks publication-oriented work derived from LocalAI-Lab.

## Purpose

The goal is not to force every engineering change into a paper. Instead, technically interesting questions should be identified early enough that the required evidence can be collected correctly from the beginning.

## Suggested structure for each study

```text
study-name/
├── protocol.md
├── hypotheses.md
├── dataset.md
├── metrics.md
├── analysis-plan.md
├── figures.md
└── manuscript-notes.md
```

## Evidence locations

Use run identifiers rather than manually copying numbers between documents.

Current canonical locations:

- coding performance summaries: `benchmarks/results/`;
- formal academic-screening run evidence: `results/academic-screening/`;
- academic corpus extraction/metadata evidence: `results/academic-rag/`;
- academic screening result interpretation: `docs/academic-rag/`;
- prompts: `prompts/`;
- analysis and execution scripts: `scripts/academic-rag/`.

Formal Academic Screening A001/A003 directories preserve manifests, raw API responses, parsed predictions, ground-truth comparisons and evaluation outputs. See `docs/academic-rag/reproducibility-record-2026-09-13.md` for the current artifact audit.

Large complete experiment snapshots should remain outside normal Git when appropriate, but must be accompanied by a checksum. Small textual raw outputs and manifests should be versioned in Git whenever practical.

## Candidate studies

1. Local vs hosted coding agents on controlled software-engineering tasks.
2. Quantization, context and CPU/GPU offload trade-offs on a 16 GB consumer AMD GPU.
3. Local literature screening and the incremental value of dense retrieval, hybrid retrieval, reranking and citation-aware RAG.
4. Retrieval/reranking strategies for citation-grounded academic RAG.
5. Energy and latency trade-offs for local AI workloads.

## Current academic-screening evidence status

Academic Screening v0.1 is currently an engineering/development benchmark:

- 24 unique papers;
- ground truth distribution: class 1 = 5, class 2 = 11, class 3 = 8, class 0 = 0;
- ground truth is human-supervised / AI-assisted;
- A001 and A003 both achieved relevant-paper recall 1.000 on this corpus;
- A003 improved ordinal calibration but did not improve the binary relevant/non-relevant confusion matrix;
- A003 was designed after inspecting A001 errors and is therefore a development-set calibration experiment.

These facts must be reported if the results are used in a manuscript. The current results must not be described as independent external validation.

## Good research practice

Before collecting publication-quality results:

- freeze a protocol version;
- define hypotheses and primary metrics;
- define task/data inclusion and exclusion criteria;
- define the ground-truth annotation process and provenance;
- record environment and software versions;
- record exact model and dataset checksums;
- record the repository commit used to execute the experiment;
- decide repetition count;
- define failure handling;
- preserve raw model outputs;
- preserve exact prompts and run manifests;
- version analysis scripts;
- collect telemetry required for any hardware/energy claims;
- document deviations from the protocol.

## Reviewer-oriented retention policy

For results that may support a paper, retain at least:

1. frozen input dataset and ground truth;
2. exact prompt and research objective;
3. exact model artifact identifier and SHA-256;
4. inference/server configuration;
5. raw responses;
6. parsed predictions;
7. evaluation outputs;
8. software/environment snapshot;
9. failure records;
10. a checksummed archival copy independent of the working repository.

The purpose is to be able to answer a reviewer request for raw predictions, confusion data, prompt text, environment details or derivation of a reported metric without reconstructing evidence after the fact.
