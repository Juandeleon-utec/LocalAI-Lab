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

- [ ] Select main academic LLM.
- [ ] Benchmark candidate models on scientific tasks.
- [ ] Define PDF ingestion pipeline.
- [ ] Define structure-aware chunking strategy.
- [ ] Select embedding model.
- [ ] Select reranker.
- [ ] Select vector database.
- [ ] Implement citation-aware retrieval.
- [ ] Build academic evaluation dataset.

## Phase 5 — Service deployment

- [x] Expose OpenAI-compatible API on the LAN for manual validation.
- [ ] Create systemd services.
- [ ] Implement manual model switching profiles.
- [ ] Add health checks.
- [ ] Add structured logging.
- [ ] Add resource telemetry.
- [ ] Replace development API key with managed secret/configuration.

## Phase 6 — Experimental platform

- [ ] Record task metadata automatically.
- [ ] Record latency and throughput.
- [ ] Record VRAM/RAM usage.
- [ ] Record GPU/CPU utilization.
- [ ] Record power and energy where available.
- [ ] Record test results for coding tasks.
- [ ] Record number of agent iterations/tool calls.
- [ ] Store immutable benchmark runs with environment metadata.

## Phase 7 — Comparative studies

- [ ] Define identical coding tasks and controlled repository states.
- [ ] Compare local coding agents against Claude Code or other hosted agents.
- [ ] Analyze quality, latency, energy, privacy and cost.
- [ ] Evaluate academic RAG retrieval and citation quality.
- [ ] Prepare figures, tables and statistical analysis.
- [ ] Assess publication targets and release reproducibility artifacts where licensing permits.
