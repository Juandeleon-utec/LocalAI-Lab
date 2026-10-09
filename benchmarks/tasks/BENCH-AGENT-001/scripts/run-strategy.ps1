param(
  [Parameter(Mandatory=$true)][ValidateSet("C","D")][string]$Strategy,
  [Parameter(Mandatory=$true)][string]$RunId,
  [string]$Model = "local/qwen3-coder",
  [int]$ContextTokens = 49152,
  [long]$ExpectedNParams = 30532122624,
  [long]$ExpectedModelSize = 14705876992,
  [string]$ExpectedFtypePattern = "Q3_K",
  [string]$Dev002Root = "C:\bench-code-001-formal\BENCH-CODE-DEV-002",
  [string]$OutputRoot = "C:\bench-code-001-formal\BENCH-AGENT-001",
  [string]$LlamaBaseUrl = "http://192.168.2.237:8080",
  [string]$LlamaApiKey = "",
  [string]$OpenCodeExe = "opencode",
  [string]$PythonExe = "python.exe",
  [int]$VerifierMySqlPort = 3310,
  [int]$VerifierBackendPort = 3013,
  [switch]$SkipFinalEvaluation
)

$ErrorActionPreference="Stop"
$ScriptRoot=Split-Path -Parent $MyInvocation.MyCommand.Path
$TaskRoot=Split-Path -Parent $ScriptRoot
$AgentFreeze=Join-Path $OutputRoot "benchmark-freeze-v1.2.json"
$VerifyAgentFreeze=Join-Path $ScriptRoot "verify-agent-freeze.ps1"
$Preflight=Join-Path $ScriptRoot "preflight-agent.ps1"
$Run=Join-Path $OutputRoot "runs\$RunId"
$Workspace=Join-Path $Run "workspace"
$Artifacts=Join-Path $Run "artifacts"
$Phases=Join-Path $Artifacts "phases"
$Evaluation=Join-Path $Run "evaluation"
$CriticDir=Join-Path $Run "critic"

$Seed=Join-Path $Dev002Root "seed.tar"
$TaskPrompt=Join-Path $Dev002Root "prompt.txt"
$Freeze=Join-Path $Dev002Root "benchmark-freeze-v1.8.json"
$VerifyFreeze=Join-Path $Dev002Root "scripts\verify-freeze.ps1"
$FinalEvaluator=Join-Path $Dev002Root "scripts\evaluate.ps1"
$SemanticAudit=Join-Path $Dev002Root "audit_v2.py"
$PublicVerifier=Join-Path $ScriptRoot "public_verifier.py"
$BuildReviewContext=Join-Path $ScriptRoot "build_review_context.py"
$Summarize=Join-Path $ScriptRoot "summarize_strategy.py"
$PreflightReport=Join-Path $OutputRoot "preflight\$RunId-preflight.json"

if([string]::IsNullOrWhiteSpace($LlamaApiKey) -and $env:LLAMA_API_KEY){
    $LlamaApiKey=$env:LLAMA_API_KEY
}

function Get-Headers {
    if([string]::IsNullOrWhiteSpace($LlamaApiKey)){ return @{} }
    return @{ Authorization = "Bearer $LlamaApiKey" }
}

function Get-WebContent([string]$Path){
    return (Invoke-WebRequest -UseBasicParsing -Uri "$LlamaBaseUrl$Path" -Headers (Get-Headers) -TimeoutSec 10 -ErrorAction Stop).Content
}

function Try-Web([string]$Path,[string]$Out){
    try {
        Get-WebContent $Path | Set-Content $Out -Encoding utf8
    } catch {
        "UNAVAILABLE: $($_.Exception.Message)" | Set-Content $Out -Encoding utf8
    }
}

function Get-ServerContext([string]$ModelsJson,[string]$WantedModel){
    try {
        $j=$ModelsJson | ConvertFrom-Json
        foreach($m in @($j.data)){
            $ids=@($m.id)+@($m.aliases)
            if(($ids -contains ($WantedModel -replace '^local/','')) -or ($ids -contains $WantedModel)){
                if($m.meta -and $m.meta.n_ctx){ return [int]$m.meta.n_ctx }
            }
        }
        foreach($m in @($j.data)){
            if($m.meta -and $m.meta.n_ctx){ return [int]$m.meta.n_ctx }
        }
    } catch {}
    return $null
}

