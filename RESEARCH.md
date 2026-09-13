# Research Program

LocalAI-Lab is both an engineering project and a potential experimental platform for technical publications. This document tracks research questions, hypotheses and publication-oriented work packages.

## Research themes

### RQ1 — Can a consumer AMD GPU host a practically useful local coding agent?

Evaluate whether a 16 GB consumer GPU, assisted by 64 GB system RAM and quantized models, can provide useful coding-agent performance for real software-development tasks.

Potential variables:

- model family and size;
- quantization;
- GPU offload;
- context length;
- prompt-processing speed;
- generation speed;
- task completion rate;
- iteration count;
- energy per successful task.

### RQ2 — How do local coding agents compare with hosted coding agents?

Possible systems:

- Claude Code;
- OpenCode + local model;
- Qwen Code + local model;
- Aider + local model.

The comparison should evaluate complete agent systems rather than isolated model responses.

### RQ3 — What is the quality/cost/privacy trade-off of local inference?

Possible dimensions:

- task success;
- latency;
- energy;
- monetary cost;
- data exposure/privacy;
- reproducibility;
- dependence on external services.

### RQ4 — How reliable can a local academic RAG system be for scientific literature?

Evaluate:

- retrieval precision/recall;
- reranking effectiveness;
- citation correctness;
- evidence traceability;
- hallucination frequency;
- multi-document comparison;
- scientific-writing quality.

### RQ5 — Can a local LLM reduce manual literature-screening effort without losing relevant papers?

Academic Screening A001 establishes the LLM-only baseline before retrieval. A002 separates reading-policy design from relevance prediction, and A003 tests prompt calibration without changing the model, dataset or research objective.

Primary outcomes:

- recall for relevant papers (`class >= 2`);
- recall for highly relevant papers (class 3);
- false-negative rate;
- macro F1 and per-class precision/recall;
- confusion matrix;
- potential reduction in human reading workload;
- latency, token use, VRAM, power and energy.

For this use case, recall of relevant literature is a more important operational criterion than raw accuracy. The current design target is recall >= 0.95 on an appropriate evaluation corpus.

### Current result for RQ5 on v0.1

A001 and A003 both retained all 19 ground-truth relevant papers:

- relevant-paper recall: 1.000;
- false-negative rate: 0.000;
- relevant-paper precision: 0.864;
- binary confusion: 19 TP, 3 FP, 0 FN, 2 TN.

A003 improves ordinal calibration relative to A001:

- exact 4-class accuracy: 0.417 -> 0.542;
- macro F1: 0.276 -> 0.408;
- MAE: 0.708 -> 0.458;
- quadratic weighted kappa: 0.281 -> 0.488.

However, class-3 recall falls from 1.000 to 0.500, and binary screening precision/recall are unchanged. This shows that ordinal calibration and screening efficiency must be treated as separate research outcomes.

The deterministic A002 reading policy applied to A001 reduces active reading by 8.3% while retaining all 19 relevant papers. A003 also produces 8.3% reduction. Therefore, the current bottleneck is not merely reading-decision generation: the model still promotes three ground-truth class-1 papers into the active-reading set.

### RQ6 — What incremental value does retrieval add beyond title/abstract screening?

Planned controlled progression:

1. title + abstract + keywords -> LLM;
2. dense retrieval -> LLM;
3. hybrid dense+sparse retrieval -> LLM;
4. hybrid retrieval -> reranker -> LLM;
5. citation-aware full RAG.

This design permits measurement of the incremental benefit and cost of each component rather than assuming that more complex RAG is always better.

## Current Academic Screening v0.1 dataset

- 25 valid source PDFs;
- 24 unique READY papers after duplicate review;
- 1 duplicate excluded;
- 274 pages;
- 1,158,398 extracted characters;
- complete title and abstract coverage for the 24 READY papers.

Ground-truth distribution:

- class 0: 0;
- class 1: 5;
- class 2: 11;
- class 3: 8.

The current corpus is strongly enriched for relevant papers: 19/24 are class >= 2. A future benchmark version must deliberately include clearly irrelevant documents and borderline studies to improve false-positive, specificity, discard-precision and calibration analysis.

