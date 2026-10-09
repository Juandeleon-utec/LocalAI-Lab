param(
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
  [string]$ReportPath = ""
)

$ErrorActionPreference = "Stop"
$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$TaskRoot = Split-Path -Parent $ScriptRoot

$Seed = Join-Path $Dev002Root "seed.tar"
$TaskPrompt = Join-Path $Dev002Root "prompt.txt"
$DevFreeze = Join-Path $Dev002Root "benchmark-freeze-v1.8.json"
$VerifyDevFreeze = Join-Path $Dev002Root "scripts\verify-freeze.ps1"
$AgentFreeze = Join-Path $OutputRoot "benchmark-freeze-v1.2.json"
$VerifyAgentFreeze = Join-Path $ScriptRoot "verify-agent-freeze.ps1"
$PublicVerifier = Join-Path $ScriptRoot "public_verifier.py"
$BuildReviewContext = Join-Path $ScriptRoot "build_review_context.py"
$Summarize = Join-Path $ScriptRoot "summarize_strategy.py"
$Compare = Join-Path $ScriptRoot "compare_strategies.py"
$RunPath = Join-Path $OutputRoot "runs\$RunId"

if([string]::IsNullOrWhiteSpace($LlamaApiKey) -and $env:LLAMA_API_KEY){
  $LlamaApiKey = $env:LLAMA_API_KEY
}

if([string]::IsNullOrWhiteSpace($ReportPath)){
  $PreflightDir = Join-Path $OutputRoot "preflight"
  $ReportPath = Join-Path $PreflightDir "$RunId-preflight.json"
}
$ReportDir = Split-Path -Parent $ReportPath
New-Item -ItemType Directory -Force $ReportDir | Out-Null

$Checks = New-Object System.Collections.ArrayList
$Started = (Get-Date).ToUniversalTime()
$TempRoot = $null

function Add-Check {
  param(
    [Parameter(Mandatory=$true)][string]$Id,
    [Parameter(Mandatory=$true)][bool]$Pass,
    [string]$Detail = "",
    [string]$Remediation = ""
  )
  [void]$Checks.Add([ordered]@{
    id = $Id
    pass = $Pass
    detail = $Detail
    remediation = $Remediation
  })
  if($Pass){
    Write-Host ("[PASS] {0} - {1}" -f $Id,$Detail) -ForegroundColor Green
  } else {
    Write-Host ("[FAIL] {0} - {1}" -f $Id,$Detail) -ForegroundColor Red
    if($Remediation){ Write-Host ("       {0}" -f $Remediation) -ForegroundColor Yellow }
  }
}

function Test-LocalPortFree {
  param([int]$Port)
  $listener = $null
  try {
    $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback,$Port)
    $listener.Start()
    return $true
  } catch {
    return $false
  } finally {
    if($listener){ try { $listener.Stop() } catch {} }
  }
}

function Invoke-NativeCapture {
  param(
    [Parameter(Mandatory=$true)][string]$FilePath,
    [string[]]$ArgumentList = @(),
    [string]$WorkingDirectory = $null
  )

  # Start-Process cannot directly execute PowerShell shim files such as
  # npm-installed opencode.ps1 (Win32 error %1). Resolve the command first
  # and, for .ps1 shims, launch it explicitly through powershell.exe.
  $resolved = Get-Command $FilePath -ErrorAction SilentlyContinue
  $resolvedPath = if($resolved -and $resolved.Source){ [string]$resolved.Source } else { $FilePath }
  $launchFile = $resolvedPath
  $launchArgs = @($ArgumentList)

  if([System.IO.Path]::GetExtension($resolvedPath).ToLowerInvariant() -eq ".ps1"){
    $launchFile = (Get-Command "powershell.exe" -ErrorAction Stop).Source
    $launchArgs = @("-NoProfile","-ExecutionPolicy","Bypass","-File",$resolvedPath) + @($ArgumentList)
  }

  $tmpOut = [System.IO.Path]::GetTempFileName()
  $tmpErr = [System.IO.Path]::GetTempFileName()
  try {
    $p = @{
      FilePath = $launchFile
      ArgumentList = $launchArgs
      RedirectStandardOutput = $tmpOut
      RedirectStandardError = $tmpErr
      PassThru = $true
      Wait = $true
      NoNewWindow = $true
    }
    if($WorkingDirectory){ $p.WorkingDirectory = $WorkingDirectory }

    try {
      $proc = Start-Process @p
      return [pscustomobject]@{
        ExitCode = $proc.ExitCode
        Stdout = (Get-Content $tmpOut -Raw -ErrorAction SilentlyContinue)
        Stderr = (Get-Content $tmpErr -Raw -ErrorAction SilentlyContinue)
        ResolvedPath = $resolvedPath
        LaunchFile = $launchFile
      }
    } catch {
      return [pscustomobject]@{
        ExitCode = 9009
        Stdout = (Get-Content $tmpOut -Raw -ErrorAction SilentlyContinue)
        Stderr = ("launcher failure for '{0}' via '{1}': {2}" -f $resolvedPath,$launchFile,$_.Exception.Message)
        ResolvedPath = $resolvedPath
        LaunchFile = $launchFile
      }
    }
  } finally {
    Remove-Item $tmpOut,$tmpErr -Force -ErrorAction SilentlyContinue
  }
}