function Invoke-LoggedProcess {
    param(
        [Parameter(Mandatory=$true)][string]$FilePath,
        [string[]]$ArgumentList=@(),
        [Parameter(Mandatory=$true)][string]$StdoutPath,
        [Parameter(Mandatory=$true)][string]$StderrPath,
        [string]$WorkingDirectory=$null
    )
    Remove-Item $StdoutPath,$StderrPath -Force -ErrorAction SilentlyContinue
    $params=@{
        FilePath=$FilePath; ArgumentList=$ArgumentList;
        RedirectStandardOutput=$StdoutPath; RedirectStandardError=$StderrPath;
        PassThru=$true; Wait=$true; NoNewWindow=$true
    }
    if($WorkingDirectory){$params.WorkingDirectory=$WorkingDirectory}
    $p=Start-Process @params
    return $p.ExitCode
}

function Invoke-AgentPhase {
    param(
      [Parameter(Mandatory=$true)][string]$Name,
      [Parameter(Mandatory=$true)][string]$WorkingDirectory,
      [Parameter(Mandatory=$true)][string]$Prompt
    )
    $Dir=Join-Path $Phases $Name
    New-Item -ItemType Directory -Force $Dir | Out-Null
    Try-Web "/metrics" (Join-Path $Dir "metrics-before.txt")
    $events=Join-Path $Dir "opencode-events.jsonl"
    $stderr=Join-Path $Dir "opencode-stderr.txt"
    $oldEA=$ErrorActionPreference
    $ErrorActionPreference="Continue"
    $sw=[System.Diagnostics.Stopwatch]::StartNew()
    Push-Location $WorkingDirectory
    try {
        & $OpenCodeExe run `
            --auto `
            --model $Model `
            --format json `
            --title "$RunId-$Name" `
            --dir $WorkingDirectory `
            $Prompt `
            1> $events `
            2> $stderr
        $exit=$LASTEXITCODE
    } finally {
        Pop-Location
        $sw.Stop()
        $ErrorActionPreference=$oldEA
    }
    Try-Web "/metrics" (Join-Path $Dir "metrics-after.txt")
    [ordered]@{
        name=$Name
        start_utc=(Get-Date).ToUniversalTime().AddSeconds(-$sw.Elapsed.TotalSeconds).ToString("o")
        end_utc=(Get-Date).ToUniversalTime().ToString("o")
        wall_seconds=[math]::Round($sw.Elapsed.TotalSeconds,3)
        exit_code=$exit
    } | ConvertTo-Json | Set-Content (Join-Path $Dir "phase.json") -Encoding utf8
    return $exit
}

function Invoke-PublicVerifier {
    param([int]$Index)
    $out=Join-Path $Artifacts "verifier-$Index.json"
    $logs=Join-Path $Artifacts "verifier-$Index-logs"
    $stdout=Join-Path $Artifacts "verifier-$Index.stdout.log"
    $stderr=Join-Path $Artifacts "verifier-$Index.stderr.log"
    $exit=Invoke-LoggedProcess `
        -FilePath $PythonExe `
        -ArgumentList @($PublicVerifier,"--workspace",$Workspace,"--out",$out,"--logs",$logs,"--run-id","$RunId-v$Index","--mysql-port","$VerifierMySqlPort","--backend-port","$VerifierBackendPort") `
        -StdoutPath $stdout -StderrPath $stderr -WorkingDirectory $Workspace
    if(!(Test-Path $out)){ throw "El verificador no genero $out (exit $exit)" }
    $report=Get-Content $out -Raw | ConvertFrom-Json
    if($report.status -eq "INFRA_ERROR"){
        throw "Public verifier infrastructure failure at stage '$($report.stage)'. Candidate preserved; do not rerun LLM until verifier is repaired."
    }
    return $report
}

function Get-FailureJson($VerifierReport){
    $compact=[ordered]@{
        status=$VerifierReport.status
        stage=$VerifierReport.stage
        critical_passed=$VerifierReport.critical_passed
        critical_total=$VerifierReport.critical_total
        failures=$VerifierReport.failures
    }
    return ($compact | ConvertTo-Json -Depth 12 -Compress)
}

function Get-LimitedText([string]$Path,[int]$MaxChars=14000){
    if(!(Test-Path $Path)){ return "" }
    $txt=Get-Content $Path -Raw
    if($txt.Length -le $MaxChars){ return $txt }
    return $txt.Substring(0,$MaxChars)+"`n...[truncated]..."
}

