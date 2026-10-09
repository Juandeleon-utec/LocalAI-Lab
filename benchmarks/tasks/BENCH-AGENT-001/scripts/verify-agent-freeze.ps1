param(
  [string]$Dev002Root = "C:\bench-code-001-formal\BENCH-CODE-DEV-002",
  [string]$OutputRoot = "C:\bench-code-001-formal\BENCH-AGENT-001"
)
$ErrorActionPreference="Stop"
$ScriptRoot=Split-Path -Parent $MyInvocation.MyCommand.Path
$TaskRoot=Split-Path -Parent $ScriptRoot
$Freeze=Join-Path $OutputRoot "benchmark-freeze-v1.2.json"
if(!(Test-Path $Freeze)){Write-Error "Missing agent freeze: $Freeze. Run freeze-agent.ps1 after installing v1.2.";exit 2}
$f=Get-Content $Freeze -Raw | ConvertFrom-Json
$bad=@()
if([string]$f.freeze_version -ne "1.2"){$bad += "freeze_version"}
if([string]$f.preflight_version -ne "1.2"){$bad += "preflight_version"}
foreach($x in $f.files){
  $p=Join-Path $TaskRoot $x.path
  if(!(Test-Path $p)){$bad += "MISSING $($x.path)";continue}
  $h=(Get-FileHash $p -Algorithm SHA256).Hash.ToLower()
  if($h -ne $x.sha256){$bad += "HASH $($x.path)"}
}
$devFreeze=Join-Path $Dev002Root "benchmark-freeze-v1.8.json"
$seed=Join-Path $Dev002Root "seed.tar"
$prompt=Join-Path $Dev002Root "prompt.txt"
if(!(Test-Path $devFreeze) -or (Get-FileHash $devFreeze -Algorithm SHA256).Hash.ToLower() -ne $f.dev002_freeze_sha256){$bad += "DEV002 freeze"}
if(!(Test-Path $seed) -or (Get-FileHash $seed -Algorithm SHA256).Hash.ToLower() -ne $f.seed_sha256){$bad += "DEV002 seed"}
if(!(Test-Path $prompt) -or (Get-FileHash $prompt -Algorithm SHA256).Hash.ToLower() -ne $f.task_prompt_sha256){$bad += "DEV002 prompt"}
if([int]$f.context_tokens -ne 49152){$bad += "context_tokens"}
if($f.preflight_full_seed_dry_run -ne $true){$bad += "preflight_full_seed_dry_run"}
if($bad.Count){
  Write-Host "BENCH-AGENT-001 FREEZE VERIFICATION v1.2 FAIL"
  $bad | ForEach-Object {Write-Host " - $_"}
  exit 1
}
Write-Host "BENCH-AGENT-001 FREEZE VERIFICATION v1.2 PASS"
exit 0
