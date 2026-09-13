# Changelog

All notable changes to LocalAI-Lab will be documented here.

## [Unreleased] - 2026-09-13

### Added

- Formal A003 result report: `docs/academic-rag/a003-results-2026-09-13.md`.
- Academic Screening reproducibility audit: `docs/academic-rag/reproducibility-record-2026-09-13.md`.
- Versioned formal-run evidence under `results/academic-screening/` for A001 and A003.
- `results/academic-screening/README.md` documenting artifact semantics, run fingerprints, and A001/A003 comparison.
- Prompt v0.2: `prompts/academic-screening-v0.2.txt`.
- Deterministic reading-policy evaluator: `scripts/academic-rag/evaluate_reading_policy_a002.py`.

### Preserved evidence

Formal A001 repository artifacts now include:

- `manifest.json`
- `responses.jsonl`
- `predictions.csv`
- `comparison.csv`
- `evaluation.json`
- `evaluation.md`

Formal A003 repository artifacts include the same evidence set.

The raw `responses.jsonl` files are preserved as the closest records to the original model outputs. A separately checksummed full experiment archive is also retained outside Git for audit/reviewer use.

### Validated — A003

- Formal run: `A003-20260913T133722Z`.
- 24/24 responses successful and structurally valid; 0 invalid outputs and 0 errors.
- Wall time: 150.522 s.
- Throughput: 574.004 papers/hour.
- Token usage: 50,088 prompt tokens, 8,824 completion tokens, 58,912 total tokens.
- Dataset SHA-256: `f0f43a52042a791b9a341011b7bf831a9d82f754f02f0d66f16e5172301bccb2`.
- Prompt v0.2 SHA-256: `04dbcc97f7b1d604746a47ff295181eaa61c678b3673190fedbfa12bfb943539`.
- Exact 4-class accuracy: 0.542.
- Macro F1: 0.408.
- Relevant-paper recall: 1.000.
- Relevant-paper precision: 0.864.
- False-negative rate: 0.000.
- Class-3 recall: 0.500.
- Relevance-class MAE: 0.458.
- Quadratic weighted kappa: 0.488.
- Active-reading reduction: 0.083.
- Relevant retention: 1.000.

### A001/A003 interpretation

- A003 improves ordinal relevance calibration relative to A001.
- The binary screening confusion matrix is unchanged: 19 TP, 3 FP, 0 FN, 2 TN.
- A003 therefore does not improve relevant-paper precision or the number of papers selected for active reading beyond the deterministic A002 policy.
- Class-3 recall falls from 1.000 to 0.500, so prompt v0.2 is frozen as a development candidate rather than tuned further on the same 24-paper set.
- Further prompt optimization on Academic Screening v0.1 is avoided to reduce development-set overfitting.

### Reproducibility audit

The Git repository now contains the formal run outputs, prompts and analysis scripts, but a repository-only end-to-end reproduction still requires additional exact inputs. Missing or externally archived items include the frozen dataset CSV and manifest, full frozen ground-truth CSV, manual metadata overrides, normalized validation outputs, exact academic GGUF SHA-256, Python dependency snapshot, and automatic hardware/energy telemetry.

These gaps are explicitly tracked instead of being silently assumed complete.

### Next

- Version or immutably reference all remaining frozen Academic Screening v0.1 input artifacts.
- Record exact GGUF SHA-256 and Python environment snapshot.
- Extend Academic Screening to v0.2 with clearly irrelevant and borderline papers.
- Validate prompt v0.2 on an independent/expanded hold-out set without further tuning.
- Add VRAM/RAM/GPU utilization and integrated-energy telemetry.
- Begin B001 dense-retrieval experiments after defining structure-aware chunks and retrieval ground truth.

## [Unreleased] - 2026-09-12

### Added

- Dependency-free Academic Screening evaluator (`evaluate_screening_run.py`).
- Formal A001 result report: `docs/academic-rag/a001-results-2026-09-12.md`.
- Evaluation artifacts for formal runs: `evaluation.json`, `comparison.csv`, and `evaluation.md`.

### Validated

- Formal A001 completed with Qwen3-30B-A3B-Instruct-2507 Q3_K_M (`qwen3-academic`) on all 24 frozen papers.
- 24/24 responses were successful and structurally valid; 0 invalid outputs and 0 errors.
- A001 wall time: 136.522 s; throughput: 632.864 papers/hour.
- Token usage: 32,808 prompt tokens, 8,680 completion tokens, 41,488 total tokens.
- Relevant-paper recall (GT >= 2): 1.000.
- Relevant-paper precision: 0.864.
- False-negative rate: 0.000.
- Class-3 recall: 1.000.
- Exact 4-class accuracy: 0.417.
- Macro F1: 0.276.
- Relevance-class MAE: 0.708.
- Quadratic weighted kappa: 0.281.
- Current active-reading policy preserves all relevant papers but produces 0.000 reading reduction.

### Decisions

- Treat A001 as a high-recall but overly conservative baseline.
- Decouple relevance estimation from reading-policy selection.
- Evaluate deterministic reading actions derived from relevance before introducing RAG.
- Keep quality and efficiency as separate evaluation dimensions.
- Do not move directly to full RAG until A002/A003 separate policy, calibration, and evidence limitations.
- Preserve Academic Screening v0.1 as a frozen benchmark when a more balanced v0.2 dataset is created.

### Next

- Inspect A001 confusion patterns and binary false positives.
- Run A002 using a deterministic relevance-to-reading mapping.
- Define A003 as a controlled prompt-calibration experiment.
- Add clearly irrelevant papers in dataset v0.2.
- Add automatic VRAM/RAM/GPU utilization and integrated-energy telemetry.
- Begin retrieval experiments only after the LLM-only screening stages are characterized.

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
- Qwen3 family and alternative models identified as academic evaluation candidates.
- Qwen3-Embedding and Qwen3-Reranker families identified as RAG candidates.
- Reproducibility, telemetry and future publication potential established as project requirements.
