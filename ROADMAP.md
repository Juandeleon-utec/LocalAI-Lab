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
- [x] Build versioned screening dataset and manifest.
- [x] Create 24-paper ground truth.
- [x] Create versioned academic-screening prompt.
- [x] Implement LLM-only baseline runner.
- [x] Select initial academic LLM: Qwen3-30B-A3B-Instruct-2507 Q3_K_M.
- [x] Complete formal A001 run on all 24 papers with `qwen3-academic`.
- [x] Add automatic metric calculation and confusion-matrix output.
- [x] Document A001 results and methodological interpretation.
- [ ] Inspect A001 disagreement patterns and false positives in detail.
- [ ] Implement A002 deterministic reading policy derived from predicted relevance.
- [ ] Define and run A003 prompt-calibration experiment.
- [ ] Extend Academic Screening dataset to v0.2 with clearly irrelevant papers.
- [ ] Define structure-aware chunking strategy.
- [ ] Benchmark embedding models.
- [ ] Benchmark reranker models.
- [x] Select Qdrant as initial vector database.
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

## Phase 6 — Experimental platform

- [x] Record per-paper academic-screening latency and response validity.
- [x] Record dataset/prompt fingerprints in screening run manifests.
- [x] Store raw API responses and structured predictions.
- [x] Record formal A001 quality metrics against frozen ground truth.
- [ ] Record VRAM/RAM usage automatically per run.
- [ ] Record GPU/CPU utilization automatically per run.
- [ ] Record power and integrated energy.
- [ ] Record test results for coding tasks.
- [ ] Record number of agent iterations/tool calls.
- [ ] Store all formal benchmark runs immutably with environment metadata.

## Phase 7 — Comparative studies

- [ ] Define identical coding tasks and controlled repository states.
- [ ] Compare local coding agents against Claude Code or other hosted agents.
- [ ] Analyze quality, latency, energy, privacy and cost.
- [ ] Compare A001, A002 and A003 before introducing retrieval.
- [ ] Compare Academic Screening LLM-only baselines against retrieval-augmented configurations.
- [ ] Extend the academic corpus with clearly irrelevant papers to improve false-positive evaluation.
- [ ] Evaluate academic RAG retrieval and citation quality.
- [ ] Prepare figures, tables and statistical analysis.
- [ ] Assess publication targets and release reproducibility artifacts where licensing permits.
