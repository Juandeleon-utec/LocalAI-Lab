# LocalAI-Lab

**Local LLM, RAG and Coding Agent Testbed on Consumer Hardware**

LocalAI-Lab is a private engineering and research project for building, operating and evaluating a local AI server with two primary workloads:

1. **AI-assisted software development**, using local coding models and agentic tools.
2. **Academic research and writing**, using literature screening, Retrieval-Augmented Generation (RAG), document analysis and scientific-writing workflows.

The project has two equally important goals:

- deliver a stable and useful local AI server for daily work;
- preserve enough technical documentation, raw outputs, configuration, telemetry and experimental provenance to support reproducible benchmarks and future academic publications.

## Current platform

- CPU: Intel Core i5-14600KF
- RAM: 64 GB
- GPU: AMD Radeon RX 9060 XT 16 GB (`gfx1200`)
- OS: Ubuntu Server 24.04.4 LTS
- Kernel: `7.0.0-30-generic`
- GPU stack: ROCm 10 / HIP 7.15.26333
- Inference engine: `llama.cpp` with ROCm
- `llama.cpp`: build/tag `b10752`, commit `b96806d96061049a5b574269b049bf6241d63d46`
- API: OpenAI-compatible `llama-server`
- Remote administration: SSH over LAN
- Graphical desktop: not required

Persistent storage:

```text
/srv/models  -> model artifacts
/srv/data    -> datasets, papers, Qdrant data, benchmarks, backups
```

## Current operating modes

Only one large GPU model is intended to be active at a time.

- `code`: OpenCode + Qwen3-Coder-30B-A3B-Instruct Q3_K_M
- `research`: academic screening/RAG + Qwen3-30B-A3B-Instruct-2507 Q3_K_M

Model switching is currently manual and explicit. systemd/autostart remains intentionally deferred while benchmark behavior is being characterized.

## Coding stack status

Validated components:

- Qwen3-Coder-30B-A3B-Instruct Q3_K_M
- `llama.cpp` ROCm build for `gfx1200`
- OpenAI-compatible API over LAN
- OpenCode 1.18.27 on Windows
- controlled repository reading and writes

Formal B002 generation throughput is about 69.1 tok/s TG128, with roughly 14.4–14.7 GB VRAM usage.

## Academic stack status

Implemented pipeline:

```text
PDF inventory
-> page-aware extraction
-> metadata normalization
-> duplicate detection + manual overrides
-> frozen screening dataset
-> ground truth
-> LLM-only screening baseline
-> prompt calibration
-> later retrieval / reranking / RAG
```

Corpus state used for Academic Screening v0.1:

- 25 PDFs processed successfully
- 274 pages
- 1,158,398 extracted characters
- 24 unique READY papers
- P024 excluded as duplicate of P023
- 0 unresolved duplicate documents

Academic model used in the formal screening experiments:

- Qwen3-30B-A3B-Instruct-2507
- Q3_K_M
- GGUF: `Qwen_Qwen3-30B-A3B-Instruct-2507-Q3_K_M.gguf`
- context: 8192
- API alias: `qwen3-academic`

## Formal Academic Screening results

Two formal 24-paper runs are now preserved in Git under `results/academic-screening/`.

| Metric | A001 | A003 |
| --- | ---: | ---: |
| Exact 4-class accuracy | 0.417 | 0.542 |
| Macro F1 | 0.276 | 0.408 |
| Relevant-paper recall (`GT >= 2`) | 1.000 | 1.000 |
| Relevant-paper precision | 0.864 | 0.864 |
| False-negative rate | 0.000 | 0.000 |
| Class-3 recall | 1.000 | 0.500 |
| Relevance-class MAE | 0.708 | 0.458 |
| Quadratic weighted kappa | 0.281 | 0.488 |

A001 used `prompts/academic-screening-v0.1.txt`. A003 used the stricter `prompts/academic-screening-v0.2.txt`. A003 improved ordinal relevance calibration while leaving the binary relevant/non-relevant confusion matrix unchanged at 19 TP, 3 FP, 0 FN and 2 TN.

A001 model-generated reading decisions produced no reading reduction. Applying the deterministic A002 policy to A001 produced an 8.3% reduction while retaining all 19 relevant papers. A003 also produced 8.3% reading reduction and 100% relevant retention.

Detailed reports:

- `docs/academic-rag/a001-results-2026-09-12.md`
- `docs/academic-rag/a003-results-2026-09-13.md`
- `docs/academic-rag/reproducibility-record-2026-09-13.md`
- `results/academic-screening/README.md`

## Reproducibility model

Formal screening run directories preserve:

- run manifest;
- raw API responses;
- parsed predictions;
- prediction/ground-truth comparison;
- machine-readable evaluation metrics;
- human-readable evaluation report.

The run manifests also record prompt and dataset SHA-256 fingerprints, generation parameters, token usage, wall time and throughput.

The repository audit found that the run outputs are well preserved but exact repository-only end-to-end reproduction is not yet complete. The frozen dataset CSV, dataset manifest, full ground-truth CSV, manual metadata overrides, normalized validation outputs, exact model SHA-256 and Python dependency snapshot should also be versioned or immutably archived. These gaps are tracked in `docs/academic-rag/reproducibility-record-2026-09-13.md`.

A separate checksummed evidence archive is also retained outside Git for reviewer/audit use.

## Academic RAG direction

- document framework: LlamaIndex preferred
- vector database: Qdrant
- retrieval: hybrid dense + sparse
- fusion: RRF initially
- embedding candidates: Qwen3-Embedding, BGE-M3, modern E5
- reranking candidates: Qwen3-Reranker
- chunking: structure-aware
- citation traceability: file/page/section/chunk

Retrieval and generation quality will be evaluated separately. The next retrieval milestone is a controlled dense-retrieval baseline before hybrid retrieval or full RAG.

## Research dimension

Potential studies include:

- local vs cloud coding agents;
- quality vs latency trade-offs;
- quantization and context-length effects;
- VRAM/RAM offloading strategies;
- energy per task;
- coding-agent task completion and iteration count;
- academic screening recall and reading reduction;
- retrieval and citation quality;
- hallucination and evidence-traceability analysis;
- privacy and operational cost.

## Repository structure

```text
LocalAI-Lab/
├── README.md
├── CHANGELOG.md
├── ROADMAP.md
├── DECISIONS.md
├── RESEARCH.md
├── docs/
│   ├── academic-rag/
│   ├── agents/
│   ├── architecture/
│   ├── benchmarks/
│   ├── hardware/
│   ├── publications/
│   └── software/
├── benchmarks/
├── configs/
├── prompts/
├── results/
│   ├── academic-rag/
│   └── academic-screening/
├── scripts/
└── services/
```

## Core principle

> Every major technical decision should be documented and, whenever possible, measurable. Formal results must preserve the provenance chain from exact input and prompt to raw response and derived metric.

## Status

**Version:** V0.1  
**Stage:** Working experimental platform; A001/A002/A003 academic screening characterization complete, reproducibility hardening and retrieval baseline next.

The coding path is operational. The academic screening baseline and prompt-calibration stages are complete. The next priorities are to close the remaining reproducibility gaps, extend the screening benchmark with class-0/borderline papers, add automatic telemetry, and begin controlled dense-retrieval experiments.
