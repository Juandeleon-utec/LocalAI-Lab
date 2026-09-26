param(
    [Parameter(Mandatory = $true)][string]$CandidateDirectory,
    [Parameter(Mandatory = $true)][string]$OutputDirectory
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $scriptDir "windows-common.ps1")
if ($null -eq (Ensure-DockerCommand)) { throw "Docker Desktop CLI was not found." }

$candidateDir = (Resolve-Path $CandidateDirectory).Path

if (-not (Test-Path $OutputDirectory)) {
    New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
}
$outputDir = (Resolve-Path $OutputDirectory).Path

$port = if ($env:PORT) { $env:PORT } else { "3000" }
$dbHost = if ($env:DB_HOST) { $env:DB_HOST } else { "127.0.0.1" }
$dbHostPort = if ($env:DB_HOST_PORT) { $env:DB_HOST_PORT } else { "3307" }
$dbName = if ($env:DB_NAME) { $env:DB_NAME } else { "bench_code_001" }
$dbUser = if ($env:DB_USER) { $env:DB_USER } else { "bench_user" }
$dbPassword = if ($env:DB_PASSWORD) { $env:DB_PASSWORD } else { "bench_password" }
$authSecret = if ($env:AUTH_SECRET) { $env:AUTH_SECRET } else { "bench-code-001-local-secret" }
$mysqlRootPassword = if ($env:MYSQL_ROOT_PASSWORD) { $env:MYSQL_ROOT_PASSWORD } else { "bench-root-password" }
$baseUrl = "http://127.0.0.1:$port"
$startedAt = Get-Date

if (-not $env:BENCH_EVALUATOR -and $env:BENCH_ALLOW_NO_EVALUATOR -ne "1") {
    throw "BENCH_EVALUATOR is required. Set BENCH_ALLOW_NO_EVALUATOR=1 only for an unscored smoke test."
}

if (-not (Test-Path (Join-Path $candidateDir "package.json"))) {
    throw "Candidate does not contain package.json: $candidateDir"
}

function Get-PythonInvocation {
    if (Get-Command python.exe -ErrorAction SilentlyContinue) {
        return @{ File = "python.exe"; Prefix = @() }
    }
    if (Get-Command py.exe -ErrorAction SilentlyContinue) {
        return @{ File = "py.exe"; Prefix = @("-3") }
    }
    throw "Python 3 is required."
}

function Invoke-Evaluator {
    param([string]$Phase, [string]$OutputPath)

    if (-not $env:BENCH_EVALUATOR) { return 0 }
    if (-not (Test-Path $env:BENCH_EVALUATOR)) {
        throw "BENCH_EVALUATOR does not exist: $($env:BENCH_EVALUATOR)"
    }

    $evaluatorArgs = @(
        "--phase", $Phase,
        "--base-url", $baseUrl,
        "--output", $OutputPath,
        "--state", (Join-Path $outputDir "evaluator-state.json"),
        "--compose-file", (Join-Path $scriptDir "docker-compose.yml"),
        "--db-name", $dbName,
        "--db-root-password", $mysqlRootPassword
    )

    if ([System.IO.Path]::GetExtension($env:BENCH_EVALUATOR).ToLowerInvariant() -eq ".py") {
        $python = Get-PythonInvocation
        $args = @() + $python.Prefix + @($env:BENCH_EVALUATOR) + $evaluatorArgs
        & $python.File @args | Out-Host
        $code = $LASTEXITCODE
        return [int]$code
    }

    & $env:BENCH_EVALUATOR @evaluatorArgs | Out-Host
    $code = $LASTEXITCODE
    return [int]$code
}

$script:appProcess = $null

function Stop-CandidateApp {
    if ($null -ne $script:appProcess -and -not $script:appProcess.HasExited) {
        $previousErrorActionPreference = $ErrorActionPreference
        $ErrorActionPreference = "Continue"
        try {
            & taskkill.exe /PID $script:appProcess.Id /T /F 2>&1 | Out-Null
        }
        finally {
            $ErrorActionPreference = $previousErrorActionPreference
        }
        try { $script:appProcess.WaitForExit(10000) | Out-Null } catch {}
    }
    $script:appProcess = $null
}

function Start-CandidateApp {
    $appLog = Join-Path $outputDir "app.log"

    $env:PORT = $port
    $env:DB_HOST = $dbHost
    $env:DB_PORT = $dbHostPort
    $env:DB_NAME = $dbName
    $env:DB_USER = $dbUser
    $env:DB_PASSWORD = $dbPassword
    $env:AUTH_SECRET = $authSecret

    $quotedLog = '"' + $appLog + '"'
    $command = "npm start >> $quotedLog 2>&1"

    $script:appProcess = Start-Process -FilePath "cmd.exe" -ArgumentList @("/d", "/s", "/c", $command) -WorkingDirectory $candidateDir -WindowStyle Hidden -PassThru
    $script:appProcess.Id | Set-Content -Path (Join-Path $outputDir "app.pid")
}

