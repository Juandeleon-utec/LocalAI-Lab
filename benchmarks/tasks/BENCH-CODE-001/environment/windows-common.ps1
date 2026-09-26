function Ensure-DockerCommand {
    $existing = Get-Command "docker.exe" -ErrorAction SilentlyContinue
    if ($null -ne $existing) {
        return $existing.Source
    }

    $candidatePaths = @()

    if ($env:ProgramFiles) {
        $candidatePaths += (Join-Path $env:ProgramFiles "Docker\Docker\resources\bin\docker.exe")
    }

    $candidatePaths += "C:\Program Files\Docker\Docker\resources\bin\docker.exe"

    foreach ($candidate in ($candidatePaths | Select-Object -Unique)) {
        if (Test-Path $candidate) {
            $dockerDir = Split-Path -Parent $candidate

            $pathParts = $env:Path -split ";"
            if ($pathParts -notcontains $dockerDir) {
                $env:Path = "$dockerDir;$env:Path"
            }

            $resolved = Get-Command "docker.exe" -ErrorAction SilentlyContinue
            if ($null -ne $resolved) {
                return $resolved.Source
            }
        }
    }

    return $null
}