function Get-Headers {
  if([string]::IsNullOrWhiteSpace($LlamaApiKey)){ return @{} }
  return @{ Authorization = "Bearer $LlamaApiKey" }
}

function Write-ReportAndExit {
  param([int]$ExitCode)
  $Ended = (Get-Date).ToUniversalTime()
  $failed = @($Checks | Where-Object { -not $_.pass })
  $report = [ordered]@{
    preflight = "BENCH-AGENT-001-preflight-v1.2"
    run_id = $RunId
    model = $Model
    required_context_tokens = $ContextTokens
    status = $(if($failed.Count -eq 0){"PASS"}else{"FAIL"})
    started_utc = $Started.ToString("o")
    ended_utc = $Ended.ToString("o")
    wall_seconds = [math]::Round(($Ended-$Started).TotalSeconds,3)
    checks_passed = @($Checks | Where-Object {$_.pass}).Count
    checks_total = $Checks.Count
    failures = $failed
    checks = $Checks
  }
  $report | ConvertTo-Json -Depth 10 | Set-Content $ReportPath -Encoding utf8
  Write-Host ""
  if($ExitCode -eq 0){
    Write-Host "BENCH-AGENT-001 PREFLIGHT PASS" -ForegroundColor Green
  } else {
    Write-Host "BENCH-AGENT-001 PREFLIGHT FAIL" -ForegroundColor Red
  }
  Write-Host "Report: $ReportPath"
  exit $ExitCode
}

Write-Host "===================================================="
Write-Host " BENCH-AGENT-001 PREFLIGHT v1.2"
Write-Host " RunId   : $RunId"
Write-Host " Model   : $Model"
Write-Host " Context : $ContextTokens"
Write-Host "===================================================="

# 1) Required files and no consumed RunId.
$requiredFiles = @(
  $Seed,$TaskPrompt,$DevFreeze,$VerifyDevFreeze,$AgentFreeze,$VerifyAgentFreeze,
  $PublicVerifier,$BuildReviewContext,$Summarize,$Compare
)
$missing = @($requiredFiles | Where-Object { !(Test-Path $_) })
Add-Check "FILES_REQUIRED" ($missing.Count -eq 0) $(if($missing.Count){"Missing: " + ($missing -join "; ")}else{"all required benchmark files present"}) "Restore/freeze BENCH-AGENT-001 before running."
Add-Check "RUN_ID_UNUSED" (!(Test-Path $RunPath)) $(if(Test-Path $RunPath){"Run path already exists: $RunPath"}else{"RunId is unused"}) "Choose a new RunId or deliberately remove the invalid run before retrying."
if($missing.Count -gt 0 -or (Test-Path $RunPath)){ Write-ReportAndExit 2 }

# 2) Frozen provenance.
$devVerify = Invoke-NativeCapture -FilePath "powershell.exe" -ArgumentList @("-NoProfile","-ExecutionPolicy","Bypass","-File",$VerifyDevFreeze)
Add-Check "DEV002_FREEZE" ($devVerify.ExitCode -eq 0) $(($devVerify.Stdout + " " + $devVerify.Stderr).Trim()) "Repair DEV002 provenance before any inference."
$agentVerify = Invoke-NativeCapture -FilePath "powershell.exe" -ArgumentList @("-NoProfile","-ExecutionPolicy","Bypass","-File",$VerifyAgentFreeze,"-Dev002Root",$Dev002Root,"-OutputRoot",$OutputRoot)
Add-Check "AGENT001_FREEZE" ($agentVerify.ExitCode -eq 0) $(($agentVerify.Stdout + " " + $agentVerify.Stderr).Trim()) "Run freeze-agent.ps1 after installing the final v1.2 scripts."
if($devVerify.ExitCode -ne 0 -or $agentVerify.ExitCode -ne 0){ Write-ReportAndExit 2 }

