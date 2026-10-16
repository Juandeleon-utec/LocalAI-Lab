# GEMMA4-LAB-001 — Operational index and handoff (2026-10-16)

**Purpose:** one-stop index to resume all four Gemma 4 / BENCH-CODE-001 configurations without rereading chat history. This is a *path and configuration inventory*, not a bundle of local files. Paths marked **observed** were confirmed by terminal output; those marked **reported** derive from prior laboratory notes and should be verified when resuming. Do not infer that local files were copied to GitHub.

**Related experiment record:** [GEMMA4-LAB-001-2026-10-16.md](./GEMMA4-LAB-001-2026-10-16.md). **Historical Qwen reference:** [C001-A-SUMMARY.md](./C001-A-SUMMARY.md).

## 1. Root map

| Role | Path / reference | Status |
|---|---|---|
| GitHub | `https://github.com/Juandeleon-utec/LocalAI-Lab` | verified remote; branch `main` |
| Windows local Git clone | `C:\Users\jpdeleon\github\LocalAI-Lab` | reported |
| Windows formal experiment root | `C:\bench-code-001-formal` | observed |
| Frozen repo (never edit) | `C:\bench-code-001-formal\LocalAI-Lab-freeze` | observed |
| Frozen prompt | `...\LocalAI-Lab-freeze\benchmarks\tasks\BENCH-CODE-001\prompt.md` | observed / hash checked |
| Original seed tar | `C:\bench-code-001-formal\BENCH-CODE-001-seed-v1.0.tar` | observed / hash checked |
| Windows Gemma launch/config bundle | `C:\bench-code-001-formal\GEMMA4-C001-FORMAL-v1\windows` | observed |
| Windows generated candidate runs | `C:\bench-code-001-formal\GEMMA4-C001-RUNS` | observed |
| Isolated OpenCode | `C:\bench-code-001-formal\opencode-bench-1.18.27\node_modules\.bin\opencode.cmd` | observed version 1.18.27 |
| Hidden evaluator (keep private) | `C:\bench-code-001-private\bench_code_001_hidden_evaluator_v1.0\evaluator.py` | observed Test-Path True; do **not** copy into Git or workspace |
| Original evaluation scripts | `C:\bench-code-001-formal\LocalAI-Lab-freeze\benchmarks\tasks\BENCH-CODE-001\environment` | observed |
| Linux Gemma lab root | `/srv/data/benchmarks/GEMMA4-LAB-001` | reported |
| Linux Gemma profile entrypoint | `/srv/data/benchmarks/GEMMA4-LAB-001/serve_gemma.sh` | reported / used |
| Dedicated Gemma llama.cpp source | `/home/jpdeleon/llama.cpp-gemma4-lab` | reported |
| Dedicated llama-server | `/home/jpdeleon/llama.cpp-gemma4-lab/build-rocm/bin/llama-server` | reported |
| GGUF directory | `/srv/models/coding/gemma-4-26b-a4b` | reported |
| Server endpoint (LAN) | `http://192.168.2.237:8088` | observed health/model checks; NOT localhost on Windows |
| Qwen original service | `llama-qwen3-coder.service` on Linux port 8080 | reported; preserve existing systemd/OliveTin |
| Earlier Qwen formal run folders | `C:\bench-code-001-formal\C001-A01`, `C001-A02`, `C001-A03` | observed |

Linux host: Ubuntu 24.04.4; GPU AMD Radeon RX 9060 XT (16 GB); ROCm 10.0, llama.cpp gfx1200, source commit `2851b3bcbf8d993a2243ae751c0a7dfa8e944a40` (reported). OpenCode's Gemma service and the preserved Qwen service must not compete for VRAM.

## 2. Files per experiment

All four profiles use the same task, same seed, same candidate-copy-and-evaluate procedure, and context `32768`. The specific Windows files are *expected paths from the generated Gemma bundle*; Q3 launcher existence/use was directly observed; IQ4 paths should be confirmed before first run.

