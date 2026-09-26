$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
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
