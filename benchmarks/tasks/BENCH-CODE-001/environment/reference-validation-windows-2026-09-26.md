# BENCH-CODE-001 Windows Reference Validation — 2026-09-26

## Host

Engineering-validation workstation:

- OS kernel/build reported by PowerShell: Microsoft Windows NT 10.0.26200.0
- CPU: AMD Ryzen 7 5700G
- RAM: 32 GB
- GPU: NVIDIA GeForce GTX 1050 4 GB
- Docker Desktop backend: WSL2

The GPU is not used by BENCH-CODE-001 candidate applications.

## Toolchain validated

- Git: detected
- Node.js: v24.19.0
- npm: 11.17.0
- Python: 3.11.9 from the LocalAI-Lab virtual environment
- Docker Engine/CLI: 29.8.0, build 88096ef
- Docker Compose: v5.5.1
- MySQL image family: mysql:8.4

## Preflight

`preflight.ps1`: **PASS**

## MySQL clean-lifecycle validation

Two consecutive clean lifecycle cycles were executed from the Windows PowerShell harness.

### Cycle 1

- `start-database.ps1`: PASS
- MySQL container reached Docker health state `healthy`
- host mapping: `3307 -> 3306`
- `stop-database.ps1`: PASS
- container removed
- Compose network removed

### Cycle 2

- `start-database.ps1`: PASS
- MySQL container reached Docker health state `healthy`
- host mapping: `3307 -> 3306`
- `stop-database.ps1`: PASS
- container removed
- Compose network removed

## Interpretation

The Windows staging harness has validated:

- Docker Desktop availability;
- Docker Compose operation;
- MySQL image retrieval/startup;
- health-check behavior;
- clean teardown;
- recreation from a fresh ephemeral database state.

This validates the database lifecycle portion of the benchmark instrument on the Windows workstation.

## Still pending

The benchmark instrument is **not yet fully validated**.

The next gate is the known-good reference candidate:

```text
reference candidate
-> npm install / npm ci
-> npm run db:init
-> npm start
-> /health
-> hidden evaluator pre-restart
-> Node restart without DB reset
-> hidden evaluator post-restart
-> aggregate evaluation
```

Required result before any model run:

- 16 / 16 total tests;
- 14 / 14 critical tests;
- persistence after restart PASS.

Do not execute C001-A01 until this gate passes.
