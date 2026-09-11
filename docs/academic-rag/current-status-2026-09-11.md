# Academic RAG current status — 2026-09-11

This document captures the validated state of LocalAI-Lab after the first academic-screening pipeline was assembled and tested.

## Server platform

- Host: `ia-server`
- CPU: Intel Core i5-14600KF
- RAM: 64 GB
- GPU: AMD Radeon RX 9060 XT 16 GB (`gfx1200`)
- OS: Ubuntu Server 24.04.4 LTS
- Kernel: `7.0.0-30-generic`
- ROCm: 10.0 / HIP 7.15.26333
- GPU nodes validated: `/dev/kfd`, `/dev/dri/renderD128`
- `llama.cpp`: tag `b10752`, commit `b96806d96061049a5b574269b049bf6241d63d46`
- Serving: `llama-server`, OpenAI-compatible API over LAN
- Operating rule: one large GPU model at a time

Persistent storage:

```text
/srv/models  -> model artifacts
/srv/data    -> datasets, papers, Qdrant, benchmarks, backups
```

## Coding stack

Validated coding model:

- Qwen3-Coder-30B-A3B-Instruct Q3_K_M
- Model path: `/srv/models/coding/qwen3-coder-30b-a3b/`
- OpenCode 1.18.27 runs on the Windows workstation and connects over the LAN.

Formal B002 measurements:

- PP512: ~1923.8 tok/s
- TG128: ~69.1 tok/s
- VRAM: ~14.4–14.7 GB
- GPU power: ~133–138 W

This model is retained for coding-agent workloads. It is not the preferred academic-screening model.

## Academic model

Selected initial academic model:

- `Qwen3-30B-A3B-Instruct-2507`
- Quantization: `Q3_K_M`
- GGUF: `Qwen_Qwen3-30B-A3B-Instruct-2507-Q3_K_M.gguf`
- Directory: `/srv/models/academic/qwen3-30b-a3b-instruct-2507/`
- Planned alias: `qwen3-academic`
- Initial context: 8192 tokens

Rationale: the general/instruction model is a better fit for literature screening than the code-specialized Qwen3-Coder model. Q3_K_M fits the 16 GB GPU with runtime/KV-cache margin.

A previous one-paper screening run with Qwen3-Coder is classified only as a pipeline smoke test, not a formal academic result.

## Academic corpus pipeline

Current deterministic pipeline:

```text
PDF corpus
  -> inventory + SHA-256
  -> page-aware extraction
  -> metadata normalization
  -> duplicate detection + manual overrides
  -> frozen screening dataset
  -> ground truth
  -> LLM-only baseline
  -> later retrieval / reranking / RAG
```

Repository scripts:

- `scripts/academic-rag/build_pdf_inventory.py`
- `scripts/academic-rag/extract_pdf_corpus.py`
- `scripts/academic-rag/normalize_metadata_and_detect_duplicates.py`
- `scripts/academic-rag/build_screening_dataset.py`
- `scripts/academic-rag/run_screening_baseline.py`

Versioned prompt:

- `prompts/academic-screening-v0.1.txt`

## Corpus validation

Latest extraction:

- PDFs: 25
- extraction OK: 25
- empty text: 0
- errors: 0
- pages: 274
- characters: 1,158,398
- wall time: ~1.184 s

The abstract extractor was improved to recognize spaced headers such as `A B S T R A C T`. This recovered P011, P012, P015, and P021.

Duplicate handling:

- P023 and P024 have identical normalized extracted text.
- P024 is excluded by manual override.
- P023 is retained as the canonical copy.
- The duplicate relation remains in audit output without blocking P023.

Latest normalized state:

- documents: 25
- READY: 24
- metadata review: 0
- possible duplicate documents: 0
- excluded: 1
- duplicate candidate pairs: 1

## Frozen screening dataset

Generated paths:

```text
/srv/data/benchmarks/academic-rag/datasets/academic-screening-v0.1/papers-v0.1.csv
/srv/data/benchmarks/academic-rag/datasets/academic-screening-v0.1/manifest-v0.1.json
/srv/data/benchmarks/academic-rag/ground-truth/academic-screening-v0.1/ground-truth-v0.1.csv
```

