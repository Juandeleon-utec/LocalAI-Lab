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

1. Close the frozen-input reproducibility gaps identified in `docs/academic-rag/reproducibility-record-2026-09-13.md`.
2. Add model hashing, environment capture and run telemetry before the next publication-oriented experiment.
3. Build Academic Screening v0.2/hold-out with class-0 and borderline papers.
4. Define structure-aware chunks and retrieval ground truth.
5. Benchmark embedding candidates and run B001 dense retrieval.
6. Add hybrid retrieval, reranking and citation-aware RAG only after retrieval metrics are understood.
7. After the Academic stack reaches a stable checkpoint, implement the web control plane for safe model/service switching.
8. Only after the web control plane is stable, begin Teaching Content Assistant v0.1 as a source-grounded generation pipeline.
