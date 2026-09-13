# LocalAI-Lab Roadmap

## Phase 0 — Project definition

- [x] Define project goals.
- [x] Create private GitHub repository.
- [x] Define initial hardware.
- [x] Define coding and academic operating modes.
- [x] Define reproducibility and benchmarking as first-class goals.

## Phase 1 — Base server

- [x] Install Ubuntu Server 24.04 LTS.
- [x] Configure SSH.
- [x] Confirm LAN-only remote administration strategy for the current phase.
- [x] Install system monitoring tools.
- [x] Install Git and development utilities.
- [x] Define storage layout.
- [ ] Configure backups.
- [x] Record complete software and firmware inventory.

## Phase 2 — AMD GPU / ROCm

- [x] Install AMD GPU drivers.
- [x] Install ROCm.
- [x] Validate GPU detection and HIP.
- [x] Run ROCm diagnostic tests.
- [x] Compile `llama.cpp` with ROCm support.
- [x] Run first GPU-offloaded model.
- [x] Record baseline GPU thermals, power and memory behavior.

## Phase 3 — Coding stack

- [x] Select initial Qwen3-Coder quantization: Qwen3-Coder-30B-A3B-Instruct Q3_K_M.
- [x] Define initial context-size profile: 8K for agent validation.
- [x] Measure prompt and generation throughput.
- [x] Measure RAM/VRAM behavior for the selected coder model.
- [x] Evaluate OpenCode for repository reading and controlled writes.
- [ ] Evaluate Qwen Code.
- [ ] Evaluate Aider.
- [x] Validate initial local coding-agent workflow over LAN.
- [ ] Create controlled coding benchmark dataset.
- [ ] Validate autonomous edit-test-fix loop.

## Phase 4 — Academic stack

- [x] Define deterministic PDF inventory and extraction pipeline.
- [x] Normalize metadata and add duplicate detection/manual overrides.
- [x] Freeze Academic Screening v0.1 corpus: 24 unique READY papers.
- [x] Build versioned screening dataset and manifest on the experiment server.
- [x] Create 24-paper ground truth.
- [x] Create versioned academic-screening prompt v0.1.
- [x] Implement LLM-only baseline runner.
- [x] Select initial academic LLM: Qwen3-30B-A3B-Instruct-2507 Q3_K_M.
- [x] Complete formal A001 run on all 24 papers with `qwen3-academic`.
- [x] Add automatic metric calculation and confusion-matrix output.
- [x] Document A001 results and methodological interpretation.
- [x] Inspect A001 disagreement patterns and false positives in detail.
- [x] Implement A002 deterministic reading policy derived from predicted relevance.
- [x] Define and run A003 prompt-calibration experiment.
- [x] Document A003 results and A001/A003 comparison.
- [x] Freeze prompt v0.2 as a development candidate after A003.
- [ ] Extend Academic Screening dataset to v0.2 with clearly irrelevant and borderline papers.
- [ ] Validate prompt v0.2 on an independent or expanded hold-out set without further tuning.
- [ ] Define structure-aware chunking strategy.
- [ ] Benchmark embedding models.
- [ ] Benchmark reranker models.
- [x] Select Qdrant as initial vector database.
- [ ] Implement dense-retrieval baseline B001.
- [ ] Implement hybrid dense+sparse retrieval.
- [ ] Implement citation-aware retrieval.
- [ ] Evaluate retrieval separately with Hit Rate@K, Precision@K, Recall@K, MRR and nDCG.

## Phase 5 — Service deployment

- [x] Expose OpenAI-compatible API on the LAN for manual validation.
- [ ] Create systemd services.
- [ ] Implement manual model-switching profiles.
- [ ] Add health checks.
- [ ] Add structured logging.
- [ ] Add resource telemetry.
- [ ] Replace development API key with managed secret/configuration.
- [ ] Build lightweight FastAPI/HTML control panel after core benchmark validation.

## Phase 6 — Experimental platform and reproducibility

- [x] Record per-paper academic-screening latency and response validity.
- [x] Record dataset/prompt fingerprints in screening run manifests.
- [x] Store raw API responses and structured predictions.
- [x] Record formal A001 quality metrics against frozen ground truth.
- [x] Record formal A003 quality metrics against frozen ground truth.
- [x] Version A001/A003 manifests, raw responses, predictions, comparisons and evaluations in Git.
- [x] Create a separately checksummed archival snapshot of the academic-screening experiments.
- [x] Audit repository reproducibility and document remaining gaps.
- [ ] Version or immutably reference the exact frozen `papers-v0.1.csv` and dataset manifest used in A001/A003.
- [ ] Version or immutably reference the exact full `ground-truth-v0.1.csv` used in evaluation.
- [ ] Version manual metadata overrides and normalized corpus validation outputs used to build v0.1.
- [ ] Record SHA-256 of every model artifact used in formal runs.
- [ ] Capture a Python/dependency environment snapshot for formal academic runs.
- [ ] Record the LocalAI-Lab repository commit used at experiment execution time in future manifests.
- [ ] Record VRAM/RAM usage automatically per run.
- [ ] Record GPU/CPU utilization automatically per run.
- [ ] Record power and integrated energy.
- [ ] Record test results for coding tasks.
- [ ] Record number of agent iterations/tool calls.
- [ ] Define an immutable artifact policy for all future formal benchmark runs.

## Phase 7 — Comparative studies

- [ ] Define identical coding tasks and controlled repository states.
- [ ] Compare local coding agents against Claude Code or other hosted agents.
- [ ] Analyze quality, latency, energy, privacy and cost.
- [x] Compare A001, A002 and A003 before introducing retrieval.
- [ ] Compare Academic Screening LLM-only baselines against retrieval-augmented configurations.
- [ ] Extend the academic corpus with clearly irrelevant papers to improve false-positive evaluation.
- [ ] Evaluate academic RAG retrieval and citation quality.
- [ ] Prepare figures, tables and statistical analysis.
- [ ] Assess publication targets and release reproducibility artifacts where licensing permits.

## Immediate priority order after A003

1. Close the frozen-input reproducibility gaps identified in `docs/academic-rag/reproducibility-record-2026-09-13.md`.
2. Add model hashing, environment capture and run telemetry before the next publication-oriented experiment.
3. Build Academic Screening v0.2/hold-out with class-0 and borderline papers.
4. Define structure-aware chunks and retrieval ground truth.
5. Benchmark embedding candidates and run B001 dense retrieval.
6. Add hybrid retrieval, reranking and citation-aware RAG only after retrieval metrics are understood.
