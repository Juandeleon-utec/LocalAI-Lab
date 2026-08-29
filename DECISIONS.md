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

Ubuntu Server 24.04 LTS is the initial operating-system candidate.

### Rationale

A graphical desktop is not required for normal operation. A headless system reduces unnecessary services and simplifies remote administration and reproducibility.

---

## ADR-003 — ROCm as primary GPU compute stack

**Status:** Accepted

ROCm/HIP will be evaluated as the primary GPU compute platform for the AMD Radeon RX 9060 XT.

### Validation requirement

The exact driver, kernel and ROCm versions used in each benchmark must be recorded.

---

## ADR-004 — llama.cpp as initial inference engine

**Status:** Accepted for initial evaluation

`llama.cpp` will be the first inference engine evaluated.

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
