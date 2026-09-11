# Changelog

All notable changes to LocalAI-Lab will be documented here.

## [Unreleased] - 2026-09-11

### Added

- Deterministic academic-PDF inventory, extraction, metadata-normalization, duplicate-detection, dataset-builder, and baseline-screening scripts.
- Versioned Academic Screening v0.1 prompt and dataset schema.
- Frozen Academic Screening v0.1 dataset with 24 unique READY papers from 25 valid PDFs.
- Human-supervised / AI-assisted ground truth for the 24-paper screening set.
- LLM-only Academic Screening baseline runner (`run_screening_baseline.py`).
- Dedicated academic-model selection: Qwen3-30B-A3B-Instruct-2507 Q3_K_M.
- Detailed current-status documentation under `docs/academic-rag/current-status-2026-09-11.md`.

### Validated

- 25/25 PDFs extract successfully with PyMuPDF: 274 pages and 1,158,398 characters.
- Spaced abstract headings such as `A B S T R A C T` are recoverable; P011, P012, P015, and P021 now have abstracts.
- P023/P024 are duplicate content; P024 is excluded and P023 remains READY.
- Final normalization state: 24 READY, 0 metadata-review, 0 unresolved duplicates, 1 excluded.
- Screening dataset builder completes with 24 included papers.
- Baseline runner smoke test completes successfully for P001 with valid structured JSON, 4.311 s latency, 0 invalid outputs, and 0 errors.

### Decisions

- Qwen3-Coder is retained for coding-agent workloads only.
- Formal academic screening will use Qwen3-30B-A3B-Instruct-2507 rather than the coding-specialized model.
- The earlier Qwen3-Coder screening run is classified as a pipeline smoke test, not a formal academic result.
- The first formal academic benchmark remains LLM-only; embeddings/RAG will be added only after baseline quality is measured.

### Pending

- Complete Qwen3-30B-A3B-Instruct-2507 Q3_K_M validation on the RX 9060 XT.
- Run Academic Screening A001 on 1, 3, then all 24 papers.
- Add automatic metrics and confusion-matrix generation against ground truth.
- Add GPU telemetry and integrated-energy logging to formal academic runs.
- Benchmark embeddings, hybrid retrieval, reranking, Qdrant, and citation-aware RAG.
- Replace deprecated `import fitz` usage with `import pymupdf` and clean remaining escape warnings.

## [Unreleased] - 2026-09-02

### Added

- Formal benchmark **LAILAB-B002** for Qwen3-Coder-30B-A3B-Instruct Q3_K_M on the Radeon RX 9060 XT.
- Persistent storage layout using dedicated SSD mount points:
  - `/srv/models` for coding, academic, embedding, and reranker models.
  - `/srv/data` for datasets, papers, Qdrant data, benchmarks, and backups.
- Manual `llama-server` deployment using the validated Qwen3-Coder model.
- OpenAI-compatible API exposed over the local network for development testing.
- API-key authentication for the LAN validation endpoint.
- Windows + Visual Studio Code client validation.
- OpenCode 1.18.27 installation and connection to the local `llama-server` backend.
- End-to-end agent validation documentation under `docs/agents/`.
- Controlled repository-write validation from OpenCode.
- Local Python virtual environment and pytest setup for agent experiments.

### Validated

- Qwen3-Coder-30B-A3B-Instruct Q3_K_M reaches approximately 69.1 tok/s TG128 in direct `llama-bench` testing.
- The same model reaches approximately 64.2 tok/s in a small OpenAI-compatible API request from the Windows workstation.
- LAN communication between the Windows development workstation and the Ubuntu inference server.
- OpenCode repository exploration and multi-tool execution.
- OpenCode reasoning over B001 and B002 benchmark records.
- OpenCode creation of files inside a controlled experiment directory.

### Pending

- Capture a successful agent-driven pytest run.
- Validate a complete autonomous edit-test-fix-retest loop.
- Add systemd service management after manual benchmark validation is complete.
- Configure backup automation.
- Evaluate Qwen Code and Aider against the same backend.

## [0.1.0] - 2026-08-29

### Added

- Project name defined as **LocalAI-Lab**.
- Private GitHub repository initialized.
- Initial hardware platform defined:
  - Intel Core i5-14600KF
  - 64 GB RAM
  - AMD Radeon RX 9060 XT 16 GB
- Ubuntu Server 24.04 LTS selected as initial operating-system candidate.
- ROCm selected as GPU compute platform.
- `llama.cpp` selected as initial inference-engine candidate.
- Two operating profiles defined: coding and academic research/RAG.
- Qwen3-Coder family selected as initial coding-model candidate.
- Qwen3 family and alternative models identified for academic evaluation.
- Qwen3-Embedding and Qwen3-Reranker families identified as RAG candidates.
- Reproducibility, telemetry and future publication potential established as project requirements.
