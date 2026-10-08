# LocalAI-Lab Roadmap

## Phase 0 — Project definition

- [x] Define project goals.
- [x] Create GitHub repository.
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
- [x] Reclassify the 8K coding-agent work as pilot evidence after context pressure/compaction was observed.
- [x] Define 32K as the nominal local context budget for formal BENCH-CODE-001 comparisons.
- [x] Measure prompt and generation throughput.
- [x] Complete direct Q3_K_M vs Q4_K_M paired throughput benchmark (LAILAB-B003): Q3 69.33 tok/s TG128 vs Q4 56.22 tok/s TG128.
- [x] Measure RAM/VRAM behavior for the selected coder model.
- [x] Evaluate OpenCode for repository reading and controlled writes.
- [ ] Evaluate Qwen Code.
- [ ] Evaluate Aider.
- [x] Validate initial local coding-agent workflow over LAN.
- [x] Validate Q4_K_M 48K real-world CODE-FIX-001 workflow through production deployment: Users and Transporters Edit flows confirmed working (2026-10-05).
- [x] Define BENCH-CODE-001 v1.0: authenticated Node.js/MySQL web-application task.
- [x] Freeze participant prompt, execution protocol, evaluator contract and blinded-review rubric before formal runs.
- [x] Implement and checksum the external hidden evaluator for BENCH-CODE-001.
- [x] Add the public staging harness and clean ephemeral MySQL-per-run reset procedure.
- [x] Complete static validation of reference candidate, hidden evaluator and result aggregation.
- [ ] Select and freeze the physical benchmark/staging host.
- [x] Validate Windows preflight and two clean MySQL create/healthy/destroy cycles on the Ryzen 7 5700G workstation.
- [x] Validate the hidden evaluator and harness against a known-good reference implementation on the Windows engineering-validation host (16/16 total, 14/14 critical).
- [x] Freeze the BENCH-CODE-001 formal inputs/environment fingerprints used for the completed local runs.
- [x] Validate autonomous one-shot coding execution and external evaluation under BENCH-CODE-001.
- [x] Run Qwen3-Coder-30B-A3B-Instruct Q3_K_M at 32K (A01/A02/A03: 3/3 clean PASS).
- [x] Integrate and benchmark Qwen3.6-35B-A3B Q4_K_M under BENCH-CODE-001 (B01/B02/B03 completed; 0/3 clean deployments).
- [ ] Evaluate Qwen3.6 MTP as a separate inference-efficiency factor.

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

## Phase 5 — Service deployment, usability and web control plane

The server is not only an experimental benchmark host. It should also become practical for daily model testing, coding, academic review and document work without sacrificing reproducibility.

The implementation should therefore separate **daily laboratory usability** from **formal benchmark execution**. Convenience layers may control services and projects, but formal experiments must still use frozen commands/configurations, clean runtime state and immutable artifacts.

Detailed implementation checklist: `docs/architecture/operational-usability-roadmap.md`.

### 5.1 — Service profiles and process control

- [x] Expose OpenAI-compatible API on the LAN for manual validation.
- [ ] Define versioned service profiles for each operational mode/model.
- [ ] Create systemd services or controlled wrapper scripts for validated `llama-server` profiles.
- [ ] Add service wrappers for Ollama and JupyterLab where appropriate.
- [ ] Implement safe start/stop/switch logic for large GPU models.
- [ ] Enforce the operating rule of one large GPU model loaded at a time.
- [ ] Add a global STOP ALL action.
- [ ] Verify process termination and VRAM release before another large model starts.
- [ ] Add health/readiness checks for each backend.
- [ ] Expose useful states: STOPPED, STARTING, READY, STOPPING and ERROR.
- [ ] Add structured logs for service transitions and failures.
- [ ] Add resource-status commands for GPU, VRAM, RAM, disk and active ports.
- [ ] Replace development API keys with managed configuration/secrets before broader exposure.

### 5.2 — OliveTin operational control panel

