# LocalAI-Lab

**Local LLM, RAG and Coding Agent Testbed on Consumer Hardware**

LocalAI-Lab is a private engineering and research project for building, operating and evaluating a local AI server with two primary workloads:

1. **AI-assisted software development**, using local coding models and agentic tools.
2. **Academic research and writing**, using literature screening, Retrieval-Augmented Generation (RAG), document analysis and scientific-writing workflows.

The project has two equally important goals:

- deliver a stable and useful local AI server for daily work;
- preserve enough technical documentation, telemetry and experimental rigor to support reproducible benchmarks and future academic publications.

## Current platform

- CPU: Intel Core i5-14600KF
- RAM: 64 GB
- GPU: AMD Radeon RX 9060 XT 16 GB (`gfx1200`)
- OS: Ubuntu Server 24.04.4 LTS
- Kernel: `7.0.0-30-generic`
- GPU stack: ROCm 10 / HIP
- Inference engine: `llama.cpp` with ROCm
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

Model switching is currently manual and explicit. systemd/autostart is intentionally deferred until manual benchmarking is complete.

## Coding stack status

Validated components:

- Qwen3-Coder-30B-A3B-Instruct Q3_K_M
- `llama.cpp` ROCm build for `gfx1200`
- OpenAI-compatible API over LAN
- OpenCode 1.18.27 on Windows
- controlled repository reading and writes

Formal B002 generation throughput is about 69.1 tok/s TG128, with roughly 14.4–14.7 GB VRAM usage.

## Academic stack status

The academic workflow has progressed beyond architecture design.

Implemented pipeline:

```text
PDF inventory
-> page-aware extraction
-> metadata normalization
-> duplicate detection + manual overrides
-> frozen screening dataset
-> ground truth
-> LLM-only screening baseline
-> later retrieval / reranking / RAG
```

Current corpus state:

- 25 PDFs processed successfully
- 274 pages
- 1,158,398 extracted characters
- 24 unique READY papers
- 1 duplicate excluded
- 0 unresolved duplicate documents

Initial academic model:

- Qwen3-30B-A3B-Instruct-2507
- Q3_K_M
- initial context: 8192
- planned API alias: `qwen3-academic`

The first executable LLM-only screening runner is available at `scripts/academic-rag/run_screening_baseline.py`. The formal A001 benchmark will compare model predictions against the frozen 24-paper ground truth before embeddings or RAG are introduced.

See `docs/academic-rag/current-status-2026-09-11.md` for the detailed current state.

## Academic RAG direction

- document framework: LlamaIndex preferred
- vector database: Qdrant
- retrieval: hybrid dense + sparse
- fusion: RRF initially
- embedding candidates: Qwen3-Embedding, BGE-M3, modern E5
- reranking candidates: Qwen3-Reranker
- chunking: structure-aware
- citation traceability: file/page/section/chunk

Retrieval and generation quality will be evaluated separately.

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
│   └── software/
├── benchmarks/
├── configs/
├── prompts/
├── results/
├── scripts/
└── services/
```

## Core principle

> Every major technical decision should be documented and, whenever possible, measurable.

## Status

**Version:** V0.1  
**Stage:** Working experimental platform; academic screening baseline in progress

The coding path is operational. The academic corpus, dataset builder, ground truth, prompt, and baseline runner are in place. The next formal milestone is Academic Screening A001 using the dedicated academic model, followed by controlled retrieval/RAG experiments.
