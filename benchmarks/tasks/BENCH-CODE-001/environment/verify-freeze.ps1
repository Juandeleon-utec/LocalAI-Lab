$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$taskDir = Split-Path -Parent $scriptDir
$repoRoot = (Resolve-Path (Join-Path $taskDir "..\..\..")).Path
$promptPath = Join-Path $taskDir "prompt.md"

$expected = @{
    PromptSha256 = "e1ec6e63a2a603a4d5591158a262d66de1f838a93e72d03ae2a158827e35dbac"
    NodeVersion = "v24.19.0"
    NpmVersion = "11.17.0"
    PythonVersion = "Python 3.11.9"
    DockerVersionPrefix = "Docker version 29.8.0, build 88096ef"
    ComposeVersion = "Docker Compose version v5.5.1"
    WindowsVersion = "10.0.26200"
    MySqlDigest = "mysql@sha256:0744ee5ef89ce6ccfa13de3e579fe6b9e27f93dd70da9c06d2c908b1b193fb8d"
}

function Assert-Equal {
    param([string]$Name, [string]$Actual, [string]$Expected)

    if ($Actual -ne $Expected) {
        throw "$Name mismatch. Expected '$Expected' but found '$Actual'."
    }

    Write-Host "PASS: $Name = $Actual"
}

$promptHash = (Get-FileHash -Algorithm SHA256 -Path $promptPath).Hash.ToLowerInvariant()
Assert-Equal "prompt_sha256" $promptHash $expected.PromptSha256

Assert-Equal "node" (& node.exe --version).Trim() $expected.NodeVersion
Assert-Equal "npm" (& npm.cmd --version).Trim() $expected.NpmVersion

$pythonVersion = if (Get-Command python.exe -ErrorAction SilentlyContinue) {
    (& python.exe --version 2>&1).Trim()
}
elseif (Get-Command py.exe -ErrorAction SilentlyContinue) {
    (& py.exe -3 --version 2>&1).Trim()
}
else {
    throw "Python 3 not found."
}
Assert-Equal "python" $pythonVersion $expected.PythonVersion

Assert-Equal "docker" (& docker.exe --version).Trim() $expected.DockerVersionPrefix
Assert-Equal "docker_compose" (& docker.exe compose version).Trim() $expected.ComposeVersion

$os = Get-CimInstance Win32_OperatingSystem
Assert-Equal "windows_version" $os.Version $expected.WindowsVersion

$repoDigests = & docker.exe image inspect $expected.MySqlDigest --format "{{json .RepoDigests}}"
if ($LASTEXITCODE -ne 0) {
    throw "Pinned MySQL image is not available locally."
}
if ($repoDigests -notmatch [regex]::Escape($expected.MySqlDigest)) {
    throw "MySQL digest mismatch. Expected $($expected.MySqlDigest), found $repoDigests"
}
Write-Host "PASS: mysql_digest = $($expected.MySqlDigest)"

Write-Host ""
Write-Host "BENCH-CODE-001 formal staging freeze verification PASS"