# 3) Executables.
$commands = [ordered]@{
  "POWERSHELL" = "powershell.exe"
  "GIT" = "git.exe"
  "TAR" = "tar.exe"
  "DOCKER" = "docker.exe"
  "NODE" = "node.exe"
  "NPM" = "npm.cmd"
  "PYTHON" = $PythonExe
  "OPENCODE" = $OpenCodeExe
}
$commandFail = $false
foreach($k in $commands.Keys){
  $cmd = Get-Command $commands[$k] -ErrorAction SilentlyContinue
  $ok = ($null -ne $cmd)
  if(!$ok){ $commandFail = $true }
  Add-Check "CMD_$k" $ok $(if($ok){$cmd.Source}else{"not found: " + $commands[$k]}) "Install/fix PATH before running the benchmark."
}
if($commandFail){ Write-ReportAndExit 2 }

$ocResolved = (Get-Command $OpenCodeExe -ErrorAction SilentlyContinue).Source
$ocExt = [System.IO.Path]::GetExtension([string]$ocResolved).ToLowerInvariant()
$ocLauncherOk = (-not [string]::IsNullOrWhiteSpace($ocResolved))
Add-Check "OPENCODE_LAUNCHER_RESOLVED" $ocLauncherOk ("path=" + $ocResolved + "; extension=" + $ocExt) "Repair the OpenCode installation/PATH before running."
if(!$ocLauncherOk){ Write-ReportAndExit 2 }

# 4) Ports must be free before Docker/backend smoke test.
$p1 = Test-LocalPortFree $VerifierMySqlPort
$p2 = Test-LocalPortFree $VerifierBackendPort
Add-Check "PORT_MYSQL_FREE" $p1 "127.0.0.1:$VerifierMySqlPort" "Stop the process/container using this port."
Add-Check "PORT_BACKEND_FREE" $p2 "127.0.0.1:$VerifierBackendPort" "Stop the process using this port."
if(!$p1 -or !$p2){ Write-ReportAndExit 2 }

# 5) Docker daemon + Linux engine + exact MySQL image locally present.
$dockerInfo = Invoke-NativeCapture -FilePath "docker.exe" -ArgumentList @("info","--format","{{.OSType}}")
$dockerReady = ($dockerInfo.ExitCode -eq 0)
Add-Check "DOCKER_DAEMON" $dockerReady $(($dockerInfo.Stdout + " " + $dockerInfo.Stderr).Trim()) "Start Docker Desktop and wait for the Linux engine to be ready."
if(!$dockerReady){ Write-ReportAndExit 2 }
$dockerLinux = ($dockerInfo.Stdout.Trim().ToLowerInvariant() -eq "linux")
Add-Check "DOCKER_LINUX_ENGINE" $dockerLinux $("OSType=" + $dockerInfo.Stdout.Trim()) "Switch Docker Desktop to the Linux engine/context."
$image = Invoke-NativeCapture -FilePath "docker.exe" -ArgumentList @("image","inspect","mysql:8.4","--format","{{.Id}}")
$imageOk = ($image.ExitCode -eq 0 -and -not [string]::IsNullOrWhiteSpace($image.Stdout))
Add-Check "DOCKER_IMAGE_MYSQL84" $imageOk $(if($imageOk){$image.Stdout.Trim()}else{$image.Stderr.Trim()}) "Run: docker pull mysql:8.4"
if(!$dockerLinux -or !$imageOk){ Write-ReportAndExit 2 }

# 6) Core tool versions.
$nodeVer = Invoke-NativeCapture -FilePath "node.exe" -ArgumentList @("--version")
$npmVer = Invoke-NativeCapture -FilePath "npm.cmd" -ArgumentList @("--version")
$pyVer = Invoke-NativeCapture -FilePath $PythonExe -ArgumentList @("--version")
$gitVer = Invoke-NativeCapture -FilePath "git.exe" -ArgumentList @("--version")
$ocVer = Invoke-NativeCapture -FilePath $OpenCodeExe -ArgumentList @("--version")
Add-Check "VERSION_NODE" ($nodeVer.ExitCode -eq 0) $nodeVer.Stdout.Trim() "Fix Node.js installation."
Add-Check "VERSION_NPM" ($npmVer.ExitCode -eq 0) $npmVer.Stdout.Trim() "Fix npm installation."
Add-Check "VERSION_PYTHON" ($pyVer.ExitCode -eq 0) ($pyVer.Stdout + $pyVer.Stderr).Trim() "Activate/install the expected Python environment."
Add-Check "VERSION_GIT" ($gitVer.ExitCode -eq 0) $gitVer.Stdout.Trim() "Fix Git installation."
Add-Check "VERSION_OPENCODE" ($ocVer.ExitCode -eq 0) ($ocVer.Stdout + $ocVer.Stderr).Trim() "Fix OpenCode installation."
$versionResults = @($nodeVer,$npmVer,$pyVer,$gitVer,$ocVer)
if(@($versionResults | Where-Object {$_.ExitCode -ne 0}).Count -gt 0){ Write-ReportAndExit 2 }