Initial control-plane implementation target: **OliveTin**, backed by versioned YAML actions and scripts rather than a custom application.

- [ ] Install OliveTin as a LAN-only administration interface.
- [ ] Require authentication before exposing operational actions.
- [ ] Version the OliveTin configuration in this repository.
- [ ] Add start/stop/status/log actions for Qwen3-Coder `llama-server`.
- [ ] Add start/stop/status/log actions for Qwen3.6 `llama-server`.
- [ ] Add start/stop/status actions for Ollama.
- [ ] Add start/stop/status actions for JupyterLab.
- [ ] Add GPU/RAM/disk/port status actions.
- [ ] Add a safe model-switch action that stops the current large model, checks VRAM release, starts the target profile and validates health.
- [ ] Add a benchmark-preparation action that checks/cleans known runtime contamination sources without modifying frozen benchmark inputs.
- [ ] Keep arbitrary privileged shell execution disabled; grant only narrowly scoped commands required by the panel.
- [ ] Evaluate a custom FastAPI/HTML control panel only if OliveTin becomes a measurable usability limitation.

Planned control flow:

```text
Browser
  -> OliveTin
  -> versioned action / wrapper script
  -> systemd or controlled process
  -> stop current large model if needed
  -> verify termination and VRAM release
  -> start selected profile
  -> health check
  -> READY
```

### 5.3 — Web chat and academic-review workspace

Initial user-facing chat target: **Open WebUI** connected to the active local backend through Ollama and/or an OpenAI-compatible `llama-server` endpoint.

- [ ] Deploy Open WebUI on the LAN.
- [ ] Connect Open WebUI to validated `llama-server` OpenAI-compatible profiles.
- [ ] Connect Open WebUI to Ollama for exploratory model use.
- [ ] Create an Academic Reviewer profile/system prompt separate from formal Academic Screening benchmark prompts.
- [ ] Add reusable chat profiles for coding, academic review and later teaching-content workflows.
- [ ] Validate PDF/document upload and persistent Knowledge/RAG collections.
- [ ] Preserve the distinction between convenience RAG in Open WebUI and formal retrieval experiments implemented/evaluated under the Academic RAG benchmark.
- [ ] Require source-grounded answers and document/page traceability where the interface supports it.
- [ ] Measure whether the interface introduces unacceptable duplication, hidden preprocessing or loss of reproducibility before using it for formal experiments.

### 5.4 — Browser-based project/file management

The daily workflow should not require SCP for normal project creation and document upload.

Initial file-management candidate: **Copyparty** or an equivalently lightweight maintained web file manager.

- [ ] Deploy a LAN-only browser file manager with authentication and restricted roots.
- [ ] Use `/srv/data/projects/` as the initial project root.
- [ ] Allow project-directory creation from the browser.
- [ ] Allow drag-and-drop upload of PDFs, DOCX, BibTeX, notes and datasets.
- [ ] Restrict write access to project/data paths; do not expose model/system directories unnecessarily.
- [ ] Define a standard project layout:

```text
/srv/data/projects/<project>/
  sources/
  notes/
  extracted/
  index/
  output/
```

### 5.5 — Project-to-Knowledge/RAG synchronization

- [ ] Implement a versioned `localai-create-project` script that creates the standard directory layout safely.
- [ ] Expose project creation through OliveTin with a validated project-name argument.
- [ ] Implement a versioned `localai-index-project` command.
- [ ] Synchronize `sources/` into an Open WebUI Knowledge collection or the formal LocalAI-Lab RAG pipeline, depending on operating mode.
- [ ] Avoid duplicate ingestion when a source file/hash has not changed.
- [ ] Preserve file identity, source path, page/section metadata and content hashes where possible.
- [ ] Add an OliveTin action to index/reindex a selected project.
- [ ] Add an action to inspect index/Knowledge status without destroying the underlying source files.
- [ ] Keep formal RAG indexes/versioned datasets independent from disposable convenience indexes.

Planned daily academic workflow:

