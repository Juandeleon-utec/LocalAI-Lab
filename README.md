# LocalAI-Lab

**Local LLM, RAG and Coding Agent Testbed on Consumer Hardware**

LocalAI-Lab is a private engineering and research project for building, operating and evaluating a local AI server with two primary workloads:

1. **AI-assisted software development**, using local coding models and agentic tools.
2. **Academic research and writing**, using Retrieval-Augmented Generation (RAG), document analysis and scientific-writing workflows.

The project has two equally important goals:

- deliver a stable and useful local AI server for daily work;
- preserve enough technical documentation, telemetry and experimental rigor to support reproducible benchmarks and future academic publications.

## Initial platform

- CPU: Intel Core i5-14600KF
- RAM: 64 GB
- GPU: AMD Radeon RX 9060 XT 16 GB
- GPU stack: ROCm / HIP
- Operating system candidate: Ubuntu Server 24.04 LTS
- Graphical desktop: not required

## Initial technical direction

- Inference engine: `llama.cpp` with ROCm
- API: OpenAI-compatible local endpoint
- Coding model family: Qwen3-Coder
- Academic/research model family: Qwen3 and alternatives to be benchmarked
- Embeddings: Qwen3-Embedding family
- Reranking: Qwen3-Reranker family
- Vector database: to be evaluated experimentally
- Remote access: SSH + VPN
- Deployment: systemd and/or containers

## Operating modes

The server is not expected to keep multiple large language models loaded simultaneously.

- `code`: coding model + coding-agent tools
- `research`: academic model + RAG services

Model switching will initially be manual and explicit.

## Research dimension

LocalAI-Lab will be designed from the beginning as an experimental platform. Potential studies include:

- local vs cloud coding agents;
- quality vs latency trade-offs;
- VRAM/RAM offloading strategies;
- quantization effects;
- context-length effects;
- energy consumption and energy per task;
- task-completion rate and test pass rate;
- agent iteration count and tool usage;
- privacy and operational cost;
- retrieval and citation quality in academic RAG.

A future coding-agent comparison may include, for example:

- Claude Code;
- OpenCode + local Qwen coder;
- Qwen Code + local Qwen coder;
- additional local or hosted agents under identical tasks and repositories.

## Repository structure

```text
LocalAI-Lab/
├── README.md
├── CHANGELOG.md
├── ROADMAP.md
├── DECISIONS.md
├── RESEARCH.md
├── .gitignore
├── docs/
│   ├── architecture/
│   ├── hardware/
│   ├── software/
│   ├── rag/
│   ├── agents/
│   └── benchmarks/
├── benchmarks/
│   ├── tasks/
│   └── results/
├── configs/
├── scripts/
├── services/
└── notebooks/
```

## Core principle

> Every major technical decision should be documented and, whenever possible, measurable.

## Status

**Version:** V0.1  
**Stage:** Architecture and experimental-platform definition

No production benchmark results are available yet. The current phase focuses on architecture, hardware/software selection, reproducibility and experiment design.
