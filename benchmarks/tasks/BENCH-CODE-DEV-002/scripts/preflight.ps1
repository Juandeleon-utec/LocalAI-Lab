param()
$ErrorActionPreference="Stop"
$Root=Split-Path -Parent $PSScriptRoot
$Seed=Join-Path $Root "seed.tar"
$ManifestPath=Join-Path $Root "benchmark-manifest.json"
$Prompt=Join-Path $Root "prompt.txt"
$Work=Join-Path $Root "_preflight_seed"
$Out=Join-Path $Root "_preflight_evaluation"

if(!(Test-Path $Seed)){throw "Falta seed.tar"}
if(!(Test-Path $ManifestPath)){throw "Falta benchmark-manifest.json"}
$m=Get-Content $ManifestPath -Raw | ConvertFrom-Json
$seedHash=(Get-FileHash $Seed -Algorithm SHA256).Hash.ToLower()
$promptHash=(Get-FileHash $Prompt -Algorithm SHA256).Hash.ToLower()
if($seedHash -ne $m.seed_sha256){throw "SHA256 del seed no coincide"}
if($promptHash -ne $m.prompt_sha256){throw "SHA256 del prompt no coincide"}
Write-Host "[PASS] Integridad seed/prompt"

Remove-Item $Work,$Out -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force $Work,$Out | Out-Null
tar -xf $Seed -C $Work
if($LASTEXITCODE -ne 0){throw "No se pudo extraer seed"}
Write-Host "[PASS] Seed extraido"

& (Join-Path $PSScriptRoot "evaluate.ps1") -Workspace $Work -OutputDirectory $Out -RunId "PREFLIGHT-SEED"
if(Test-Path (Join-Path $Out "harness-error.json")){
    Get-Content (Join-Path $Out "harness-error.json")
    throw "Preflight fallo por harness/startup"
}
$e=Get-Content (Join-Path $Out "evaluation.json") -Raw | ConvertFrom-Json
$names=@("admin_login","regression_create_transporter","regression_list_transporters","regression_users_list")
foreach($n in $names){
    $x=$e.tests | Where-Object {$_.name -eq $n}
    if(!$x -or !$x.pass){throw "Regression/preflight esperado no paso: $n"}
}
$vehicle=$e.tests | Where-Object {$_.name -eq "vehicle_create"}
if($vehicle.pass){throw "El seed ya implementa la funcionalidad objetivo; benchmark no es valido"}
Write-Host "[PASS] Infraestructura base funciona"
Write-Host "[PASS] Evaluador detecta que el seed NO tiene Vehiculos"
if(Test-Path (Join-Path $Out "e2e.json")){
    Write-Host "[INFO] Playwright ejecutado; es normal que falle sobre el seed sin la funcionalidad."
}else{
    Write-Host "[INFO] E2E no ejecutado. Ejecute setup-evaluator.ps1 para habilitar Playwright."
}
Write-Host ""
Write-Host "PREFLIGHT OK. Todavia NO se ejecuto ningun modelo."
