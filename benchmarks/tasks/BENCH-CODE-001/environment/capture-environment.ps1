param(
    [string]$OutputPath = "environment-snapshot.txt"
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $scriptDir "windows-common.ps1")
if ($null -eq (Ensure-DockerCommand)) { throw "Docker Desktop CLI was not found." }

$lines = New-Object System.Collections.Generic.List[string]

function Add-Line([string]$Text = "") {
    $lines.Add($Text)
}

Add-Line "timestamp_utc=$((Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ'))"
Add-Line ""
Add-Line "## Windows"
Add-Line ([System.Environment]::OSVersion.VersionString)

try {
    $os = Get-CimInstance Win32_OperatingSystem
    Add-Line "caption=$($os.Caption)"
    Add-Line "version=$($os.Version)"
    Add-Line "build=$($os.BuildNumber)"
}
catch {}

Add-Line ""
Add-Line "## CPU"
try {
    Get-CimInstance Win32_Processor | ForEach-Object {
        Add-Line "name=$($_.Name)"
        Add-Line "cores=$($_.NumberOfCores)"
        Add-Line "logical_processors=$($_.NumberOfLogicalProcessors)"
    }
}
catch {}

Add-Line ""
Add-Line "## Memory"
try {
    $computer = Get-CimInstance Win32_ComputerSystem
    Add-Line "total_physical_memory_bytes=$($computer.TotalPhysicalMemory)"
}
catch {}

Add-Line ""
Add-Line "## Node"
Add-Line (& node.exe --version)

Add-Line ""
Add-Line "## npm"
Add-Line (& npm.cmd --version)

Add-Line ""
Add-Line "## Python"
if (Get-Command python.exe -ErrorAction SilentlyContinue) {
    Add-Line (& python.exe --version 2>&1)
}
elseif (Get-Command py.exe -ErrorAction SilentlyContinue) {
    Add-Line (& py.exe -3 --version 2>&1)
}

Add-Line ""
Add-Line "## Docker"
Add-Line (& docker.exe --version)

Add-Line ""
Add-Line "## Docker Compose"
Add-Line (& docker.exe compose version)

Add-Line ""
Add-Line "## MySQL image"
$mysqlImage = if ($env:MYSQL_IMAGE) { $env:MYSQL_IMAGE } else { "mysql:8.4" }
try {
    $repoDigests = & docker.exe image inspect $mysqlImage --format "{{json .RepoDigests}}"
    Add-Line $repoDigests
}
catch {
    Add-Line "image_not_available=$mysqlImage"
}

$fullPath = [System.IO.Path]::GetFullPath($OutputPath)
$lines | Set-Content -Path $fullPath -Encoding UTF8

$hash = Get-FileHash -Algorithm SHA256 -Path $fullPath
Write-Output "$($hash.Hash.ToLower())  $([System.IO.Path]::GetFileName($fullPath))"
