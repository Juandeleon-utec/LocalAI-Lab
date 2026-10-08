param()
$ErrorActionPreference="Stop"
$Root=Split-Path -Parent $PSScriptRoot
$FreezePath=Join-Path $Root "benchmark-freeze-v1.8.json"

if(!(Test-Path $FreezePath)){
    Write-Error "Falta benchmark-freeze-v1.8.json"
    exit 2
}

$f=Get-Content $FreezePath -Raw | ConvertFrom-Json
$bad=@()

foreach($x in $f.files){
    $p=Join-Path $Root $x.path
    if(!(Test-Path $p)){
        $bad += "MISSING $($x.path)"
        continue
    }
    $h=(Get-FileHash $p -Algorithm SHA256).Hash.ToLower()
    if($h -ne $x.sha256){
        $bad += "HASH $($x.path)"
    }
}

$seedHash=(Get-FileHash (Join-Path $Root "seed.tar") -Algorithm SHA256).Hash.ToLower()
$promptHash=(Get-FileHash (Join-Path $Root "prompt.txt") -Algorithm SHA256).Hash.ToLower()

if($seedHash -ne $f.seed_sha256){$bad += "HASH seed.tar"}
if($promptHash -ne $f.prompt_sha256){$bad += "HASH prompt.txt"}

if($bad.Count -gt 0){
    Write-Host "FREEZE VERIFICATION FAIL"
    $bad | ForEach-Object {Write-Host " - $_"}
    exit 1
}

Write-Host "FREEZE VERIFICATION PASS"
exit 0
