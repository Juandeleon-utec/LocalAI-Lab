param()
$ErrorActionPreference="Stop"
$Root=Split-Path -Parent $PSScriptRoot
$Eval=Join-Path $Root "evaluator"
Push-Location $Eval
try {
  if(!(Test-Path "package.json")){
@'
{
  "name": "bench-code-dev-002-evaluator",
  "private": true,
  "version": "1.0.0",
  "dependencies": {
    "playwright": "1.55.0"
  }
}
'@ | Set-Content package.json -Encoding utf8
  }
  npm install
  if($LASTEXITCODE -ne 0){throw "npm install evaluator fallo"}
  npx playwright install chromium
  if($LASTEXITCODE -ne 0){throw "playwright install chromium fallo"}
  Write-Host "Playwright evaluator listo."
} finally { Pop-Location }
