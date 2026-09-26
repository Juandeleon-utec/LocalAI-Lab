# BENCH-CODE-001 v1.0 — Staging Validation Procedure

Use this procedure before the first Qwen or Claude candidate run.

## 1. Choose one physical staging host

Use the same host for every candidate in the comparison.

The current Ryzen 7 5700G / 32 GB development workstation is technically sufficient for Node.js/MySQL validation, but it is optional. If it is selected, keep its runtime configuration fixed for all candidates.

## 2. Required software

The selected host must provide:

- Git;
- Node.js 24 LTS family;
- npm;
- Docker with Compose;
- curl;
- Bash-compatible shell for the current public harness.

On a Windows staging host, run the harness from a consistent Linux-compatible environment such as WSL2, or use a separate Linux staging host. Do not mix Windows-native and Linux executions inside the same formal comparison.

## 3. Clone and freeze

```bash
git clone https://github.com/Juandeleon-utec/LocalAI-Lab.git
cd LocalAI-Lab
git rev-parse HEAD
```

Record that commit in the run manifest.

## 4. Capture environment

```bash
cd benchmarks/tasks/BENCH-CODE-001/environment
chmod +x *.sh
./capture-environment.sh environment-snapshot.txt
```

Record the generated SHA-256.

## 5. Validate clean MySQL lifecycle

```bash
./start-database.sh
docker compose ps
./stop-database.sh
./start-database.sh
docker compose ps
```

Both starts must reach the healthy state.

## 6. Hidden evaluator

Place the frozen evaluator outside the participant workspace.

Example:

```text
/opt/bench-code-001-hidden/evaluator.py
```

Record the evaluator archive SHA-256 in the run manifest.

Do not copy the evaluator into a candidate repository.

## 7. Reference-validation run

Before evaluating an AI-generated candidate, use a known-good reference implementation that follows the same public prompt contract.

Run:

```bash
export BENCH_EVALUATOR=/opt/bench-code-001-hidden/evaluator.py

./run-candidate.sh \
  /path/to/reference-candidate \
  /path/to/results/reference-validation
```

The purpose of this run is to validate the benchmark harness, not to create a comparison result.

Check:

- MySQL starts from an empty state;
- `npm ci` or `npm install` succeeds;
- `npm run db:init` succeeds;
- `npm start` succeeds;
- `/health` becomes ready;
- pre-restart evaluator output is created;
- the application is restarted without resetting MySQL;
- post-restart persistence output is created;
- application and MySQL logs are preserved.

## 8. Freeze before formal runs

After the reference-validation run passes:

- pin exact Node.js version;
- pin exact MySQL image digest;
- record Docker/Compose version;
- record staging-host OS/kernel;
- preserve environment snapshot hash;
- preserve prompt hash;
- preserve hidden evaluator hash;
- preserve the LocalAI-Lab commit.

Do not change these inputs between Qwen3-Coder, Qwen3.6 and Claude Code runs.

## 9. Formal sequence

Only after the harness has passed reference validation:

1. C001-A01/A02/A03 — OpenCode + Qwen3-Coder, 32K;
2. C001-B01/B02/B03 — OpenCode + Qwen3.6, 32K;
3. C001-C01/C02/C03 — Claude Code;
4. C001-D — Qwen3.6 + MTP efficiency experiment.

Each run starts from a clean candidate workspace and a fresh MySQL instance.
