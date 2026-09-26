$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $scriptDir "windows-common.ps1")
if ($null -eq (Ensure-DockerCommand)) { throw "Docker Desktop CLI was not found." }

$ErrorActionPreference = "Stop"

Push-Location $scriptDir

try {
    & docker.exe compose down --remove-orphans
    if ($LASTEXITCODE -ne 0) {
        throw "Docker Compose failed to stop the BENCH-CODE-001 database."
    }
}
finally {
    Pop-Location
}
