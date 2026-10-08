param(
  [Parameter(Mandatory=$true)][string]$SourceRepo,
  [string]$Commit = "d429be34cab51ae58b5237ef6e0c296e2c5b67f0"
)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Seed = Join-Path $Root "seed.tar"
Push-Location $SourceRepo
try {
  git cat-file -e "$Commit^{commit}"
  if ($LASTEXITCODE -ne 0) { throw "Commit no encontrado: $Commit" }
  git archive --format=tar --output="$Seed" $Commit
  if ($LASTEXITCODE -ne 0) { throw "git archive fallo" }
} finally { Pop-Location }
$hash=(Get-FileHash $Seed -Algorithm SHA256).Hash.ToLower()
$hash | Set-Content (Join-Path $Root "seed.sha256") -Encoding ascii
$promptHash=(Get-FileHash (Join-Path $Root "prompt.txt") -Algorithm SHA256).Hash.ToLower()
$manifest=[ordered]@{
  benchmark="BENCH-CODE-DEV-002"; version="1.0"
  source_repo=$SourceRepo; seed_commit=$Commit
  seed_sha256=$hash; prompt_sha256=$promptHash
  created_utc=(Get-Date).ToUniversalTime().ToString("o")
}
$manifest | ConvertTo-Json | Set-Content (Join-Path $Root "benchmark-manifest.json") -Encoding utf8
Write-Host "Seed OK: $Seed"
Write-Host "SHA256: $hash"
