# Benchmark Methodology

## Objective

LocalAI-Lab benchmarks should prioritize reproducibility over anecdotal impressions.

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
- power draw where available;
- energy per task where available.

## Academic/RAG metrics

- retrieval precision;
- retrieval recall where ground truth exists;
- reranking gain;
- citation correctness;
- factual consistency;
- source attribution;
- hallucination rate;
- answer completeness;
- scientific-writing quality.

## Reproducibility record

Each benchmark result should include:

- date and run identifier;
- repository commit;
- task/dataset version;
- model identifier and artifact hash where possible;
- quantization;
- inference-engine version;
- ROCm/driver/kernel/OS versions;
- context length;
- generation parameters;
- warm-up policy;
- number of repetitions;
- raw measurements and derived metrics.

## Publication-quality experiments

Before a formal comparison begins, freeze a protocol that defines task inclusion criteria, primary metrics, repetition count, treatment of failures and statistical analysis. Do not change the primary evaluation criteria after seeing the final results without documenting the change as exploratory analysis.
