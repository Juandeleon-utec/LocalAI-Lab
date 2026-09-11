# Architecture Decision Log

This file records important technical decisions, alternatives and rationale. Decisions should be updated when new measurements justify a change.

## ADR-001 — Single large model loaded at a time

**Status:** Accepted

The server will initially load only one large LLM at a time.

### Rationale

The Radeon RX 9060 XT provides 16 GB of VRAM. Loading multiple large models concurrently would reduce usable context, increase memory pressure and complicate performance analysis. The expected workflow naturally supports multi-hour sessions dedicated either to coding or to academic work.

---

## ADR-002 — Headless Linux server

**Status:** Accepted

Ubuntu Server 24.04 LTS is the operating system for the current platform.

### Rationale

A graphical desktop is not required for normal operation. A headless system reduces unnecessary services and simplifies remote administration and reproducibility.

---

## ADR-003 — ROCm as primary GPU compute stack

**Status:** Accepted

ROCm/HIP is the primary GPU compute platform for the AMD Radeon RX 9060 XT.

### Validation requirement

The exact driver, kernel and ROCm versions used in each benchmark must be recorded.

---

## ADR-004 — llama.cpp as initial inference engine

**Status:** Accepted for current experiments

`llama.cpp` is the first inference engine used for coding and academic baselines.

### Rationale

The project requires explicit control and measurement of GPU offload, quantization, context length, KV cache, RAM/VRAM trade-offs and OpenAI-compatible serving.

Other engines may be introduced later and compared experimentally.

---

## ADR-005 — Benchmarkability is a design requirement

**Status:** Accepted

Every major service should expose enough telemetry to support reproducible experiments.

### Minimum run metadata

- model and exact model artifact;
- quantization;
- inference engine and version;
- prompt/task identifier;
- context length;
- generation parameters;
- wall-clock time;
- prompt and generation tokens;
- RAM/VRAM usage;
- CPU/GPU utilization;
- task outcome or test result;
- environment commit/version identifiers.

---

## ADR-006 — Production usefulness and research reproducibility must coexist

**Status:** Accepted

The system will be optimized for real daily use, but production convenience must not erase the information required to reproduce important experiments.

Configuration changes that can materially affect results should therefore be versioned in the repository.

---

## ADR-007 — Separate coding and academic LLM roles

**Status:** Accepted

Qwen3-Coder-30B-A3B-Instruct Q3_K_M is retained for coding-agent workloads. Academic screening will use a general instruction model, initially Qwen3-30B-A3B-Instruct-2507 Q3_K_M.

### Rationale

The coding model is specialized for software-development tasks and is not the preferred choice for literature relevance judgment. A general instruction model provides a cleaner baseline for academic screening and reduces task/model mismatch.

The previous one-paper academic-screening run with Qwen3-Coder is retained only as a pipeline smoke test.

---

## ADR-008 — Establish an LLM-only academic baseline before RAG

**Status:** Accepted

Academic Screening A001 will evaluate title + abstract + keywords directly with the academic LLM before embeddings, retrieval, reranking, or RAG are introduced.

### Rationale

A clean baseline is required to quantify whether later retrieval components improve quality rather than merely add complexity. Retrieval metrics and generation metrics will therefore be measured separately.

---

## ADR-009 — Freeze and audit the academic corpus before inference

**Status:** Accepted

The screening corpus must pass deterministic extraction, metadata validation and duplicate review before formal LLM evaluation.

### Current validated state

- 25 PDFs extracted successfully;
- 24 unique READY papers;
- P024 excluded as a duplicate of P023;
- 0 unresolved duplicate documents;
- frozen dataset and manifest generated under `/srv/data/benchmarks/academic-rag/`.

### Rationale

Corpus defects discovered after inference would invalidate comparisons and obscure whether errors originated in document parsing or model behavior.

---

## ADR-010 — Academic screening prioritizes recall of relevant literature

**Status:** Accepted

For literature screening, retaining relevant papers is more important than maximizing raw classification accuracy.

### Primary interpretation

Metrics must include recall for `class >= 2`, recall for class 3, and false-negative rate. A recall target such as 0.95 may be used as an experimental design goal, but must not be reported as achieved until measured.

---

## ADR-011 — Ground-truth provenance must be explicit

**Status:** Accepted

The current 24-paper ground truth is human-supervised and AI-assisted. This provenance must be recorded in reports.

### Publication implication

For stronger publication-quality claims, an independent human-only review should be considered so that label-assistance bias can be quantified or reduced.