# ---------------------------------------------------------------------
# PRE-FLIGHT v1.2: no RunId is consumed and no model inference is allowed
# until the entire disposable seed dry-run reaches verifier stage=complete.
# ---------------------------------------------------------------------
foreach($p in @($Seed,$TaskPrompt,$Freeze,$VerifyFreeze,$FinalEvaluator,$PublicVerifier,$BuildReviewContext,$Summarize,$VerifyAgentFreeze,$AgentFreeze,$Preflight)){
    if(!(Test-Path $p)){ throw "Falta archivo requerido: $p" }
}
if(Test-Path $Run){ throw "RunId ya existe: $RunId" }

Write-Host "`n=== BENCH-AGENT-001 full preflight v1.2 ==="
& $Preflight `
    -RunId $RunId `
    -Model $Model `
    -ContextTokens $ContextTokens `
    -ExpectedNParams $ExpectedNParams `
    -ExpectedModelSize $ExpectedModelSize `
    -ExpectedFtypePattern $ExpectedFtypePattern `
    -Dev002Root $Dev002Root `
    -OutputRoot $OutputRoot `
    -LlamaBaseUrl $LlamaBaseUrl `
    -LlamaApiKey $LlamaApiKey `
    -OpenCodeExe $OpenCodeExe `
    -PythonExe $PythonExe `
    -VerifierMySqlPort $VerifierMySqlPort `
    -VerifierBackendPort $VerifierBackendPort `
    -ReportPath $PreflightReport
if($LASTEXITCODE -ne 0){
    throw "BENCH-AGENT-001 preflight failed. No LLM call was made and RunId was not consumed. Report: $PreflightReport"
}

$health=Get-WebContent "/health"
$models=Get-WebContent "/v1/models"
$serverCtx=Get-ServerContext $models $Model
$oldEA=$ErrorActionPreference; $ErrorActionPreference="Continue"
try {
    $ocModels=(& $OpenCodeExe models 2>&1 | Out-String)
    $ocModelsExit=$LASTEXITCODE
} finally { $ErrorActionPreference=$oldEA }
if($ocModelsExit -ne 0){ throw "opencode models fallo despues de preflight" }

# ---------------------------------------------------------------------
# RUN starts here.
# ---------------------------------------------------------------------
New-Item -ItemType Directory -Force $Workspace,$Artifacts,$Phases,$Evaluation | Out-Null
$pipelineSw=[System.Diagnostics.Stopwatch]::StartNew()
$health | Set-Content (Join-Path $Artifacts "health-before.json") -Encoding utf8
$models | Set-Content (Join-Path $Artifacts "models-before.json") -Encoding utf8
$ocModels | Set-Content (Join-Path $Artifacts "opencode-models.txt") -Encoding utf8
if(Test-Path $PreflightReport){
    Copy-Item $PreflightReport (Join-Path $Artifacts "preflight.json") -Force
}

# Preserve exact task/freeze fingerprints without copying benchmark internals into the candidate.
$pre=[ordered]@{
    benchmark="BENCH-AGENT-001"
    task_benchmark="BENCH-CODE-DEV-002-v1.8"
    run_id=$RunId
    strategy=$Strategy
    model=$Model
    configured_context_tokens=$ContextTokens
    expected_n_params=$ExpectedNParams
    expected_model_size=$ExpectedModelSize
    expected_ftype_pattern=$ExpectedFtypePattern
    server_context_tokens=$serverCtx
    seed_sha256=(Get-FileHash $Seed -Algorithm SHA256).Hash.ToLower()
    task_prompt_sha256=(Get-FileHash $TaskPrompt -Algorithm SHA256).Hash.ToLower()
    dev002_freeze_sha256=(Get-FileHash $Freeze -Algorithm SHA256).Hash.ToLower()
    agent_freeze_sha256=(Get-FileHash $AgentFreeze -Algorithm SHA256).Hash.ToLower()
    preflight_sha256=$(if(Test-Path $PreflightReport){(Get-FileHash $PreflightReport -Algorithm SHA256).Hash.ToLower()}else{$null})
    human_interventions=0
    start_utc=(Get-Date).ToUniversalTime().ToString("o")
}
$pre | ConvertTo-Json | Set-Content (Join-Path $Artifacts "pre-run.json") -Encoding utf8

tar -xf $Seed -C $Workspace
if($LASTEXITCODE -ne 0){ throw "No se pudo extraer DEV002 seed" }
Push-Location $Workspace
try {
    git init -q
    git config user.email "bench-agent@example.invalid"
    git config user.name "BENCH-AGENT-001"
    git add -A
    git commit -q -m "BENCH-AGENT-001 seed"
    if($LASTEXITCODE -ne 0){ throw "No se pudo crear commit seed" }
} finally { Pop-Location }

$task=Get-Content $TaskPrompt -Raw
$implementPrompt=@"
BENCH-AGENT-001 — IMPLEMENTATION PHASE

The task contract below is authoritative and unchanged. Work autonomously in the current repository.

Process discipline:
1. Before editing, inspect the repository architecture and identify the real application entry points, route mounts, model registry and frontend structure.
2. Turn the task into an internal requirement checklist.
3. Implement the complete feature using the existing architecture; avoid unnecessary rewrites.
4. Run reasonable local startup/source/smoke checks available in the repository.
5. Before finishing, review your checklist and the current diff for omissions or disconnected code.
6. Do not ask for human help and do not modify benchmark infrastructure.

TASK CONTRACT
-------------
$task
"@

Write-Host "`n=== Phase 1: implement ($Strategy) ==="
$implExit=Invoke-AgentPhase -Name "01-implement" -WorkingDirectory $Workspace -Prompt $implementPrompt