```text
Browser file manager
  -> create /srv/data/projects/<project>
  -> upload source documents
  -> OliveTin: index project
  -> Open WebUI: select Academic Reviewer + project Knowledge
  -> chat / review / compare documents
  -> save outputs under project output/
```

### 5.6 — Laboratory mode vs benchmark mode

- [ ] Define an explicit **laboratory mode** for convenience services: OliveTin, Open WebUI, file manager, Ollama, Jupyter and manually selected `llama-server` profiles.
- [ ] Define an explicit **benchmark mode** with frozen launch commands, exact model/config hashes, clean runtime checks and controlled telemetry.
- [ ] Ensure convenience services cannot silently modify benchmark prompt, seed, evaluator or candidate artifacts.
- [ ] Before a formal benchmark, verify/clean expected ports, residual containers, processes and GPU state.
- [ ] Record which convenience services remained active during each benchmark; preferably stop unrelated GPU/process workloads.
- [ ] Keep benchmark generation and clean evaluation as independent phases.
- [ ] Preserve failed runs and contamination findings rather than silently repairing them.
- [ ] Add usability measurements where useful: number of manual steps, setup time, project-switch time and required terminal commands.

### 5.7 — Usability acceptance checks

The operational platform should eventually satisfy these practical checks:

- [ ] Start/stop a validated LLM from a browser without manually reconstructing its long command line.
- [ ] See whether each major service is running and whether its health endpoint is READY.
- [ ] Switch between two validated large-model profiles safely.
- [ ] Open JupyterLab without manual server-side process management.
- [ ] Create an academic project from the browser.
- [ ] Upload project files without SCP.
- [ ] Index/reindex the project from the browser.
- [ ] Open a chat interface, select a local model/reviewer profile and query the project documents.
- [ ] Recover logs/status when a model fails to start.
- [ ] Return the machine to a known-clean benchmark state with a documented procedure.
- [ ] Reproduce a formal benchmark without depending on undocumented state created by the convenience interfaces.

## Phase 6 — Experimental platform and reproducibility

- [x] Record per-paper academic-screening latency and response validity.
- [x] Record dataset/prompt fingerprints in screening run manifests.
- [x] Store raw API responses and structured predictions.
- [x] Record formal A001 quality metrics against frozen ground truth.
- [x] Record formal A003 quality metrics against frozen ground truth.
- [x] Version A001/A003 manifests, raw responses, predictions, comparisons and evaluations in Git.
- [x] Create a separately checksummed archival snapshot of the academic-screening experiments.
- [x] Audit repository reproducibility and document remaining gaps.
- [x] Version the exact frozen `papers-v0.1.csv` and dataset manifest used in A001/A003; the dataset CSV matches the SHA-256 recorded in both run manifests.
- [x] Version the exact full `ground-truth-v0.1.csv` used in evaluation and record its SHA-256.
- [x] Version manual metadata overrides, normalized metadata, duplicate candidates, and corpus-validation outputs used to build v0.1.
- [x] Record the SHA-256 of the preserved Qwen3 academic GGUF used for A001/A003; the hash was captured post hoc and is documented as such.
- [x] Preserve a post-run Python/dependency snapshot from 2026-09-20 (Python 3.12.3, PyMuPDF 1.28.2); keep the exact A001/A003 package state marked as not independently proven.
- [ ] Record the LocalAI-Lab repository commit used at experiment execution time in future manifests.
- [ ] Record VRAM/RAM usage automatically per run.
- [ ] Record GPU/CPU utilization automatically per run.
- [ ] Record power and integrated energy.
- [ ] Record test results for coding tasks.
- [ ] Record number of agent iterations/tool calls.
- [ ] Define an immutable artifact policy for all future formal benchmark runs.

## Phase 7 — Comparative studies