| Profile ID | GGUF basename in `/srv/models/coding/gemma-4-26b-a4b/` | Linux command | Windows launcher | OpenCode model |
|---|---|---|---|---|
| `C001-GEMMA-Q3_OFF` | `gemma-4-26B-A4B-it-UD-Q3_K_M.gguf` | `./serve_gemma.sh q3_off` | `launch-q3_off.ps1` | `local/gemma4-q3_off` |
| `C001-GEMMA-Q3_ON` | `gemma-4-26B-A4B-it-UD-Q3_K_M.gguf` | `./serve_gemma.sh q3_on` | `launch-q3_on.ps1` | `local/gemma4-q3_on` |
| `C001-GEMMA-IQ4_OFF` | `gemma-4-26B-A4B-it-UD-IQ4_XS.gguf` | `./serve_gemma.sh iq4_off` | `launch-iq4_off.ps1` | `local/gemma4-iq4_off` |
| `C001-GEMMA-IQ4_ON` | `gemma-4-26B-A4B-it-UD-IQ4_XS.gguf` | `./serve_gemma.sh iq4_on` | `launch-iq4_on.ps1` | `local/gemma4-iq4_on` |

In Windows bundle, profile OpenCode configuration files were installed alongside launchers; **exact config filenames are not independently verified**. Inspect each launcher for its `$ConfigPath` and `$VerifyFreeze` before executing; do not infer a filename. Each launcher checks the config SHA256 and endpoint model in preflight.

Shared Windows files:

- `GEMMA4-C001-FORMAL-v1\windows\verify-freeze-gemma.ps1`: adapted **copy** of frozen verifier; Windows check set to `10.0.26300`, and frozen task directory path corrected. Original `...\environment\verify-freeze.ps1` is untouched.
- `GEMMA4-C001-FORMAL-v1\windows\launch-q3_off.ps1` and `launch-q3_on.ps1`: patched locally to reference `verify-freeze-gemma.ps1`; the four launchers also received a PATH prefix targeting isolated OpenCode 1.18.27.
- `GEMMA4-C001-FORMAL-v1\windows\launch-iq4_off.ps1` and `launch-iq4_on.ps1`: isolated OpenCode PATH prefix added; check/patch verifier path before starting; original frozen script will reject newer Windows.
- `*.ps1.bak`: local backups may exist; inspect rather than overwrite.
- Linux `serve_gemma.sh`: local custom script; full file contents have **not** been committed to GitHub.

Original frozen evaluation/control scripts (Git-tracked in `benchmarks/tasks/BENCH-CODE-001/environment/`):

`docker-compose.yml`, `start-database.ps1`, `stop-database.ps1`, `run-candidate.ps1`, `verify-freeze.ps1`, `aggregate-evaluation.py`, `capture-environment.ps1`, `preflight.ps1`, `wait-health.ps1`, `windows-common.ps1`. These are historical baseline references; **do not modify the frozen clone**.

Frozen SHA256: prompt `e1ec6e63a2a603a4d5591158a262d66de1f838a93e72d03ae2a158827e35dbac`; seed `a1d24686ddf69b8d5eb69b956b1500fafa92aac8658270deff33ba3e2c1eadc7`; repo commit `23bed848a1467225a0858dbdb27e57ef2e9aa474`. Observed config hashes: Q3 OFF `7618e912f554504158548632dc4c786a31ad3b9259c832b338d149eda382c3e1`; Q3 ON `d961e23b8aa5464b58ed8f1eb954ae4947c412fcee26b65327f952f084d5972b`.

## 3. Experimental run locations, distinct attempts, and statuses

