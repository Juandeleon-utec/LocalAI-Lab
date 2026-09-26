param(
    [string]$BaseUrl = "http://127.0.0.1:3000",
    [int]$TimeoutSeconds = 60
)

$ErrorActionPreference = "Stop"
$deadline = (Get-Date).AddSeconds($TimeoutSeconds)

while ((Get-Date) -lt $deadline) {
    try {
        $response = Invoke-RestMethod -Uri "$BaseUrl/health" -Method Get -TimeoutSec 2
        if ($null -ne $response -and $response.status -eq "ok") {
            Write-Host "Candidate is healthy at $BaseUrl"
            exit 0
        }
    }
    catch {
        # Candidate may still be starting.
    }

    Start-Sleep -Seconds 1
}

throw "Candidate did not become healthy within $TimeoutSeconds seconds: $BaseUrl/health"
