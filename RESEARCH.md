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

Academic Screening A001 establishes an LLM-only baseline before retrieval is introduced.

Primary outcomes:

- recall for relevant papers (`class >= 2`);
- recall for highly relevant papers (class 3);
- false-negative rate;
- macro F1 and per-class precision/recall;
- confusion matrix;
- potential reduction in human reading workload;
- latency, token use, VRAM, power and energy.

For this use case, recall of relevant literature is a more important operational criterion than raw accuracy. A design target such as recall >= 0.95 should be treated as a hypothesis/goal until experimentally demonstrated.

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

Current ground-truth distribution:

- class 0: 0;
- class 1: 5;
- class 2: 11;
- class 3: 8.

The current corpus is strongly enriched for relevant papers (19/24 are class >= 2). A future benchmark version should deliberately include clearly irrelevant documents to improve false-positive, specificity, and discard-precision analysis.

The current ground truth is human-supervised and AI-assisted. This provenance must be reported. A later independent human-only annotation pass is recommended for stronger publication claims.

## Initial academic model baseline

Selected initial model:

- Qwen3-30B-A3B-Instruct-2507;
- Q3_K_M;
- AMD Radeon RX 9060 XT 16 GB;
- `llama.cpp` / ROCm;
- initial context: 8192 tokens.

Qwen3-Coder is not used as the formal academic model. A previous one-paper run with the coder model is retained only as a pipeline smoke test.

## Publication-oriented experiment design

Experiments should, whenever possible, preserve:

1. immutable task definitions;
2. repository commit or document-set version;
3. exact model identifier and model hash;
4. quantization;
5. full inference configuration;
6. hardware/software environment;
7. raw results;
8. processed results and analysis scripts;
9. inclusion/exclusion criteria;
10. known limitations and failures;
11. prompt and dataset SHA-256 fingerprints;
12. ground-truth provenance.

Retrieval quality should be evaluated separately from generation quality. Planned retrieval metrics include Hit Rate@K, Precision@K, Recall@K, MRR and nDCG.

Energy analysis should prefer integrated energy over peak power whenever telemetry permits.

## Candidate publication lines

### Study A — Local vs hosted coding agents

Working concept: **Performance and Resource Trade-Offs of Local Coding Agents on Consumer Hardware**.

### Study B — Quantization and memory trade-offs

Study how quantization, context length and CPU/GPU offload affect code-task quality, latency and energy on a 16 GB GPU.

### Study C — Local academic screening and RAG

Evaluate whether a local instruction model can reduce literature-screening effort at high recall, then quantify the incremental effect of dense retrieval, hybrid retrieval, reranking and citation-aware RAG.

Potential endpoints include quality, reading reduction, latency, energy, retrieval effectiveness and evidence traceability.

## Publication policy

Do not select primary metrics after inspecting formal results. Before publication-oriented experiments, create a versioned benchmark protocol defining primary metrics, task selection, repetitions, ground-truth provenance and statistical analysis.