function Write-RunInfo {
    param([string]$Text)
    Add-Content -Path (Join-Path $outputDir "run-info.txt") -Value $Text
}

function Invoke-NpmLogged {
    param([string[]]$Arguments, [string]$LogPath)

    Push-Location $candidateDir
    try {
        & npm.cmd @Arguments 2>&1 | Tee-Object -FilePath $LogPath
        $exitCode = $LASTEXITCODE
        if ($exitCode -ne 0) {
            throw "npm $($Arguments -join ' ') failed with exit code $exitCode."
        }
    }
    finally {
        Pop-Location
    }
}

try {
    Set-Content -Path (Join-Path $outputDir "run-info.txt") -Value "candidate_dir=$candidateDir"
    Write-RunInfo "started_at_utc=$($startedAt.ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ'))"

    try {
        $candidateCommit = (& git.exe -C $candidateDir rev-parse HEAD 2>$null).Trim()
        if ($LASTEXITCODE -eq 0 -and $candidateCommit) {
            Write-RunInfo "candidate_commit=$candidateCommit"
        }
    }
    catch {}

    $env:PORT = $port
    $env:DB_HOST = $dbHost
    $env:DB_PORT = $dbHostPort
    $env:DB_HOST_PORT = $dbHostPort
    $env:DB_NAME = $dbName
    $env:DB_USER = $dbUser
    $env:DB_PASSWORD = $dbPassword
    $env:AUTH_SECRET = $authSecret
    $env:MYSQL_ROOT_PASSWORD = $mysqlRootPassword

    & (Join-Path $scriptDir "start-database.ps1")

    $snapshotPath = Join-Path $outputDir "environment-snapshot.txt"
    & (Join-Path $scriptDir "capture-environment.ps1") -OutputPath $snapshotPath | Set-Content -Path (Join-Path $outputDir "environment-sha256.txt")

    if (Test-Path (Join-Path $candidateDir "package-lock.json")) {
        Invoke-NpmLogged @("ci") (Join-Path $outputDir "npm-install.log")
        Write-RunInfo "install_command=npm ci"
    }
    else {
        Invoke-NpmLogged @("install") (Join-Path $outputDir "npm-install.log")
        Write-RunInfo "install_command=npm install"
    }

    Invoke-NpmLogged @("run", "db:init") (Join-Path $outputDir "db-init.log")

    Start-CandidateApp
    & (Join-Path $scriptDir "wait-health.ps1") -BaseUrl $baseUrl -TimeoutSeconds 90

    $preExit = 0
    $postExit = 0

    if ($env:BENCH_EVALUATOR) {
        $preExit = Invoke-Evaluator "pre-restart" (Join-Path $outputDir "evaluator-pre.json")
        Write-RunInfo "evaluator_pre_exit=$preExit"
    }

    Stop-CandidateApp
    Start-Sleep -Seconds 2
    Start-CandidateApp
    & (Join-Path $scriptDir "wait-health.ps1") -BaseUrl $baseUrl -TimeoutSeconds 90

    if ($env:BENCH_EVALUATOR) {
        $postExit = Invoke-Evaluator "post-restart" (Join-Path $outputDir "evaluator-post.json")
        Write-RunInfo "evaluator_post_exit=$postExit"

        $prePath = Join-Path $outputDir "evaluator-pre.json"
        $postPath = Join-Path $outputDir "evaluator-post.json"
        if ((Test-Path $prePath) -and (Test-Path $postPath)) {
            $python = Get-PythonInvocation
            $aggregateArgs = @() + $python.Prefix + @(
                (Join-Path $scriptDir "aggregate-evaluation.py"),
                "--pre", $prePath,
                "--post", $postPath,
                "--output", (Join-Path $outputDir "evaluation.json")
            )
            & $python.File @aggregateArgs
            if ($LASTEXITCODE -ne 0) { throw "Evaluation aggregation failed." }
        }
    }

    $endedAt = Get-Date
    Write-RunInfo "ended_at_utc=$($endedAt.ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ'))"
    Write-RunInfo "wall_time_seconds=$([int](($endedAt - $startedAt).TotalSeconds))"

    if ($preExit -ne 0 -or $postExit -ne 0) {
        throw "Evaluator returned a non-zero exit code."
    }

    Write-Host "BENCH-CODE-001 candidate run completed."
}
finally {
    Stop-CandidateApp

    Push-Location $scriptDir
    try {
        $previousErrorActionPreference = $ErrorActionPreference
        $ErrorActionPreference = "Continue"
        try {
            $mysqlLog = Join-Path $outputDir "mysql.log"
            & docker.exe compose logs mysql 2>&1 | ForEach-Object { "$_" } | Set-Content -Path $mysqlLog
            & docker.exe compose down --remove-orphans 2>&1 | Out-Null
        }
        catch {
            Write-Warning "Cleanup warning: $($_.Exception.Message)"
        }
        finally {
            $ErrorActionPreference = $previousErrorActionPreference
        }
    }
    finally {
        Pop-Location
    }
}