| Run | Candidate location | Evidence / state | Time and interpretation |
|---|---|---|---|
| Q3 OFF attempt 1 | Prior `GEMMA4-C001-RUNS\C001-GEMMA-Q3_OFF` run; launch preservation message gave `C:\bench-code-001-formal\C001-GEMMA-Q3_OFF-preexisting-20261016T035932Z` | Previous run preserved by launcher; verify actual artifacts location | 337 s; `exit=0`; unscored |
| Q3 OFF attempt 2 | `GEMMA4-C001-RUNS\C001-GEMMA-Q3_OFF\workspace` | `artifacts\`, `evaluation-workspace-clean\`, `evaluation\` | 205 s; `exit=0`; db-init hanging on open pool, evaluator blocked and unscored |
| Q3 ON | `GEMMA4-C001-RUNS\C001-GEMMA-Q3_ON\workspace` | `artifacts\`, `evaluation-workspace-clean\`, `evaluation\` | 377 s; `exit=1`; original hidden evaluator 16/16, critical 14/14 PASS |
| IQ4 OFF | `GEMMA4-C001-RUNS\C001-GEMMA-IQ4_OFF\workspace` (expected) | Not generated yet | Pending |
| IQ4 ON | `GEMMA4-C001-RUNS\C001-GEMMA-IQ4_ON\workspace` (expected) | Not generated yet | Pending |

**Important scoring discipline:** Q3 ON functional PASS despite OpenCode exit code 1, recorded as separate dimensions; Q3 OFF did *not* run tests, so is not a numeric 0/16 outcome. Baseline Qwen A01/A02/A03 each got 16/16, 14/14 critical (436, 567, 586 s respectively; mean 529.7 s). Generated candidates must never be patched in place.

## 4. Restart playbook — Linux first, then Windows

### Linux

```bash
# Inspect existing inference processes and memory BEFORE launching a new mode.
systemctl status llama-qwen3-coder.service --no-pager
ps -ww -eo pid,args | grep '[l]lama-server'
ss -ltnp | grep -E ':8080|:8088'

# Do not kill an unrelated process. Stop the active Gemma instance gracefully
# in its serving terminal (Ctrl+C), confirm 8088 released, then:
cd /srv/data/benchmarks/GEMMA4-LAB-001
./serve_gemma.sh iq4_off    # or q3_off, q3_on, iq4_on

# From a second terminal (LAN-bound endpoint):
curl -sS http://192.168.2.237:8088/health
curl -sS http://192.168.2.237:8088/v1/models
```

The profile must match OpenCode's model ID and reasoning flag. Keep the original Qwen systemd configuration untouched; when RAM/VRAM is tight, stop it rather than removing/reconfiguring it. For VRAM and exact context inspect the actual llama-server arguments with `ps -ww -p $(pgrep -n llama-server) -o args=`.

### Windows — preflight and generation

```powershell
$base = 'C:\bench-code-001-formal'
$win  = Join-Path $base 'GEMMA4-C001-FORMAL-v1\windows'
$profile = 'iq4_off' # change to q3_off/q3_on/iq4_on
$launcher = Join-Path $win "launch-$profile.ps1"

# Inspect original references; IQ4 verifier may still point to frozen OS verifier.
Select-String $launcher -Pattern 'VerifyFreeze|ConfigPath|GEMMA_OPENCODE_BIN'
& (Join-Path $base 'opencode-bench-1.18.27\node_modules\.bin\opencode.cmd') --version
curl.exe -sS http://192.168.2.237:8088/health
if (-not (Test-Path $launcher)) { throw "Missing launcher: $launcher" }
# Only execute after verifying the verifier path and server model.
& $launcher
```

If updating an IQ4 launcher's `$VerifyFreeze` reference: back up the file; change only the string pointing to `...\environment\verify-freeze.ps1` into `Join-Path $PSScriptRoot "verify-freeze-gemma.ps1"`. Never change the frozen verifier, task prompt, seed, or generated candidate.

### Windows — evaluation

```powershell
$base = 'C:\bench-code-001-formal'
$run = Join-Path $base 'GEMMA4-C001-RUNS\C001-GEMMA-Q3_ON'  # adjust selected completed run
$source = Join-Path $run 'workspace'
$dest = Join-Path $run 'evaluation-workspace-clean'
$env:BENCH_EVALUATOR = 'C:\bench-code-001-private\bench_code_001_hidden_evaluator_v1.0\evaluator.py'
if (-not (Test-Path $env:BENCH_EVALUATOR)) { throw 'Hidden evaluator unavailable' }
if (Test-Path $dest) { throw 'Destination already exists; do not overwrite a scored candidate' }
New-Item -ItemType Directory -Path $dest | Out-Null
robocopy $source $dest /E /XD node_modules .git /XF .env | Out-Null
if ($LASTEXITCODE -ge 8) { throw "Workspace copy failed: $LASTEXITCODE" }

