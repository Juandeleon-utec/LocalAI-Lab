$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $scriptDir "windows-common.ps1")
if ($null -eq (Ensure-DockerCommand)) { throw "Docker Desktop CLI was not found." }

$ErrorActionPreference = "Stop"

Push-Location $scriptDir

try {
    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        & docker.exe compose down --remove-orphans 2>&1 | Out-Host
        $dockerExitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }

    if ($dockerExitCode -ne 0) {
        throw "Docker Compose failed to stop the BENCH-CODE-001 database with exit code $dockerExitCode."
    }
}
finally {
    Pop-Location
}
