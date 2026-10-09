# LocalAI-Lab

## Operational coding profile update — 2026-10-08

The **currently running daily Qwen coding profile** is now Qwen3-Coder-30B-A3B-Instruct **Q3_K_M**, hosted by `llama-qwen-coder.service` and controlled through OliveTin. Its requested context is `114688` tokens (`--fit on --fit-target 1024 -np 1`), with `--jinja --metrics`, default sampling `--temp 0.7 --top-p 0.8 --top-k 20 --repeat-penalty 1.05`, and OpenAI-compatible alias `qwen3-coder` on port 8080. Actual context allocation can be adjusted by `--fit`, and clients can override sampling defaults.

For VS Code/OpenCode coding tasks, the **Qwen Coding Policy v1.2** is loaded as an `AGENTS.md` file in the *application's repository*, not through llama-server or OliveTin. Its canonical shareable template is `prompts/coding/qwen-coding-policy-v1.2.md`.

See [operational setup and validation](docs/agents/qwen-coding-policy-and-server-2026-10-08.md) and [versioned systemd unit template](services/systemd/llama-qwen-coder.service). These describe **today's operational profile** and do not alter the frozen benchmark conditions documented below. References below to Q4/48K/t0.1 describe the previous October 2 profile, not the current daily-use profile.


**Local LLM, RAG and Coding Agent Testbed on Consumer Hardware**

LocalAI-Lab is an engineering and research project for building, operating and evaluating a local AI server with two primary workloads:

1. **AI-assisted software development**, using local coding models and agentic tools.
2. **Academic research and writing**, using literature screening, Retrieval-Augmented Generation (RAG), document analysis and scientific-writing workflows.

The project has two equally important goals:

- deliver a stable and useful local AI server for daily work;
- preserve enough technical documentation, raw outputs, configuration, telemetry and experimental provenance to support reproducible benchmarks and future academic publications.

Practical usability is treated as part of the engineering problem rather than an afterthought. The planned operational layer will provide browser-based service control, chat/document workflows and project-file management while keeping formal benchmark execution isolated from convenience-state. The implementation checklist is tracked in `docs/architecture/operational-usability-roadmap.md`.

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

- `code` (daily/experimental): OpenCode + Qwen3-Coder-30B-A3B-Instruct Q4_K_M at 49,152 context (convenience profile; BENCH-CODE-DEV-002 currently favors the Q3 profile for the measured autonomous-development workload)
- `code-formal-baseline`: Qwen3-Coder-30B-A3B-Instruct Q3_K_M retained for frozen BENCH-CODE-001 conditions
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

The current Q4_K_M daily profile uses 49,152 context, 8,192 output and temperature 0.1. Exploratory long-context work is documented in `docs/benchmarks/qwen3-coder-q3-q4-2026-10-02.md`. A 10m17s real coding-agent session reached about 39K context without compaction and measured about 512.9 prompt tok/s and 29.7 generation tok/s as weighted llama.cpp session averages. These figures are not directly comparable with B002 because the workloads differ.

The initial 8K OpenCode validation is now treated as pilot evidence because context pressure/compaction was observed during larger code-generation work.

The first controlled coding-agent benchmark, **BENCH-CODE-001 v1.0**, is now preserved as the greenfield baseline:

- greenfield authenticated Node.js + MySQL web application;
- fixed REST/API and minimal frontend contract;
- 32K nominal context for local model comparisons;
- independent external hidden evaluator;
- three clean engineering runs per system;
- OpenCode + Qwen3-Coder as the local baseline;
- OpenCode + Qwen3.6 as the next local-model comparison;
- Claude Code as a hosted system-level baseline;
- Qwen3.6 + MTP evaluated separately for inference efficiency.

Benchmark definition: `benchmarks/tasks/BENCH-CODE-001/`.

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

The coding path is operational. BENCH-CODE-001 is preserved as the greenfield baseline and BENCH-CODE-DEV-002 now adds an existing-code integration benchmark with official and semantically audited results. The academic screening baseline and prompt-calibration stages are complete. Near-term coding work is the same-scale Qwen3 Instruct control, followed by additional local/hosted comparisons under frozen protocols.

<!-- BENCH-CODE-DEV-002-2026-10-08 -->
## BENCH-CODE-DEV-002 — existing-code development benchmark

A second coding benchmark is now preserved under `benchmarks/tasks/BENCH-CODE-DEV-002/`. It evaluates one-pass modification of an existing Node.js/Express/MySQL application: adding administrative vehicle management while preserving current behavior.

The frozen v1.8 protocol uses a 49,152-token context budget, zero corrective human interventions and an external API/restart/Playwright evaluator. A complementary Semantic Audit v2 preserves the official scores while removing vacuous PASS cases caused by generic route-level 404 responses.

Current audited results:

| Model | Audited main | Audited critical | Critical completion | Restart | E2E | Wall time | Prompt tok/s | Gen tok/s | Result |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Qwen3-Coder-Next ~80B-A3B Q3_K_M | 12/18 | 10/15 | **66.7%** | 2/2 | 0/6 | 737.994 s | 277.218 | 30.0023 | FAIL |
| Qwen3-Coder-30B-A3B Q3_K_M | 12/18 | 10/15 | **66.7%** | 1/2 | 1/6 | **535.188 s** | **656.087** | 36.2531 | FAIL |
| Qwen3-Coder-30B-A3B Q4_K_M | — | — | **N/A (startup)** | — | — | 843.555 s | 611.408 | 30.7436 | **FAIL_STARTUP** |
| Qwen3.6-35B-A3B Q4_K_M | 5/18 | 5/15 | **33.3%** | 1/2 | 0/6 | 987.068 s | 628.782 | **40.6422** | FAIL |

`Prompt tok/s` measures prompt/context processing throughput; `Gen tok/s` measures generated-token throughput. These are efficiency metrics and are not used as functional PASS criteria.

Under this benchmark, Coder-Next ~80B Q3 provides the strongest persistence/backend evidence, while Coder-30B Q3 provides the strongest quality/efficiency trade-off. The 30B Q4 result is a candidate startup failure caused by an invalid duplicated Sequelize association alias. Qwen3.6 R2 completed, but its vehicle routes were not integrated into the live router.

Detailed results: `benchmarks/results/BENCH-CODE-DEV-002/`.

The next planned controlled comparison is Qwen3-30B-A3B-Instruct-2507 Q3_K_M as a same-scale general-instruction control against the specialized Coder-30B Q3 profile.
