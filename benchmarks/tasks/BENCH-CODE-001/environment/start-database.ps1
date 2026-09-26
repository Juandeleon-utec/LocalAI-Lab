$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $scriptDir

try {
    & docker.exe compose down --remove-orphans *> $null

    & docker.exe compose up -d mysql
    if ($LASTEXITCODE -ne 0) {
        throw "Docker Compose could not start MySQL."
    }

    $containerId = (& docker.exe compose ps -q mysql).Trim()
    if ([string]::IsNullOrWhiteSpace($containerId)) {
        throw "MySQL container was not created."
    }

    Write-Host "Waiting for BENCH-CODE-001 MySQL..."

    for ($i = 0; $i -lt 60; $i++) {
        $status = (& docker.exe inspect -f "{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}" $containerId).Trim()

        if ($status -eq "healthy") {
            Write-Host "MySQL is healthy."
            exit 0
        }

        if ($status -eq "unhealthy") {
            & docker.exe compose logs mysql
            throw "MySQL became unhealthy."
        }

        Start-Sleep -Seconds 2
    }

    & docker.exe compose logs mysql
    throw "Timed out waiting for MySQL health."
}
finally {
    Pop-Location
}
