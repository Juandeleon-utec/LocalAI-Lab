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

## 4. Preflight and capture environment

```bash
cd benchmarks/tasks/BENCH-CODE-001/environment
chmod +x *.sh
./preflight.sh
```

The preflight must report `PASS` before continuing.

The candidate runner captures the environment automatically after the MySQL image is available. For a manual snapshot:

```bash
./start-database.sh
./capture-environment.sh environment-snapshot.txt
./stop-database.sh
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

## 6. Hidden evaluator and validation reference

Place both frozen validation artifacts outside the participant workspace.

Recommended layout:

```text
/opt/bench-code-001-hidden/
├── evaluator.py
└── reference-candidate/
```

Current engineering-validation fingerprints:

```text
hidden evaluator ZIP
SHA-256: edb663ba732cd54ad3ce6cae34e73d1a351ed8afe4bcf58209dd60e46aede670

reference candidate ZIP
SHA-256: 452d8deae6fa04b83b1356850db265105e5fa5ee94bfa4471deff5dc93d3d5cf
```

The reference implementation exists only to validate the harness. It is not ground truth and must never be provided to evaluated agents.

Record the evaluator archive SHA-256 in every formal run manifest.

Do not copy either artifact into a participant repository.

## 7. Reference-validation run

Before evaluating an AI-generated candidate, use a known-good reference implementation that follows the same public prompt contract.

Run:

```bash
export BENCH_EVALUATOR=/opt/bench-code-001-hidden/evaluator.py

./run-candidate.sh \
  /opt/bench-code-001-hidden/reference-candidate \
  /path/to/results/reference-validation
```

The runner must produce at least:

```text
run-info.txt
environment-snapshot.txt
environment-sha256.txt
npm-install.log
db-init.log
app.log
mysql.log
evaluator-pre.json
evaluator-post.json
evaluator-state.json
evaluation.json
```

For the known-good reference candidate, the expected functional result is:

```text
tests_passed: 16
tests_total: 16
critical_tests_passed: 14
critical_tests_total: 14
all_tests_passed: true
all_critical_tests_passed: true
```

If the reference candidate does not reach that result, do not run model comparisons yet. Diagnose the harness/evaluator/reference interaction first.

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


## 10. Engineering validation vs formal staging

The Ryzen 7 5700G / 32 GB workstation may be used immediately for engineering validation under WSL2/Linux-compatible Docker.

That does **not** automatically freeze it as the formal staging host.

If a different dedicated staging server is selected later, repeat Sections 4–8 on that server and freeze the new environment before C001-A01. Formal Qwen/Claude results must all use the same final staging environment.
