param(
  [Parameter(Mandatory=$true)][string]$RunId,
  [Parameter(Mandatory=$true)][string]$Model,
  [int]$ContextTokens = 32768,
  [string]$LlamaBaseUrl = "http://ia-server:8080",
  [string]$LlamaApiKey = "",
  [string]$OpenCodeExe = "opencode",
  [switch]$SkipEvaluation
)

$ErrorActionPreference="Stop"
$Root=Split-Path -Parent $PSScriptRoot
$Run=Join-Path $Root "runs\$RunId"
$Workspace=Join-Path $Run "workspace"
$Artifacts=Join-Path $Run "artifacts"
$Evaluation=Join-Path $Run "evaluation"

if(Test-Path $Run){
    throw "RunId ya existe. No se permiten reintentos sobre la misma corrida: $RunId"
}

$Seed=Join-Path $Root "seed.tar"
$Prompt=Join-Path $Root "prompt.txt"
$Freeze=Join-Path $Root "benchmark-freeze-v1.8.json"

if(!(Test-Path $Seed)){throw "Falta seed.tar. Ejecute prepare-seed.ps1."}
if(!(Test-Path $Freeze)){throw "Falta benchmark-freeze-v1.8.json. Ejecute freeze-benchmark.ps1 antes de corridas oficiales."}

& (Join-Path $PSScriptRoot "verify-freeze.ps1")
if($LASTEXITCODE -ne 0){throw "Freeze verification fallo"}

function Get-Headers {
    if([string]::IsNullOrWhiteSpace($LlamaApiKey)){
        return @{}
    }
    return @{ Authorization = "Bearer $LlamaApiKey" }
}

function Get-WebContent([string]$Path){
    try {
        return (Invoke-WebRequest `
            -UseBasicParsing `
            -Uri "$LlamaBaseUrl$Path" `
            -Headers (Get-Headers) `
            -TimeoutSec 10 `
            -ErrorAction Stop).Content
    } catch {
        throw "Servidor de modelo no disponible/autorizado en $LlamaBaseUrl$Path : $($_.Exception.Message)"
    }
}

function Try-Web([string]$Path,[string]$Out) {
    try {
        (Invoke-WebRequest `
            -UseBasicParsing `
            -Uri "$LlamaBaseUrl$Path" `
            -Headers (Get-Headers) `
            -TimeoutSec 10 `
            -ErrorAction Stop).Content |
            Set-Content $Out -Encoding utf8
    } catch {
        "UNAVAILABLE: $($_.Exception.Message)" | Set-Content $Out -Encoding utf8
    }
}

function Invoke-GitCapture {
    param(
        [Parameter(Mandatory=$true)][string[]]$Arguments,
        [Parameter(Mandatory=$true)][string]$StdoutPath,
        [Parameter(Mandatory=$true)][string]$StderrPath,
        [Parameter(Mandatory=$true)][string]$WorkingDirectory
    )

    Remove-Item $StdoutPath,$StderrPath -Force -ErrorAction SilentlyContinue

    $p=Start-Process `
        -FilePath "git.exe" `
        -ArgumentList $Arguments `
        -WorkingDirectory $WorkingDirectory `
        -RedirectStandardOutput $StdoutPath `
        -RedirectStandardError $StderrPath `
        -PassThru `
        -Wait `
        -NoNewWindow

    return $p.ExitCode
}

# ============================================================
# PREFLIGHTS QUE NO CONSUMEN RUNID
# ============================================================

$healthBefore=Get-WebContent "/health"
$modelsBefore=Get-WebContent "/v1/models"

$ocCmd=Get-Command $OpenCodeExe -ErrorAction SilentlyContinue
if(!$ocCmd){
    throw "OpenCode no encontrado: $OpenCodeExe"
}

$oldEA=$ErrorActionPreference
$ErrorActionPreference="Continue"
try {
    $ocVersionOutput = (& $OpenCodeExe --version 2>&1 | Out-String).Trim()
    $ocVersionExit=$LASTEXITCODE
} finally {
    $ErrorActionPreference=$oldEA
}
if($ocVersionExit -ne 0){
    throw "OpenCode --version fallo con exit code $ocVersionExit. Salida: $ocVersionOutput"
}
if([string]::IsNullOrWhiteSpace($ocVersionOutput)){
    throw "OpenCode --version no devolvio salida"
}
$opencodeVersion=$ocVersionOutput

$oldEA=$ErrorActionPreference
$ErrorActionPreference="Continue"
try {
    $ocModelsOutput = (& $OpenCodeExe models 2>&1 | Out-String)
    $ocModelsExit=$LASTEXITCODE
} finally {
    $ErrorActionPreference=$oldEA
}
if($ocModelsExit -ne 0){
    throw "OpenCode models fallo con exit code $ocModelsExit"
}
if($ocModelsOutput -notmatch [regex]::Escape($Model)){
    throw "El modelo '$Model' no aparece en 'opencode models'. No se consume RunId."
}

# ============================================================
# RECIEN AHORA SE CREA/CONSUME EL RUNID
# ============================================================

New-Item -ItemType Directory -Force $Workspace,$Artifacts,$Evaluation | Out-Null

$healthBefore | Set-Content (Join-Path $Artifacts "health-before.json") -Encoding utf8
$modelsBefore | Set-Content (Join-Path $Artifacts "models-before.json") -Encoding utf8
$opencodeVersion | Set-Content (Join-Path $Artifacts "opencode-version.txt") -Encoding utf8
$ocModelsOutput | Set-Content (Join-Path $Artifacts "opencode-models.txt") -Encoding utf8
Try-Web "/metrics" (Join-Path $Artifacts "metrics-before.txt")