# 7) Python scripts compile before benchmark work.
$compileArgs = @("-m","py_compile",$PublicVerifier,$BuildReviewContext,$Summarize,$Compare)
$compile = Invoke-NativeCapture -FilePath $PythonExe -ArgumentList $compileArgs
Add-Check "PYTHON_SCRIPTS_COMPILE" ($compile.ExitCode -eq 0) $(($compile.Stdout + " " + $compile.Stderr).Trim()) "Fix the pipeline scripts before freezing/running."
if($compile.ExitCode -ne 0){ Write-ReportAndExit 2 }

# 8) Seed archive can be listed.
$tarList = Invoke-NativeCapture -FilePath "tar.exe" -ArgumentList @("-tf",$Seed)
$tarOk = ($tarList.ExitCode -eq 0 -and -not [string]::IsNullOrWhiteSpace($tarList.Stdout))
Add-Check "SEED_TAR_READABLE" $tarOk $(if($tarOk){"seed.tar readable"}else{$tarList.Stderr.Trim()}) "Restore the frozen DEV002 seed."
if(!$tarOk){ Write-ReportAndExit 2 }

# 9) llama.cpp endpoint, exact model identity and exact benchmark context.
try {
  $health = Invoke-RestMethod -Uri "$LlamaBaseUrl/health" -Headers (Get-Headers) -TimeoutSec 10 -ErrorAction Stop
  Add-Check "LLAMA_HEALTH" $true "server responded"
} catch {
  Add-Check "LLAMA_HEALTH" $false $_.Exception.Message "Start the benchmark llama-server profile and verify API key/network."
  Write-ReportAndExit 2
}

try {
  $models = Invoke-RestMethod -Uri "$LlamaBaseUrl/v1/models" -Headers (Get-Headers) -TimeoutSec 10 -ErrorAction Stop
  $wanted = $Model -replace '^local/',''
  $match = $null
  foreach($m in @($models.data)){
    $ids = @($m.id) + @($m.aliases)
    if($ids -contains $wanted -or $ids -contains $Model){ $match = $m; break }
  }
  Add-Check "LLAMA_MODEL_VISIBLE" ($null -ne $match) $(if($match){"id=$($match.id)"}else{"wanted=$wanted"}) "Start the intended benchmark model/alias."
  if(!$match){ Write-ReportAndExit 2 }

  $ctxOk = ([int64]$match.meta.n_ctx -eq [int64]$ContextTokens)
  Add-Check "LLAMA_CONTEXT_EXACT" $ctxOk ("n_ctx=" + $match.meta.n_ctx) "Restart llama-server with -c $ContextTokens."

  $trainOk = ([int64]$match.meta.n_ctx_train -ge [int64]$ContextTokens)
  Add-Check "LLAMA_CONTEXT_TRAIN" $trainOk ("n_ctx_train=" + $match.meta.n_ctx_train) "Use the intended model metadata."

  if($ExpectedNParams -gt 0){
    $npOk = ([int64]$match.meta.n_params -eq $ExpectedNParams)
    Add-Check "LLAMA_N_PARAMS" $npOk ("n_params=" + $match.meta.n_params) "The loaded model is not the expected benchmark model."
  }
  if($ExpectedModelSize -gt 0){
    $szOk = ([int64]$match.meta.size -eq $ExpectedModelSize)
    Add-Check "LLAMA_MODEL_SIZE" $szOk ("size=" + $match.meta.size) "The loaded GGUF differs from the expected benchmark profile."
  }
  if(-not [string]::IsNullOrWhiteSpace($ExpectedFtypePattern)){
    $ft = [string]$match.meta.ftype
    $ftOk = ($ft -match $ExpectedFtypePattern)
    Add-Check "LLAMA_FTYPE" $ftOk ("ftype=" + $ft) "Load the expected Q3 benchmark model."
  }
} catch {
  Add-Check "LLAMA_MODELS_QUERY" $false $_.Exception.Message "Fix /v1/models access before inference."
  Write-ReportAndExit 2
}

if(@($Checks | Where-Object {-not $_.pass}).Count -gt 0){ Write-ReportAndExit 2 }