Write-Host "`n=== Public verifier 1 ==="
$v1=Invoke-PublicVerifier -Index 1
Write-Host "Verifier 1: $($v1.critical_passed)/$($v1.critical_total) critical; status=$($v1.status)"

$needsRepair=($v1.status -ne "PASS")
if($needsRepair){
    if($Strategy -eq "C"){
        $failures=Get-FailureJson $v1
        $fixPrompt=@"
BENCH-AGENT-001 — REPAIR PHASE (Strategy C)

You are working on the same candidate repository after one deterministic pre-delivery verification pass.
The original task contract remains authoritative.

The verifier is NOT the hidden benchmark evaluator. It only checks explicit task requirements and startup/API smoke behavior. Fix the reported failures and any directly related defect you discover. Inspect the current code before editing; make the smallest coherent corrections; do not rewrite unrelated code. Re-run appropriate local checks before finishing.

VERIFIER FAILURES
-----------------
$failures

ORIGINAL TASK CONTRACT
----------------------
$task
"@
        Write-Host "`n=== Phase 2: repair C ==="
        [void](Invoke-AgentPhase -Name "02-repair" -WorkingDirectory $Workspace -Prompt $fixPrompt)
    } else {
        Write-Host "`n=== Build clean critic context ==="
        New-Item -ItemType Directory -Force $CriticDir | Out-Null
        $reviewContext=Join-Path $CriticDir "review-context.md"
        $ctxExit=Invoke-LoggedProcess `
            -FilePath $PythonExe `
            -ArgumentList @($BuildReviewContext,"--workspace",$Workspace,"--task-prompt",$TaskPrompt,"--verifier",(Join-Path $Artifacts "verifier-1.json"),"--out",$reviewContext) `
            -StdoutPath (Join-Path $Artifacts "review-context.stdout.log") `
            -StderrPath (Join-Path $Artifacts "review-context.stderr.log") `
            -WorkingDirectory $Workspace
        if($ctxExit -ne 0){ throw "No se pudo construir critic context" }

        $criticPrompt=@"
BENCH-AGENT-001 — INDEPENDENT CRITIC PHASE (Strategy D)

Read review-context.md in this directory. The candidate repository itself is intentionally not mounted here: you are a reviewer, not an implementer.

Audit the implementation against the task contract and verifier evidence. Look specifically for incomplete requirements, unreachable/disconnected integration, startup/migration risks, model/association mistakes, API semantics, frontend contract gaps, persistence/regression risks, and inconsistencies between backend and frontend.

Do not invent hidden tests. Do not broaden the task. Produce a concise prioritized report with evidence and a minimal correction plan.

Your required deliverable is a file named critic-report.md in this directory. Do not create or edit any other file.
"@
        Write-Host "`n=== Phase 2: independent critic D ==="
        [void](Invoke-AgentPhase -Name "02-critic" -WorkingDirectory $CriticDir -Prompt $criticPrompt)

        $criticReportPath=Join-Path $CriticDir "critic-report.md"
        $criticText=Get-LimitedText $criticReportPath 16000
        if([string]::IsNullOrWhiteSpace($criticText)){
            $criticText=Get-LimitedText (Join-Path $Phases "02-critic\opencode-events.jsonl") 12000
        }
        $failures=Get-FailureJson $v1
        $fixPrompt=@"
BENCH-AGENT-001 — REPAIR PHASE (Strategy D)

You are the final implementer. Work on the current candidate repository.
The original task contract is authoritative. Use both the deterministic verifier failures and the independent critic report as review evidence. Validate every recommendation against the actual code before changing it. Fix the smallest coherent set of defects, avoid unrelated rewrites, and run appropriate local checks before finishing.

DETERMINISTIC VERIFIER FAILURES
-------------------------------
$failures

INDEPENDENT CRITIC REPORT
-------------------------
$criticText

ORIGINAL TASK CONTRACT
----------------------
$task
"@
        Write-Host "`n=== Phase 3: repair D ==="
        [void](Invoke-AgentPhase -Name "03-repair" -WorkingDirectory $Workspace -Prompt $fixPrompt)
    }

    Write-Host "`n=== Public verifier 2 ==="
    $v2=Invoke-PublicVerifier -Index 2
    Write-Host "Verifier 2: $($v2.critical_passed)/$($v2.critical_total) critical; status=$($v2.status)"
} else {
    Write-Host "Verifier 1 passed all critical checks. Early exit: no repair/critic call is needed."
}

