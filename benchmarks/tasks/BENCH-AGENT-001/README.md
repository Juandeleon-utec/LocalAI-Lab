# BENCH-AGENT-001 — Agent strategy benchmark

BENCH-AGENT-001 reuses the frozen BENCH-CODE-DEV-002 v1.8 task, seed and final evaluator. It does **not** replace DEV002 and does not rerun baseline A.

The experiment changes only the orchestration around the same coding model/task.

## Minimal experiment matrix

| ID | Model | Strategy | New model runs |
|---|---|---|---:|
| A | Qwen3-Coder-30B Q3 | original one-shot DEV002 baseline | 0 |
| C | Qwen3-Coder-30B Q3 | implement → public verifier → at most one repair | 1 |
| D | Qwen3-Coder-30B Q3 | implement → public verifier → independent critic → at most one repair | 1 |
| E | Qwen3-Coder-Next ~80B Q3 | repeat only the winning C/D strategy | 1 |

Stopping rule: if C reaches 15/15 audited critical requirements, D may be skipped and E should repeat C.

## Design principles

- DEV002 seed/prompt/final evaluator remain frozen.
- Context remains 49,152 for A/C/D/E comparability.
- The public verifier is derived only from the explicit task contract; it never invokes the frozen final evaluator.
- The frozen DEV002 evaluator runs **once**, only after the strategy has finished.
- Strategy C allows at most two LLM calls.
- Strategy D allows at most three LLM calls.
- The critic in D runs in a separate directory containing a generated review bundle, so it cannot modify the candidate repository.
- If the first public verifier passes all critical checks, the strategy exits early and does not spend extra LLM calls.
- Human interventions remain zero during a valid run.
- **No model call is allowed until preflight v1.2 passes.** The preflight performs a full disposable dry-run of the untouched DEV002 seed through Docker, MySQL, npm install, bcrypt, DB migration, backend startup and the public verifier.

## Pipeline C

```text
frozen seed
   ↓
LLM implementer
   ↓
public deterministic verifier
   ├── all critical PASS ───────────────┐
   └── failures → LLM repair (1 max)   │
                    ↓                    │
              public verifier 2         │
                    ↓                    │
                    └────────────────────┘
                              ↓
                    frozen DEV002 evaluator
                              ↓
                       Semantic Audit v2
```

## Pipeline D

```text
frozen seed
   ↓
LLM implementer
   ↓
public deterministic verifier
   ├── all critical PASS ───────────────────────────┐
   └── failures                                     │
          ↓                                         │
     compact review-context.md                      │
          ↓                                         │
     LLM critic in isolated directory               │
          ↓                                         │
     critic-report.md                               │
          ↓                                         │
     LLM repair (1 max)                             │
          ↓                                         │
     public verifier 2                              │
          ↓                                         │
          └─────────────────────────────────────────┘
                              ↓
                    frozen DEV002 evaluator
                              ↓
                       Semantic Audit v2
```

## What the public verifier checks

It is a pre-delivery quality gate, not the hidden/frozen evaluator. It checks explicit requirements that a developer can derive from the task itself:

- required frontend `data-testid` values;
- source-level CRUD route presence;
- vehicle model field presence;
- dependency install, DB migration and backend startup;
- admin authentication requirement;
- admin login and existing transporter/user regressions;
- create/list/get/update/delete vehicle smoke behavior;
- duplicate matrícula and invalid transporter rejection;
- missing-resource 404 behavior.

It intentionally does **not** run Playwright E2E or restart persistence. Those remain final-evaluation evidence and keep the intermediate loop reasonably cheap.


### v1.2 preflight hardening

The v1.2 preflight resolves command shims before launching them. In particular, npm-installed PowerShell wrappers such as `opencode.ps1` are executed through `powershell.exe -NoProfile -ExecutionPolicy Bypass -File` instead of being passed directly to `Start-Process`, which would raise Win32 error `%1 is not a valid Win32 application`. Launcher failures are now recorded as normal preflight failures instead of terminating the script with an uncaught exception.

## Mandatory preflight v1.2

Before any LLM inference, `preflight-agent.ps1` verifies:

- DEV002 and BENCH-AGENT-001 frozen hashes;
- RunId unused;
- PowerShell, Git, tar, Docker, Node, npm, Python and OpenCode;
- Docker daemon running with Linux engine;
- local `mysql:8.4` image present;
- verifier MySQL/backend ports free;
- Python pipeline scripts compile;
- `seed.tar` is readable;
- llama `/health` and `/v1/models`;
- exact `n_ctx=49152` plus expected model parameter count, GGUF size and Q3 ftype;
- exact OpenCode model visibility;
- a **full disposable seed dry-run** through the public verifier, which must reach `stage=complete`;
- cleanup/release of verifier ports after the dry-run.

If any check fails, `run-strategy.ps1` aborts **before creating `runs/<RunId>` and before the first LLM call**.

Manual preflight can be run with:

```powershell
.\benchmarks\tasks\BENCH-AGENT-001\scripts\preflight-agent.ps1 `
  -RunId AG001-C-CODER30-Q3 `
  -Model local/qwen3-coder `
  -ContextTokens 49152 `
  -Dev002Root C:\bench-code-001-formal\BENCH-CODE-DEV-002 `
  -OutputRoot C:\bench-code-001-formal\BENCH-AGENT-001 `
  -LlamaBaseUrl http://192.168.2.237:8080 `
  -LlamaApiKey $env:LLAMA_API_KEY
