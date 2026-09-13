# Benchmark Methodology

## Objective

LocalAI-Lab benchmarks prioritize reproducibility, traceability and controlled comparison over anecdotal impressions.

A benchmark result is not considered fully reproducible merely because its final metric table is documented. The provenance chain from exact input and configuration to raw output and derived metric must be preserved.

## Coding-agent comparison

A future controlled benchmark may compare Claude Code, OpenCode + local coding model, Qwen Code + local coding model, Aider + local model, and additional systems added later.

## Experimental control

Each system should receive, as far as technically possible:

- the same repository;
- the same initial commit;
- the same task description;
- the same test suite;
- the same execution environment;
- the same time/resource limits.

Any unavoidable difference must be documented before interpreting results.

## Core coding metrics

- task success;
- tests passed;
- compile/build success;
- time to completion;
- number of agent iterations;
- number of tool calls;
- input/output tokens where measurable;
- files and lines changed;
- human intervention required;
- failure mode.

## Infrastructure metrics

- mean and peak VRAM usage;
- mean and peak RAM usage;
- GPU utilization;
- CPU utilization;
- prompt-processing speed;
- generation speed;
- total task duration;
- sampled power draw where available;
- integrated energy per task where available.

Energy claims should use time-integrated energy rather than treating a peak or single power sample as energy consumption.

## Academic screening metrics

For literature screening, report both ordinal classification quality and operational screening quality.

Ordinal/classification metrics:

- exact class accuracy;
- per-class precision, recall and F1;
- macro F1;
- confusion matrix;
- mean absolute class error;
- weighted kappa.

Binary screening metrics at the predefined relevance threshold:

- true positives;
- false positives;
- false negatives;
- true negatives;
- relevant-paper precision;
- relevant-paper recall;
- false-negative rate.

Reading-workload metrics:

- number/fraction selected for active reading;
- potential active-reading reduction;
- relevant-paper retention;
- class-3 READ_FULL recall where applicable.

Ordinal calibration and reading-effort reduction must not be conflated. A prompt can improve four-class agreement while leaving the binary screening set unchanged, as observed in A003.

## Retrieval/RAG metrics

Retrieval should be evaluated separately from generation whenever ground truth permits.

Planned retrieval metrics:

- Hit Rate@K;
- Precision@K;
- Recall@K;
- MRR;
- nDCG.

Generation/citation metrics may include:

- citation correctness;
- evidence traceability;
- factual consistency;
- source attribution;
- hallucination rate;
- answer completeness;
- scientific-writing quality.

## Reproducibility record

Every formal run should record or immutably reference:

- date and run identifier;
- LocalAI-Lab repository commit used for execution;
- task/dataset version;
- exact dataset checksum;
- exact ground-truth artifact and checksum when evaluation uses labels;
- prompt identifier and checksum;
- model identifier, filename, quantization and SHA-256;
- inference-engine repository revision/build;
- ROCm/driver/kernel/OS versions;
- Python version and dependency snapshot;
- server launch arguments;
- context length;
- temperature, seed and token limits;
- warm-up policy;
- number of repetitions;
- raw model responses;
- parsed predictions;
- derived evaluation artifacts;
- failure logs;
- resource telemetry when hardware/energy claims are made.

## Formal-run artifact contract

For Academic Screening, the current minimal Git-preserved run directory contains:

```text
manifest.json
responses.jsonl
predictions.csv
comparison.csv
evaluation.json
evaluation.md
```

`responses.jsonl` is the raw model-output evidence. `evaluation.json` is the machine-readable source for reported metrics. `manifest.json` binds the run to prompt/dataset fingerprints and generation parameters.

The canonical preserved A001/A003 run artifacts are under `results/academic-screening/`.

Large evidence packages may be stored outside normal Git, but must be checksummed and referenced. Small textual artifacts should remain in Git whenever practical.

## Dataset and prompt immutability

A named benchmark version should not be silently modified after formal evaluation. Changes to dataset membership, labels, prompts or parsing rules require a new version or an explicitly documented calibration experiment.

When a prompt is changed after inspecting errors from a benchmark, the resulting experiment is a development-set calibration result. It must be validated on independent or expanded hold-out material before being treated as evidence of generalization.

## Failure handling

Infrastructure failures must be retained as operational evidence but excluded from scientific comparisons unless failure rate itself is an outcome.

Examples include model-server unavailability, request failures before inference, corrupt files, or execution interruptions.

Smoke tests validate the pipeline only. They must not be merged into formal benchmark statistics.

## Publication-quality experiments

Before a formal comparison begins, freeze a protocol defining:

- research question and hypotheses;
- primary metrics;
- task/data inclusion and exclusion criteria;
- relevance threshold where applicable;
- repetition count;
- failure treatment;
- ground-truth provenance;
- statistical analysis;
- artifact-retention policy.

Do not change primary evaluation criteria after seeing final results without documenting the change as exploratory analysis.

The current Academic Screening v0.1 corpus is a development/engineering benchmark with no class-0 ground-truth papers and human-supervised/AI-assisted labels. Publication-level screening claims require a more representative hold-out set and explicit reporting of this provenance.
