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

Raw benchmark measurements should remain under `benchmarks/results/` and be linked to a study through run identifiers rather than duplicated manually.

## Candidate studies

1. Local vs hosted coding agents on controlled software-engineering tasks.
2. Quantization, context and CPU/GPU offload trade-offs on a 16 GB consumer AMD GPU.
3. Retrieval/reranking strategies for citation-grounded academic RAG.
4. Energy and latency trade-offs for local AI workloads.

## Good research practice

Before collecting publication-quality results:

- freeze a protocol version;
- define hypotheses and primary metrics;
- define task inclusion/exclusion criteria;
- record environment and software versions;
- decide repetition count;
- define failure handling;
- preserve raw data;
- version analysis scripts;
- document deviations from the protocol.