```

The same preflight runs automatically again at the start of `run-strategy.ps1`.

## Prerequisites

1. Existing frozen DEV002 directory, e.g.:

```text
C:\bench-code-001-formal\BENCH-CODE-DEV-002
```

2. OpenCode configured with the candidate model.
3. Docker available on the Windows benchmark host.
4. `llama-server` started with the frozen benchmark context:

```text
n_ctx = 49152
```

The runner aborts before consuming a RunId if the server reports a different context. This prevents accidentally running C/D against the 112K production profile.

Set the API key in the shell rather than embedding it in scripts:

```powershell
$env:LLAMA_API_KEY = "<your-key>"
```

Before the first C run, freeze the agent pipeline itself. C, D and E must all verify against this same local freeze:

```powershell
.\benchmarks\tasks\BENCH-AGENT-001\scripts\freeze-agent.ps1 `
  -Dev002Root C:\bench-code-001-formal\BENCH-CODE-DEV-002 `
  -OutputRoot C:\bench-code-001-formal\BENCH-AGENT-001
```

This creates `C:\bench-code-001-formal\BENCH-AGENT-001\benchmark-freeze-v1.0.json`. `run-strategy.ps1` refuses to consume a RunId if the pipeline, DEV002 seed/prompt/freeze, or required 49,152-token context no longer matches.

## Reset after an invalid infrastructure-only attempt

If an earlier attempt is deliberately discarded before adopting v1.2, remove only the BENCH-AGENT-001 output root and create a fresh v1.2 freeze:

```powershell
Remove-Item C:\bench-code-001-formal\BENCH-AGENT-001 -Recurse -Force
New-Item C:\bench-code-001-formal\BENCH-AGENT-001 -ItemType Directory -Force | Out-Null
```

Do not alter DEV002.

## Run C

From the LocalAI-Lab repository:

```powershell
cd C:\Users\jpdeleon\github\LocalAI-Lab

.\benchmarks\tasks\BENCH-AGENT-001\scripts\run-strategy.ps1 `
  -Strategy C `
  -RunId AG001-C-CODER30-Q3 `
  -Model local/qwen3-coder `
  -ContextTokens 49152 `
  -Dev002Root C:\bench-code-001-formal\BENCH-CODE-DEV-002 `
  -OutputRoot C:\bench-code-001-formal\BENCH-AGENT-001 `
  -LlamaBaseUrl http://192.168.2.237:8080 `
  -LlamaApiKey $env:LLAMA_API_KEY
```

## Run D

Use a fresh RunId and fresh seed; never continue C's workspace:

```powershell
.\benchmarks\tasks\BENCH-AGENT-001\scripts\run-strategy.ps1 `
  -Strategy D `
  -RunId AG001-D-CODER30-Q3 `
  -Model local/qwen3-coder `
  -ContextTokens 49152 `
  -Dev002Root C:\bench-code-001-formal\BENCH-CODE-DEV-002 `
  -OutputRoot C:\bench-code-001-formal\BENCH-AGENT-001 `
  -LlamaBaseUrl http://192.168.2.237:8080 `
  -LlamaApiKey $env:LLAMA_API_KEY
```

## Run E

Only after selecting C or D. Example if C wins:

```powershell
.\benchmarks\tasks\BENCH-AGENT-001\scripts\run-strategy.ps1 `
  -Strategy C `
  -RunId AG001-E-NEXT80-Q3-C `
  -Model local/qwen3-coder-next-q3 `
  -ContextTokens 49152 `
  -Dev002Root C:\bench-code-001-formal\BENCH-CODE-DEV-002 `
  -OutputRoot C:\bench-code-001-formal\BENCH-AGENT-001 `
  -LlamaBaseUrl http://192.168.2.237:8080 `
  -LlamaApiKey $env:LLAMA_API_KEY
```

## Result layout

```text
C:\bench-code-001-formal\BENCH-AGENT-001\runs\<RunId>\
├── workspace\
├── artifacts\
│   ├── phases\
│   │   ├── 01-implement\
│   │   ├── 02-repair\              # C
│   │   └── 02-critic\ + 03-repair\ # D
│   ├── verifier-1.json
│   ├── verifier-2.json
│   ├── candidate.diff
│   └── pre-run.json / post-run.json
├── critic\                          # D only
│   ├── review-context.md
│   └── critic-report.md
├── evaluation\                      # frozen DEV002 evaluator
├── audit-v2\                        # semantic audit
└── result.json
```

`result.json` reports separate model/pipeline wall times, LLM-call count, aggregate prompt/output tokens, prompt tok/s, generation tok/s, verifier results and final functional results.

## Compare A/C/D/E

```powershell
python .\benchmarks\tasks\BENCH-AGENT-001\scripts\compare_strategies.py `
  --dev002-root C:\bench-code-001-formal\BENCH-CODE-DEV-002 `
  --agent-root C:\bench-code-001-formal\BENCH-AGENT-001 `
  --out C:\bench-code-001-formal\BENCH-AGENT-001\strategy-comparison.csv
```

Primary decision metric: **audited critical completion**. Secondary metrics: restart/E2E, total pipeline wall time, prompt/output tokens and number of LLM calls.
