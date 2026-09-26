$ErrorActionPreference = "Stop"

function Test-Command {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$DisplayName
    )

    $cmd = Get-Command $Name -ErrorAction SilentlyContinue
    if ($null -eq $cmd) {
        Write-Host "MISSING: $DisplayName"
        return $false
    }

    Write-Host "FOUND:   $DisplayName -> $($cmd.Source)"
    return $true
}

$ok = $true
$ok = (Test-Command "git.exe" "Git") -and $ok
$ok = (Test-Command "docker.exe" "Docker") -and $ok
$ok = (Test-Command "node.exe" "Node.js") -and $ok
$ok = (Test-Command "npm.cmd" "npm") -and $ok

$pythonCommand = $null
if (Get-Command "python.exe" -ErrorAction SilentlyContinue) {
    $pythonCommand = "python.exe"
    Write-Host "FOUND:   Python -> $((Get-Command python.exe).Source)"
}
elseif (Get-Command "py.exe" -ErrorAction SilentlyContinue) {
    $pythonCommand = "py.exe"
    Write-Host "FOUND:   Python launcher -> $((Get-Command py.exe).Source)"
}
else {
    Write-Host "MISSING: Python 3"
    $ok = $false
}

if (-not $ok) {
    Write-Error "Preflight FAILED: required commands are missing."
}

& docker.exe compose version *> $null
if ($LASTEXITCODE -ne 0) {
    throw "Preflight FAILED: Docker Compose plugin is not available."
}

& docker.exe info *> $null
if ($LASTEXITCODE -ne 0) {
    throw "Preflight FAILED: Docker Desktop/daemon is not running or is unavailable."
}

Write-Host ""
Write-Host "## Versions"
Write-Host "Windows: $([System.Environment]::OSVersion.VersionString)"
Write-Host "Node:    $(& node.exe --version)"
Write-Host "npm:     $(& npm.cmd --version)"

if ($pythonCommand -eq "python.exe") {
    Write-Host "Python:  $(& python.exe --version 2>&1)"
}
else {
    Write-Host "Python:  $(& py.exe -3 --version 2>&1)"
}

Write-Host "Docker:  $(& docker.exe --version)"
Write-Host "Compose: $(& docker.exe compose version)"
Write-Host ""
Write-Host "Preflight PASS"
