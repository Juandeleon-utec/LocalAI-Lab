param(
  [string]$Dev002Root = "C:\bench-code-001-formal\BENCH-CODE-DEV-002",
  [string]$OutputRoot = "C:\bench-code-001-formal\BENCH-AGENT-001"
)
$ErrorActionPreference="Stop"
$ScriptRoot=Split-Path -Parent $MyInvocation.MyCommand.Path
$TaskRoot=Split-Path -Parent $ScriptRoot
$Out=Join-Path $OutputRoot "benchmark-freeze-v1.2.json"
$DevFreeze=Join-Path $Dev002Root "benchmark-freeze-v1.8.json"
$Seed=Join-Path $Dev002Root "seed.tar"
$Prompt=Join-Path $Dev002Root "prompt.txt"
foreach($p in @($DevFreeze,$Seed,$Prompt)){ if(!(Test-Path $p)){throw "Missing: $p"} }
$required=@(
  "README.md",
  "scripts\run-strategy.ps1",
  "scripts\preflight-agent.ps1",
  "scripts\public_verifier.py",
  "scripts\build_review_context.py",
  "scripts\summarize_strategy.py",
  "scripts\compare_strategies.py",
  "scripts\freeze-agent.ps1",
  "scripts\verify-agent-freeze.ps1"
)
$files=@()
foreach($rel in $required){
  $p=Join-Path $TaskRoot $rel
  if(!(Test-Path $p)){throw "Missing pipeline file: $rel"}
  $files += [ordered]@{path=$rel;sha256=(Get-FileHash $p -Algorithm SHA256).Hash.ToLower();bytes=(Get-Item $p).Length}
}
New-Item -ItemType Directory -Force $OutputRoot | Out-Null
$f=[ordered]@{
  benchmark="BENCH-AGENT-001"
  freeze_version="1.2"
  task_benchmark="BENCH-CODE-DEV-002-v1.8"
  context_tokens=49152
  strategy_c_max_llm_calls=2
  strategy_d_max_llm_calls=3
  preflight_version="1.2"
  preflight_requires_docker_linux=$true
  preflight_requires_mysql_image="mysql:8.4"
  preflight_full_seed_dry_run=$true
  preflight_dry_run_must_reach_stage="complete"
  dev002_freeze_sha256=(Get-FileHash $DevFreeze -Algorithm SHA256).Hash.ToLower()
  seed_sha256=(Get-FileHash $Seed -Algorithm SHA256).Hash.ToLower()
  task_prompt_sha256=(Get-FileHash $Prompt -Algorithm SHA256).Hash.ToLower()
  files=$files
  frozen_utc=(Get-Date).ToUniversalTime().ToString("o")
}
$f | ConvertTo-Json -Depth 6 | Set-Content $Out -Encoding utf8
Write-Host "BENCH-AGENT-001 FREEZE v1.2 OK"
Write-Host "Freeze: $Out"
Write-Host "SHA256: $((Get-FileHash $Out -Algorithm SHA256).Hash.ToLower())"