# 10) OpenCode must see the exact configured provider/model before the LLM is called.
$ocModels = Invoke-NativeCapture -FilePath $OpenCodeExe -ArgumentList @("models")
$ocModelOk = ($ocModels.ExitCode -eq 0 -and (($ocModels.Stdout + $ocModels.Stderr) -match [regex]::Escape($Model)))
Add-Check "OPENCODE_MODEL_VISIBLE" $ocModelOk $(if($ocModelOk){$Model}else{($ocModels.Stdout + " " + $ocModels.Stderr).Trim()}) "Fix OpenCode provider/model configuration."
if(!$ocModelOk){ Write-ReportAndExit 2 }

# 11) Full infrastructure dry-run on a disposable copy of the untouched seed.
# This intentionally exercises Docker -> MySQL -> npm install -> bcrypt -> db:migrate
# -> backend startup -> HTTP verifier, BEFORE any model inference and without consuming RunId.
try {
  $guid = [guid]::NewGuid().ToString("N")
  $TempRoot = Join-Path $env:TEMP ("BENCH-AGENT-001-preflight-" + $guid)
  $TempWorkspace = Join-Path $TempRoot "workspace"
  $TempLogs = Join-Path $TempRoot "logs"
  $TempReport = Join-Path $TempRoot "verifier.json"
  New-Item -ItemType Directory -Force $TempWorkspace,$TempLogs | Out-Null

  $extract = Invoke-NativeCapture -FilePath "tar.exe" -ArgumentList @("-xf",$Seed,"-C",$TempWorkspace)
  if($extract.ExitCode -ne 0){
    Add-Check "DRYRUN_SEED_EXTRACT" $false $extract.Stderr.Trim() "Restore seed.tar/tar.exe."
    Write-ReportAndExit 2
  }
  Add-Check "DRYRUN_SEED_EXTRACT" $true "disposable seed extracted"

  $dry = Invoke-NativeCapture -FilePath $PythonExe -ArgumentList @(
    $PublicVerifier,
    "--workspace",$TempWorkspace,
    "--out",$TempReport,
    "--logs",$TempLogs,
    "--run-id",("preflight-" + $guid.Substring(0,12)),
    "--mysql-port","$VerifierMySqlPort",
    "--backend-port","$VerifierBackendPort"
  ) -WorkingDirectory $TempWorkspace

  if(!(Test-Path $TempReport)){
    Add-Check "DRYRUN_PUBLIC_VERIFIER" $false ("no report; exit=" + $dry.ExitCode + "; stderr=" + $dry.Stderr) "Repair verifier/infrastructure before inference."
    Write-ReportAndExit 2
  }
  $vr = Get-Content $TempReport -Raw | ConvertFrom-Json
  $infraOk = ($vr.status -ne "INFRA_ERROR" -and $vr.stage -eq "complete")
  Add-Check "DRYRUN_PUBLIC_VERIFIER" $infraOk ("status=" + $vr.status + "; stage=" + $vr.stage + "; checks=" + $vr.checks_passed + "/" + $vr.checks_total) "Inspect preflight verifier logs; Docker/MySQL/npm/migration/backend must all reach stage=complete."
  if(!$infraOk){
    # Persist useful diagnostics next to the preflight report before temp cleanup.
    $diagDir = Join-Path $ReportDir ("$RunId-preflight-diagnostics")
    New-Item -ItemType Directory -Force $diagDir | Out-Null
    Copy-Item $TempReport (Join-Path $diagDir "verifier.json") -Force -ErrorAction SilentlyContinue
    Copy-Item $TempLogs (Join-Path $diagDir "logs") -Recurse -Force -ErrorAction SilentlyContinue
    Write-ReportAndExit 2
  }

  Start-Sleep -Milliseconds 800
  $mysqlReleased = Test-LocalPortFree $VerifierMySqlPort
  $backendReleased = Test-LocalPortFree $VerifierBackendPort
  Add-Check "DRYRUN_MYSQL_PORT_RELEASED" $mysqlReleased "port $VerifierMySqlPort released after verifier" "Remove stale Docker container/process before running."
  Add-Check "DRYRUN_BACKEND_PORT_RELEASED" $backendReleased "port $VerifierBackendPort released after verifier" "Stop stale backend process before running."
  if(!$mysqlReleased -or !$backendReleased){ Write-ReportAndExit 2 }
} catch {
  Add-Check "DRYRUN_UNEXPECTED" $false $_.Exception.Message "Repair the preflight environment before inference."
  Write-ReportAndExit 2
} finally {
  if($TempRoot -and (Test-Path $TempRoot)){
    Remove-Item $TempRoot -Recurse -Force -ErrorAction SilentlyContinue
  }
}

Write-ReportAndExit 0