$environment = Join-Path $base 'LocalAI-Lab-freeze\benchmarks\tasks\BENCH-CODE-001\environment'
& (Join-Path $environment 'run-candidate.ps1') -CandidateDirectory $dest -OutputDirectory (Join-Path $run 'evaluation')
```

The original `run-candidate.ps1` resets the MySQL Compose service, sets the host port to 3307 and executes original evaluator phase `pre-restart` then `post-restart`. Evaluator file SHA256 from prior terminal check: `0098e69f2f1d8e18e56b4de1b8132f3baa08eaaf2151c0f06ddf8bf296693903`. Confirm hash whenever auditability matters.

**Blocker warning:** A candidate `npm run db:init` may hang indefinitely when `mysql2` pool is not closed. A message “schema initialized” does not prove process exit. Inspect separate terminal for `node src/db/init.js` and port 3000. Do not patch candidate; record the blocker and stop only benchmark-owned processes if required.

## 5. Full machine inventory: commands to discover actual configs and artifacts

Use these **read-only** inventory commands when resuming, because this index cannot introspect the Windows PC or Linux server.

```powershell
$base = 'C:\bench-code-001-formal'
$win  = Join-Path $base 'GEMMA4-C001-FORMAL-v1\windows'
Get-ChildItem $win -File | Select-Object Name,Length,LastWriteTime
Get-ChildItem (Join-Path $base 'GEMMA4-C001-RUNS') -Directory |
  Select-Object Name,FullName
Get-ChildItem (Join-Path $base 'GEMMA4-C001-RUNS') -Recurse -File |
  Where-Object { $_.FullName -notmatch 'node_modules|\.git' -and $_.Name -match 'json|log|ps1|md' } |
  Select-Object -ExpandProperty FullName
```

```bash
ls -lah /srv/data/benchmarks/GEMMA4-LAB-001
ls -lah /srv/models/coding/gemma-4-26b-a4b
sha256sum /srv/models/coding/gemma-4-26b-a4b/*.gguf
ps -ww -eo pid,args | grep '[l]lama-server'
```

For completeness, the previous Qwen coding policy was identified as `QWEN-CODING-POLICY-V1` and later v1.2, and `AGENTS.md` was used in other local coding sessions. **Do not automatically add these agent policies to BENCH-CODE-001**: frozen benchmark configuration/prompt must remain the experimental source of truth.

## 6. Checklist for next session

- [x] Qwen historical frozen results preserved (3 × 16/16).
- [x] Gemma Q3 OFF recorded (two unscored attempts, detailed blocker).
- [x] Gemma Q3 ON evaluated with original evaluator (16/16; exit=1 discrepancy recorded).
- [ ] Verify exact IQ4 launchers' `$VerifyFreeze` and `$ConfigPath`.
- [ ] Run and evaluate IQ4 OFF.
- [ ] Run and evaluate IQ4 ON.
- [ ] Compute local candidate/log/model SHA256 and persist an immutable per-attempt manifest.
- [ ] After IQ4, optionally run repeated successful profiles for uncertainty estimates and production context 48K/64K as a separate protocol (not comparable to 32K baseline).