Dataset builder result:

- source documents: 25
- READY included: 24
- skipped: 1
- missing keywords: 17
- missing DOI: 1
- missing authors: 17

Missing authors/keywords are not blockers for the first baseline because title and abstract coverage is complete.

## Ground truth

Current ground truth: 24 evaluated papers.

Relevance distribution:

- class 0 / NOT_RELEVANT: 0
- class 1 / TANGENTIAL: 5
- class 2 / RELEVANT: 11
- class 3 / HIGHLY_RELEVANT: 8

Reading-decision distribution:

- REFERENCE_ONLY: 5
- READ_SECTIONS: 11
- READ_FULL: 8

The current ground truth is human-supervised and AI-assisted. For publication-quality work, a later independent human-only review should be considered to quantify or reduce labeling bias.

The current corpus is highly enriched for relevant papers: 19/24 are class >= 2. A future benchmark extension should deliberately add clearly irrelevant documents to improve false-positive and discard-precision evaluation.

## Baseline A001

`run_screening_baseline.py` implements the first LLM-only screening baseline.

Input per paper:

- title
- abstract
- keywords
- bibliographic metadata

No RAG, embeddings, reranking, OCR, or external APIs are used.

The runner records:

- structured JSON prediction
- validation errors
- latency per paper
- prompt/completion tokens when returned by the endpoint
- raw API response
- dataset and prompt SHA-256
- run manifest

Validated smoke test with Qwen3-Coder:

- P001: OK
- latency: 4.311 s
- successful: 1
- invalid: 0
- errors: 0

This validates the runner only. The formal A001 run must use `qwen3-academic`.

Primary metrics planned:

- accuracy
- macro F1
- precision/recall by class
- confusion matrix
- recall for relevant papers (`class >= 2`)
- recall for class 3
- false-negative rate
- potential human-reading reduction
- wall time, tokens, VRAM, GPU power, and later integrated energy

High recall of relevant literature is a primary design objective. A target such as recall >= 0.95 is a benchmark goal to test, not a claimed result.

## Planned RAG progression

Controlled experimental progression:

```text
A — title/abstract/keywords -> LLM
B — dense retrieval -> LLM
C — hybrid dense+sparse retrieval -> LLM
D — hybrid retrieval -> reranker -> LLM
E — full citation-aware RAG
```

Current architecture direction:

- document framework: LlamaIndex preferred
- vector database: Qdrant
- retrieval: hybrid dense + sparse
- fusion: RRF initially
- embeddings: benchmark Qwen3-Embedding, BGE-M3, and modern E5 candidates
- reranking: benchmark Qwen3-Reranker candidates
- chunking: structure-aware
- citations: file/page/section/chunk traceability

Retrieval will be evaluated separately using Hit Rate@K, Precision@K, Recall@K, MRR, and nDCG.

## Operational UI direction

A lightweight control panel is planned after core academic validation:

- Coding Agent
- Academic Reviewer
- Image Generator
- Document Generator
- STOP ALL

Initial implementation direction: FastAPI + HTML/JS, profile-driven subprocess management, and exactly one large GPU model active at a time. The Linux backend starts/stops model services only; OpenCode remains on Windows.

## Immediate next steps

1. Finish validating `Qwen3-30B-A3B-Instruct-2507-Q3_K_M` on the RX 9060 XT.
2. Start `llama-server` with alias `qwen3-academic` and context 8192.
3. Run A001 with `--limit 1`, then `--limit 3`, then all 24 papers.
4. Compare predictions with `ground-truth-v0.1.csv`.
5. Add automatic metric calculation and confusion-matrix output.
6. Add GPU telemetry and integrated-energy capture to formal runs.
7. Begin embedding/retrieval experiments only after the LLM-only baseline is stable.

## Cleanup items

- Replace deprecated `import fitz` with `import pymupdf` in the extractor.
- Remove remaining invalid escape warnings in DOI-cleaning strings where present.
- Keep service startup manual until benchmark behavior is fully validated; systemd/autostart is intentionally deferred.