The current ground truth is human-supervised and AI-assisted. This provenance must be reported. A later independent human-only annotation pass is recommended for stronger publication claims.

## Initial academic model baseline

Selected formal model:

- Qwen3-30B-A3B-Instruct-2507;
- Q3_K_M;
- AMD Radeon RX 9060 XT 16 GB;
- `llama.cpp` / ROCm;
- context: 8192 tokens;
- alias: `qwen3-academic`.

Qwen3-Coder is not used as the formal academic model. A previous one-paper run with the coder model is retained only as a pipeline smoke test.

## Formal run record

### A001

- run: `A001-20260912T122718Z`;
- prompt: `prompts/academic-screening-v0.1.txt`;
- prompt SHA-256: `2d63833dcf5e3a2cbbea8ddc6296dd040ed73b63f261fd10e7b4d3b8537e670d`;
- dataset SHA-256: `f0f43a52042a791b9a341011b7bf831a9d82f754f02f0d66f16e5172301bccb2`;
- wall time: 136.522 s;
- total tokens: 41,488.

### A003

- run: `A003-20260913T133722Z`;
- prompt: `prompts/academic-screening-v0.2.txt`;
- prompt SHA-256: `04dbcc97f7b1d604746a47ff295181eaa61c678b3673190fedbfa12bfb943539`;
- dataset SHA-256: `f0f43a52042a791b9a341011b7bf831a9d82f754f02f0d66f16e5172301bccb2`;
- wall time: 150.522 s;
- total tokens: 58,912.

Raw and derived artifacts are versioned under `results/academic-screening/`.

## Publication-oriented experiment design

Experiments should, whenever possible, preserve:

1. immutable task definitions;
2. repository commit or document-set version;
3. exact model identifier and model SHA-256;
4. quantization;
5. full inference configuration and server launch arguments;
6. hardware/software environment;
7. exact dataset and ground-truth artifacts;
8. raw model responses;
9. processed results and analysis scripts;
10. inclusion/exclusion criteria;
11. known limitations and failures;
12. prompt and dataset SHA-256 fingerprints;
13. ground-truth provenance;
14. Python/dependency environment;
15. telemetry when hardware/energy claims are made.

Retrieval quality should be evaluated separately from generation quality. Planned retrieval metrics include Hit Rate@K, Precision@K, Recall@K, MRR and nDCG.

Energy analysis should prefer integrated energy over peak power whenever telemetry permits.

## Development-set policy

A003 was designed after inspecting A001 disagreements on the same 24-paper ground truth. A003 is therefore a development-set calibration result, not independent validation.

Prompt v0.2 is frozen as a candidate. Further tuning against Academic Screening v0.1 should stop until an independent or expanded hold-out set exists. The hold-out set should include class-0 and borderline papers and should not be used to iteratively tune the same prompt after each result.

## Candidate publication lines

### Study A — Local vs hosted coding agents

Working concept: **Performance and Resource Trade-Offs of Local Coding Agents on Consumer Hardware**.

### Study B — Quantization and memory trade-offs

Study how quantization, context length and CPU/GPU offload affect code-task quality, latency and energy on a 16 GB GPU.

### Study C — Local academic screening and RAG

Evaluate whether a local instruction model can reduce literature-screening effort at high recall, then quantify the incremental effect of dense retrieval, hybrid retrieval, reranking and citation-aware RAG.

Potential endpoints include quality, reading reduction, latency, energy, retrieval effectiveness and evidence traceability.

The A001/A003 results are engineering/development evidence. Publication-level claims require hold-out validation and stronger artifact completeness as documented in `docs/academic-rag/reproducibility-record-2026-09-13.md`.

## Publication policy

Do not select primary metrics after inspecting formal results. Before publication-oriented experiments, create a versioned benchmark protocol defining primary metrics, task selection, repetitions, ground-truth provenance and statistical analysis.

When an intervention is designed after inspecting prior errors, label the resulting experiment as development/calibration and validate it independently before presenting it as generalizable evidence.
