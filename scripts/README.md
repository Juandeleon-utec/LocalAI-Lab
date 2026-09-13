# Scripts

Automation and experiment-support scripts belong here. Scripts used in formal or publication-oriented experiments must be versioned and tied to the corresponding run evidence.

## Academic screening pipeline

Current scripts under `scripts/academic-rag/`:

- `build_pdf_inventory.py` — create deterministic source-PDF inventory and SHA-256 records;
- `extract_pdf_corpus.py` — page-aware PyMuPDF extraction and conservative metadata recovery;
- `normalize_metadata_and_detect_duplicates.py` — normalize metadata, apply manual overrides, calculate normalized-text hashes and detect duplicate candidates;
- `build_screening_dataset.py` — build the frozen READY-paper screening dataset and manifest;
- `run_screening_baseline.py` — execute one-paper-at-a-time OpenAI-compatible LLM screening and preserve raw/structured outputs;
- `evaluate_screening_run.py` — join predictions to frozen ground truth and calculate multiclass, ordinal, binary-screening and reading-workload metrics;
- `evaluate_reading_policy_a002.py` — apply deterministic relevance-to-reading policy without rerunning the LLM.

Formal A001 and A003 outputs are preserved under `results/academic-screening/`.

## Reproducibility requirements for future scripts

New formal-run utilities should, where applicable, record:

- repository commit;
- model artifact filename and SHA-256;
- dataset and ground-truth checksums;
- prompt checksum;
- engine/runtime versions;
- generation parameters;
- raw responses;
- wall time and token usage;
- failure records;
- hardware/resource telemetry.

## Planned utilities

Still planned:

- automatic environment snapshot;
- model launcher/profile switching;
- GPU/CPU/RAM telemetry capture;
- integrated-energy calculation;
- retrieval benchmark execution;
- result aggregation and plotting;
- reproducibility verification/checksum validation.

## Parser-version caution

The Academic Screening v0.1 dataset is already frozen. Changes to extraction or normalization code must not silently redefine A001/A003 inputs. Parser improvements should be versioned and applied to a new dataset build or explicitly documented reprocessing stage.

Known cleanup items are documented in `docs/academic-rag/reproducibility-record-2026-09-13.md`.
