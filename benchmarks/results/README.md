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
