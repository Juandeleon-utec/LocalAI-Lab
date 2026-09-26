# BENCH-CODE-001 v1.0 — Staging Validation Procedure

Use this procedure before the first Qwen or Claude candidate run.

## 1. Current engineering-validation host

The current Windows workstation is suitable for engineering validation:

- CPU: AMD Ryzen 7 5700G
- RAM: 32 GB
- GPU: NVIDIA GeForce GTX 1050 4 GB
- OS: Windows

The GPU is not used by BENCH-CODE-001 candidate applications.

This machine may later become the formal staging host, but that decision is made only after reference validation succeeds.

## 2. Required Windows software

Install and keep available:

- Git for Windows;
- Node.js 24 LTS family;
- npm;
- Python 3;
- Docker Desktop with Docker Compose;
- Windows PowerShell 5.1 or PowerShell 7.

Docker Desktop must be running before the validation begins.

No WSL, Bash or `chmod` command is required for the Windows-native harness.

## 3. Update LocalAI-Lab

From PowerShell:

```powershell
cd C:\path\to\LocalAI-Lab
git pull
git rev-parse HEAD
```

Record the commit shown by `git rev-parse HEAD`.

## 4. PowerShell execution policy for the current terminal

If Windows blocks local `.ps1` execution, use a process-local policy only:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

This affects only the current PowerShell process.

## 5. Preflight

```powershell
cd .\benchmarks\tasks\BENCH-CODE-001\environment
.\preflight.ps1
```

The last line must be:

```text
Preflight PASS
```

The preflight reports the exact Windows, Node.js, npm, Python, Docker and Docker Compose versions.

## 6. Validate clean MySQL lifecycle

Run:

```powershell
.\start-database.ps1
docker compose ps
.\stop-database.ps1

.\start-database.ps1
docker compose ps
.\stop-database.ps1
```

Both starts must reach the Docker health state `healthy`.

The MySQL data directory is ephemeral, so a new benchmark run starts from an empty database.

## 7. Hidden evaluator and reference candidate

Keep both artifacts outside the LocalAI-Lab repository and outside every candidate workspace.

A convenient Windows layout is:

```text
C:\bench-code-001-private\
├── hidden-evaluator\
│   └── evaluator.py
└── reference-candidate\
    ├── package.json
    ├── src\
    ├── public\
    └── ...
```

Engineering-validation fingerprints:

```text
hidden evaluator ZIP
SHA-256: edb663ba732cd54ad3ce6cae34e73d1a351ed8afe4bcf58209dd60e46aede670

reference candidate ZIP
SHA-256: 452d8deae6fa04b83b1356850db265105e5fa5ee94bfa4471deff5dc93d3d5cf
```

The reference candidate validates the benchmark instrument only. It is not ground truth and must never be supplied to an evaluated agent.

## 8. Reference-validation run on Windows

Set the evaluator path:

```powershell
$env:BENCH_EVALUATOR = "C:\bench-code-001-private\hidden-evaluator\evaluator.py"
```

Create a results directory outside the candidate:

```powershell
New-Item -ItemType Directory -Force C:\bench-code-001-results | Out-Null
```

Run the known-good reference:

```powershell
.\run-candidate.ps1 `
  -CandidateDirectory "C:\bench-code-001-private\reference-candidate" `
  -OutputDirectory "C:\bench-code-001-results\reference-validation"
```

The runner automatically performs:

```text
fresh MySQL
-> npm ci / npm install
-> npm run db:init
-> npm start
-> GET /health
-> hidden evaluator pre-restart
-> stop Node
-> restart Node without resetting MySQL
-> hidden evaluator post-restart
-> evaluation.json
-> logs + environment snapshot
```

## 9. Expected reference result

Open:

```powershell
Get-Content C:\bench-code-001-results\reference-validation\evaluation.json
```

Expected summary:

```json
{
  "tests_passed": 16,
  "tests_total": 16,
  "critical_tests_passed": 14,
  "critical_tests_total": 14,
  "all_tests_passed": true,
  "all_critical_tests_passed": true
}
```

If the reference candidate does not reach this result, do not execute Qwen or Claude yet.

## 10. Expected retained artifacts

The result directory should include at least:

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

## 11. Freeze before formal runs

Only after the reference candidate reaches 16/16 and 14/14:

- decide whether this Windows workstation is the formal staging host;
- record the exact Windows build;
- pin the exact Node.js version;
- pin the exact MySQL image digest;
- record Docker Desktop and Docker Compose versions;
- preserve the environment snapshot;
- preserve the prompt hash;
- preserve the hidden evaluator hash;
- preserve the LocalAI-Lab commit.

If another machine is chosen for formal staging, repeat this complete validation on that machine.

Do not change the selected staging environment between Qwen3-Coder, Qwen3.6 and Claude Code runs.

## 12. Formal sequence

After the staging environment is frozen:

1. C001-A01/A02/A03 — OpenCode + Qwen3-Coder, 32K;
2. C001-B01/B02/B03 — OpenCode + Qwen3.6, 32K;
3. C001-C01/C02/C03 — Claude Code;
4. C001-D — Qwen3.6 + MTP efficiency experiment.

Each run starts from a clean candidate workspace and a fresh MySQL instance.

## Linux alternative

The existing Bash helpers remain available for a future Linux staging host. Do not mix Windows-native and Linux staging results inside the same formal comparison.