# Capture candidate evidence before the official evaluator creates runtime files.
$gitEvidence=@(
    @{args=@("status","--short"); out="git-status.txt"; err="git-status.stderr.txt"; fatal=$true},
    @{args=@("diff","--stat"); out="git-diff-stat.txt"; err="git-diff-stat.stderr.txt"; fatal=$true},
    @{args=@("diff","--check"); out="git-diff-check.txt"; err="git-diff-check.stderr.txt"; fatal=$false},
    @{args=@("diff","--binary"); out="candidate.diff"; err="candidate-diff.stderr.txt"; fatal=$true}
)
foreach($g in $gitEvidence){
    $gx=Invoke-LoggedProcess -FilePath "git.exe" -ArgumentList $g.args -StdoutPath (Join-Path $Artifacts $g.out) -StderrPath (Join-Path $Artifacts $g.err) -WorkingDirectory $Workspace
    if($g.fatal -and $gx -ne 0){ throw "git evidence collection failed: $($g.args -join ' ')" }
}

if(!$SkipFinalEvaluation){
    Write-Host "`n=== Final frozen DEV002 evaluator (one time only) ==="
    & $FinalEvaluator -Workspace $Workspace -OutputDirectory $Evaluation -RunId $RunId
}

$pipelineSw.Stop()
[ordered]@{
    end_utc=(Get-Date).ToUniversalTime().ToString("o")
    pipeline_wall_seconds=[math]::Round($pipelineSw.Elapsed.TotalSeconds,3)
    implementation_exit_code=$implExit
    strategy=$Strategy
} | ConvertTo-Json | Set-Content (Join-Path $Artifacts "post-run.json") -Encoding utf8

& $PythonExe $Summarize --run $Run --model $Model --strategy $Strategy --context $ContextTokens
if($LASTEXITCODE -ne 0){ throw "summarize_strategy.py failed" }

if(!$SkipFinalEvaluation -and (Test-Path $SemanticAudit)){
    Write-Host "`n=== Semantic Audit v2 ==="
    & $PythonExe $SemanticAudit --root $OutputRoot --runs $RunId --out "runs/$RunId/audit-v2"
}

Write-Host ""
Write-Host "===================================================="
Write-Host " BENCH-AGENT-001 COMPLETE"
Write-Host " Strategy : $Strategy"
Write-Host " RunId    : $RunId"
Write-Host " Model    : $Model"
Write-Host " Result   : $(Join-Path $Run 'result.json')"
Write-Host " Audit    : $(Join-Path $Run 'audit-v2')"
Write-Host "===================================================="