- [x] Define identical coding task and controlled repository state for BENCH-CODE-001 v1.0.
- [x] Execute three BENCH-CODE-001 runs per tested local system; preserve clean PASS/failure outcomes rather than rerunning failed candidates.
- [ ] Compare BENCH-CODE-001 local systems against Claude Code as a hosted system-level baseline.
- [ ] Analyze quality, latency, energy, privacy and cost.
- [x] Compare A001, A002 and A003 before introducing retrieval.
- [ ] Compare Academic Screening LLM-only baselines against retrieval-augmented configurations.
- [ ] Extend the academic corpus with clearly irrelevant papers to improve false-positive evaluation.
- [ ] Evaluate academic RAG retrieval and citation quality.
- [ ] Prepare figures, tables and statistical analysis.
- [ ] Assess publication targets and release reproducibility artifacts where licensing permits.

## Phase 8 — Future Teaching Content Assistant

This is a planned future capability and is intentionally deferred until the Academic stack and the web control plane are stable. The initial assumption is to reuse a validated general instruction model before introducing another model family.

### 8.1 — Source-grounded knowledge layer

- [ ] Reuse the document-ingestion and RAG foundations already validated in the Academic stack.
- [ ] Accept books, articles, technical documents, notes and instructor-provided texts as source material.
- [ ] Preserve source metadata and page/section traceability.
- [ ] Implement structure-aware chunking appropriate for books and teaching material.
- [ ] Retrieve only the evidence required for the requested lesson instead of placing entire books in the LLM context.
- [ ] Require generated teaching content to remain grounded in the supplied sources.

### 8.2 — Teaching planning layer

- [ ] Define a structured request for target audience, learning objectives, lesson duration, technical depth and desired activities.
- [ ] Separate source analysis from pedagogical planning.
- [ ] Generate a lesson outline before generating final artifacts.
- [ ] Support class structure such as concepts, examples, exercises, questions, instructor notes and student material.

### 8.3 — Structured content generation

- [ ] Use Qwen3-30B-A3B-Instruct-2507 initially as the general instruction-model baseline unless benchmark evidence justifies changing models.
- [ ] Define a versioned Teaching Generation prompt/profile independent from Academic Screening prompts.
- [ ] Generate an intermediate structured representation, preferably JSON plus Markdown, before rendering files.
- [ ] Include source references in the intermediate representation so claims can be traced back to books/articles/texts.
- [ ] Keep content generation separate from document rendering.

Planned logical pipeline:

```text
Books / articles / notes / technical texts
  -> extraction and metadata
  -> structure-aware chunks
  -> embeddings / retrieval
  -> grounded evidence set
  -> general instruction LLM
  -> pedagogical plan
  -> structured lesson representation
  -> artifact renderers
       -> Markdown
       -> PDF
       -> PPTX
       -> later additional formats
```

### 8.4 — Artifact rendering

- [ ] Generate Markdown directly from the structured lesson representation.
- [ ] Add deterministic PDF generation from templates rather than asking the LLM to create binary PDF output directly.
- [ ] Add deterministic PPTX generation from structured slide data rather than asking the LLM to create presentations directly.
- [ ] Preserve references, document metadata and generation configuration alongside each artifact.
- [ ] Add reusable visual/document templates only after content correctness is validated.

### 8.5 — Web integration

- [ ] Add a Teaching Content Generator mode to the web control panel after the service manager is stable.
- [ ] Allow source-set selection and generation-profile selection from the interface.
- [ ] Reuse the same large general instruction model initially when practical rather than maintaining an unnecessary dedicated model.
- [ ] Add additional models only when controlled benchmarks show a measurable benefit.
- [ ] Keep the one-large-model-at-a-time policy unless future hardware changes justify a different design.

### 8.6 — Validation and future benchmark

- [ ] Define Teaching Generation v0.1 before comparing models.
- [ ] Measure source fidelity and unsupported-claim/hallucination rate.
- [ ] Measure conceptual coverage against the requested learning objectives.
- [ ] Measure instructor editing effort required before use.
- [ ] Measure generation time, token usage, resource consumption and integrated energy.
- [ ] Evaluate PPTX/PDF/MD artifact correctness separately from pedagogical/content quality.
- [ ] Only after this baseline exists, compare alternative general-purpose LLMs against the existing Qwen3 instruction model.

