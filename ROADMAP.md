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
- [x] Reclassify the 8K coding-agent work as pilot evidence after context pressure/compaction was observed.
- [x] Define 32K as the nominal local context budget for formal BENCH-CODE-001 comparisons.
- [x] Measure prompt and generation throughput.
- [x] Measure RAM/VRAM behavior for the selected coder model.
- [x] Evaluate OpenCode for repository reading and controlled writes.
- [ ] Evaluate Qwen Code.
- [ ] Evaluate Aider.
- [x] Validate initial local coding-agent workflow over LAN.
- [x] Define BENCH-CODE-001 v1.0: authenticated Node.js/MySQL web-application task.
- [x] Freeze participant prompt, execution protocol, evaluator contract and blinded-review rubric before formal runs.
- [ ] Implement and checksum the external hidden evaluator for BENCH-CODE-001.
- [ ] Prepare the isolated benchmark/staging server and clean MySQL-per-run reset procedure.
- [ ] Validate autonomous edit-test-fix loop under BENCH-CODE-001.
- [ ] Run Qwen3-Coder-30B-A3B-Instruct Q3_K_M at 32K.
- [ ] Integrate and benchmark Qwen3.6-35B-A3B Q4_K_M at 32K.
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

## Phase 5 — Service deployment and web control plane

This phase starts only after the current Academic Screening/RAG validation work reaches a stable checkpoint. The first goal is operational control of model services, not new end-user functionality.

- [x] Expose OpenAI-compatible API on the LAN for manual validation.
- [ ] Define service profiles for each operational mode.
- [ ] Create systemd services or equivalent controlled service wrappers.
- [ ] Implement safe start/stop/switch logic for large GPU models.
- [ ] Enforce the operating rule of one large GPU model loaded at a time.
- [ ] Add health checks and readiness state for each model backend.
- [ ] Add structured logging for service transitions and failures.
- [ ] Add resource telemetry to the service layer.
- [ ] Replace development API key with managed secret/configuration.
- [ ] Build lightweight FastAPI/HTML web control panel.
- [ ] Expose model/service states in the web interface: STOPPED, STARTING, READY, STOPPING, ERROR.
- [ ] Add initial web actions for Coding Agent and Academic Reviewer profiles.
- [ ] Add a global STOP ALL action and verify VRAM release before a new large model starts.
- [ ] Keep OpenCode on the Windows workstation; the web panel controls Linux model backends only.

Planned control flow:

```text
Browser
  -> Web control panel
  -> Mode / service manager
  -> stop currently active large model
  -> verify process termination and VRAM release
  -> start selected model profile
  -> health check
  -> READY
```

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
- [ ] Execute three clean runs per local system for the BENCH-CODE-001 engineering phase.
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

1. Freeze and checksum BENCH-CODE-001 v1.0 inputs before the first formal run.
2. Build the external hidden evaluator and staging-server reset procedure.
3. Run OpenCode + Qwen3-Coder-30B-A3B-Instruct Q3_K_M at 32K as the local baseline.
4. Add Qwen3.6-35B-A3B Q4_K_M without MTP and repeat the identical benchmark.
5. Compare the best local configuration with Claude Code using the same prompt and seed repository.
6. Evaluate Qwen3.6 + MTP separately for end-to-end throughput, latency and energy.
7. Preserve every candidate repository, run manifest, hidden-test output and telemetry artifact before interpretation.