tar -xf $Seed -C $Workspace
if($LASTEXITCODE -ne 0){throw "No se pudo extraer seed"}

Push-Location $Workspace
try {
    git init -q
    git config user.email "bench@example.invalid"
    git config user.name "BENCH-CODE-DEV-002"
    git add -A
    git commit -q -m "BENCH-CODE-DEV-002 seed"
    if($LASTEXITCODE -ne 0){throw "No se pudo crear commit seed local"}
    $seedCommit=(git rev-parse HEAD).Trim()
} finally {
    Pop-Location
}

$pre=[ordered]@{
    run_id=$RunId
    benchmark="BENCH-CODE-DEV-002"
    benchmark_freeze="v1.8"
    model=$Model
    llama_base_url=$LlamaBaseUrl
    llama_api_key_configured=(![string]::IsNullOrWhiteSpace($LlamaApiKey))
    configured_context_tokens=$ContextTokens
    seed_commit=$seedCommit
    seed_sha256=(Get-FileHash $Seed -Algorithm SHA256).Hash.ToLower()
    prompt_sha256=(Get-FileHash $Prompt -Algorithm SHA256).Hash.ToLower()
    freeze_sha256=(Get-FileHash $Freeze -Algorithm SHA256).Hash.ToLower()
    opencode_version=$opencodeVersion
    opencode_command=$ocCmd.Source
    human_interventions=0
    start_utc=(Get-Date).ToUniversalTime().ToString("o")
}
$pre | ConvertTo-Json | Set-Content (Join-Path $Artifacts "pre-run.json") -Encoding utf8

$promptText=Get-Content -LiteralPath $Prompt -Raw
$events=Join-Path $Artifacts "opencode-events.jsonl"
$stderr=Join-Path $Artifacts "opencode-stderr.txt"

$oldEA=$ErrorActionPreference
$ErrorActionPreference="Continue"
$sw=[System.Diagnostics.Stopwatch]::StartNew()
Push-Location $Workspace
try {
    & $OpenCodeExe run `
        --auto `
        --model $Model `
        --format json `
        --title $RunId `
        --dir $Workspace `
        $promptText `
        1> $events `
        2> $stderr

    $agentExit=$LASTEXITCODE
} finally {
    Pop-Location
    $sw.Stop()
    $ErrorActionPreference=$oldEA
}

Try-Web "/metrics" (Join-Path $Artifacts "metrics-after.txt")
Try-Web "/health" (Join-Path $Artifacts "health-after.json")
Try-Web "/v1/models" (Join-Path $Artifacts "models-after.json")

# ============================================================
# EVIDENCIA GIT
# IMPORTANTE: warnings LF/CRLF van a stderr y NO abortan la corrida.
# ============================================================

$gitEvidence=@(
    @{ args=@("status","--short"); stdout="git-status.txt"; stderr="git-status.stderr.txt"; fatal=$true },
    @{ args=@("diff","--stat"); stdout="git-diff-stat.txt"; stderr="git-diff-stat.stderr.txt"; fatal=$true },
    @{ args=@("diff","--check"); stdout="git-diff-check.txt"; stderr="git-diff-check.stderr.txt"; fatal=$false },
    @{ args=@("diff","--binary"); stdout="candidate.diff"; stderr="candidate-diff.stderr.txt"; fatal=$true },
    @{ args=@("diff","--numstat"); stdout="git-numstat.txt"; stderr="git-numstat.stderr.txt"; fatal=$true },
    @{ args=@("diff","--name-only"); stdout="git-files.txt"; stderr="git-files.stderr.txt"; fatal=$true }
)

$gitCapture=@()
foreach($g in $gitEvidence){
    $exit=Invoke-GitCapture `
        -Arguments $g.args `
        -StdoutPath (Join-Path $Artifacts $g.stdout) `
        -StderrPath (Join-Path $Artifacts $g.stderr) `
        -WorkingDirectory $Workspace

    $gitCapture += [ordered]@{
        command=("git " + ($g.args -join " "))
        exit_code=$exit
        stdout=$g.stdout
        stderr=$g.stderr
    }

    # git diff --check returns nonzero for whitespace errors; that is candidate
    # evidence, not harness failure. Other git collection failures are infra.
    if($g.fatal -and $exit -ne 0){
        throw "Fallo al recolectar evidencia: git $($g.args -join ' ') (exit $exit)"
    }
}

$gitCapture | ConvertTo-Json -Depth 4 |
    Set-Content (Join-Path $Artifacts "git-capture.json") -Encoding utf8

$post=[ordered]@{
    end_utc=(Get-Date).ToUniversalTime().ToString("o")
    agent_wall_seconds=[math]::Round($sw.Elapsed.TotalSeconds,3)
    agent_exit_code=$agentExit
}
$post | ConvertTo-Json | Set-Content (Join-Path $Artifacts "post-run.json") -Encoding utf8

if(!$SkipEvaluation){
    & (Join-Path $PSScriptRoot "evaluate.ps1") `
        -Workspace $Workspace `
        -OutputDirectory $Evaluation `
        -RunId $RunId
}

& python (Join-Path $PSScriptRoot "summarize.py") `
    --run $Run `
    --model $Model `
    --context $ContextTokens

Write-Host ""
Write-Host "===================================================="
Write-Host " BENCH-CODE-DEV-002 RUN COMPLETE"
Write-Host " RunId: $RunId"
Write-Host " Agent exit: $agentExit"
Write-Host " Wall seconds: $([math]::Round($sw.Elapsed.TotalSeconds,3))"
Write-Host " Resultado: $(Join-Path $Run 'result.json')"
Write-Host "===================================================="