## Immediate priority order after A003

1. Keep the frozen Academic Screening v0.1 inputs and A001/A003 evidence immutable.
2. Add automatic run telemetry and record the repository commit directly in every future formal run manifest.
3. Build Academic Screening v0.2/hold-out with class-0 and borderline papers.
4. Define structure-aware chunks and retrieval ground truth.
5. Benchmark embedding candidates and run B001 dense retrieval.
6. Add hybrid retrieval, reranking and citation-aware RAG only after retrieval metrics are understood.
7. After the Academic stack reaches a stable checkpoint, implement the web control plane for safe model/service switching.
8. Only after the web control plane is stable, begin Teaching Content Assistant v0.1 as a source-grounded generation pipeline.


## Immediate coding benchmark sequence

1. [x] Preserve BENCH-CODE-001 as the greenfield baseline with three Qwen3-Coder Q3 runs and three Qwen3.6 Q4 runs.
2. [x] Freeze and execute BENCH-CODE-DEV-002 as the existing-code integration benchmark.
3. [x] Add Semantic Audit v2 so generic 404 responses cannot inflate negative-path scoring.
4. [ ] Run Qwen3-30B-A3B-Instruct-2507 Q3_K_M under BENCH-CODE-DEV-002 as a same-scale general-instruction control.
5. [ ] Add a DeepSeek-family local candidate if the installed profile can be frozen under the same protocol.
6. [ ] Compare the strongest local configuration with Claude Code using the same frozen task/seed.
7. [ ] Add integrated energy/resource telemetry without changing the functional benchmark contract.
8. [ ] Preserve every candidate repository, run artifact, evaluator output and telemetry record before interpretation.


## BENCH-CODE-001 formal runs

- [x] C001-A01 — OpenCode 1.18.27 + Qwen3-Coder-30B-A3B-Instruct Q3_K_M, 32768 context: 16/16 total, 14/14 critical, 436 s, 0 human interventions.
- [x] C001-A02 — OpenCode 1.18.27 + Qwen3-Coder-30B-A3B-Instruct Q3_K_M, 32768 context: 16/16 total, 14/14 critical, 567 s, 0 human interventions.
- [x] C001-A03 — OpenCode 1.18.27 + Qwen3-Coder-30B-A3B-Instruct Q3_K_M, 32768 context: 16/16 total, 14/14 critical, 586 s, 0 human interventions.

<!-- BENCH-CODE-DEV-002-ROADMAP -->
## BENCH-CODE-DEV-002 progression

- [x] Freeze existing-code vehicle-management task and seed.
- [x] Validate API, restart and Playwright evaluator layers.
- [x] Run Qwen3-Coder-Next ~80B-A3B Q3_K_M.
- [x] Run Qwen3-Coder-30B-A3B Q3_K_M.
- [x] Run Qwen3-Coder-30B-A3B Q4_K_M and classify its candidate startup failure.
- [x] Run Qwen3.6-35B-A3B Q4_K_M R2 after preserving the first context-overflow attempt.
- [x] Add Semantic Audit v2 and retain official + audited scores side by side.
- [x] Preserve benchmark prompt, v1.8 freeze fingerprints and consolidated result table in Git.
- [ ] Run Qwen3-30B-A3B-Instruct-2507 Q3_K_M as a same-scale general-instruction control.
- [ ] Add DeepSeek-family candidate if the installed local profile can be frozen under the same protocol.
- [ ] Add a hosted-system comparison only after the local comparison matrix is sufficiently controlled.
- [ ] Add integrated energy/resource telemetry to BENCH-CODE-DEV-002 without changing functional scoring.
- [ ] Refine a future evaluator version so negative-path tests are semantically guarded natively; keep the v1.8 evaluator immutable for historical runs.
