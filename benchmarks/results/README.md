# Benchmark Results

Benchmark outputs should be append-only whenever practical. Do not overwrite historical runs after analysis.

Recommended structure:

```text
benchmarks/results/
├── raw/
├── processed/
├── figures/
└── tables/
```

Each run should have a unique identifier linking the raw measurement, environment metadata, task definition and analysis output.

Large raw datasets and model artifacts should not be committed directly to Git unless intentionally managed with an appropriate large-file/data strategy.

## Current direct model benchmarks

- `LAILAB-B001-qwen3-8b-q4km-rx9060xt.md`
- `LAILAB-B002-qwen3-coder-30b-a3b-q3km-rx9060xt.md`
- `LAILAB-B003-qwen3-coder-q3-vs-q4-rx9060xt.md` — paired Q3_K_M vs Q4_K_M throughput comparison.
