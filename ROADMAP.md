# LocalAI-Lab Roadmap

## Phase 0 — Project definition

- [x] Define project goals.
- [x] Create private GitHub repository.
- [x] Define initial hardware.
- [x] Define coding and academic operating modes.
- [x] Define reproducibility and benchmarking as first-class goals.

## Phase 1 — Base server

- [ ] Install Ubuntu Server 24.04 LTS.
- [ ] Configure SSH.
- [ ] Configure VPN access.
- [ ] Install system monitoring tools.
- [ ] Install Git and development utilities.
- [ ] Define storage layout.
- [ ] Configure backups.
- [ ] Record complete software and firmware inventory.

## Phase 2 — AMD GPU / ROCm

- [ ] Install AMD GPU drivers.
- [ ] Install ROCm.
- [ ] Validate GPU detection and HIP.
- [ ] Run ROCm diagnostic tests.
- [ ] Compile `llama.cpp` with ROCm support.
- [ ] Run first GPU-offloaded model.
- [ ] Record baseline GPU thermals, power and memory behavior.

## Phase 3 — Coding stack

- [ ] Select Qwen3-Coder quantization.
- [ ] Define context-size profiles.
- [ ] Measure prompt and generation throughput.
- [ ] Measure RAM and VRAM usage.
- [ ] Evaluate OpenCode.
- [ ] Evaluate Qwen Code.
- [ ] Evaluate Aider.
- [ ] Define local coding-agent workflow.
- [ ] Create controlled coding benchmark dataset.

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

- [ ] Expose OpenAI-compatible API.
- [ ] Create systemd services.
- [ ] Implement manual model switching.
- [ ] Add health checks.
- [ ] Add structured logging.
- [ ] Add resource telemetry.

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
