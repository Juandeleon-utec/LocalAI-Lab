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
10. known limitations and failures.

## Candidate publication lines

### Study A — Local vs hosted coding agents

Working concept: **Performance and Resource Trade-Offs of Local Coding Agents on Consumer Hardware**.

### Study B — Quantization and memory trade-offs

Study how quantization, context length and CPU/GPU offload affect code-task quality, latency and energy on a 16 GB GPU.

### Study C — Local academic RAG

Compare retrieval/reranking configurations and quantify citation reliability when querying scientific-paper collections.

## Publication policy

Do not select metrics after inspecting results. Before formal experiments, create a versioned benchmark protocol defining primary metrics, task selection, repetitions and statistical analysis.
