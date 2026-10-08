param()
$ErrorActionPreference="Stop"
$Root=Split-Path -Parent $PSScriptRoot
$Out=Join-Path $Root "benchmark-freeze-v1.8.json"

$required=@(
    "prompt.txt",
    "seed.tar",
    "evaluator\evaluator.py",
    "evaluator\e2e.js",
    "scripts\prepare-seed.ps1",
    "scripts\preflight.ps1",
    "scripts\setup-evaluator.ps1",
    "scripts\evaluate.ps1",
    "scripts\run-model.ps1",
    "scripts\summarize.py"
)

$files=@()
foreach($rel in $required){
    $p=Join-Path $Root $rel
    if(!(Test-Path $p)){throw "Falta archivo requerido: $rel"}
    $files += [ordered]@{
        path=$rel
        sha256=(Get-FileHash $p -Algorithm SHA256).Hash.ToLower()
        bytes=(Get-Item $p).Length
    }
}

$seedManifest=Join-Path $Root "benchmark-manifest.json"
$seedInfo=$null
if(Test-Path $seedManifest){
    $seedInfo=Get-Content $seedManifest -Raw | ConvertFrom-Json
}

$freeze=[ordered]@{
    benchmark="BENCH-CODE-DEV-002"
    freeze_version="1.8"
    protocol="one-shot-per-model"
    human_interventions_per_run=0
    seed_commit=$seedInfo.seed_commit
    seed_sha256=(Get-FileHash (Join-Path $Root "seed.tar") -Algorithm SHA256).Hash.ToLower()
    prompt_sha256=(Get-FileHash (Join-Path $Root "prompt.txt") -Algorithm SHA256).Hash.ToLower()
    files=$files
    frozen_utc=(Get-Date).ToUniversalTime().ToString("o")
}
$freeze | ConvertTo-Json -Depth 6 | Set-Content $Out -Encoding utf8

Write-Host "BENCHMARK FREEZE OK"
Write-Host "Freeze: $Out"
Write-Host "SHA256: $((Get-FileHash $Out -Algorithm SHA256).Hash.ToLower())"
Write-Host "Seed: $($freeze.seed_sha256)"
Write-Host "Prompt: $($freeze.prompt_sha256)"
