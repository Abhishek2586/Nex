# NEXORA Start Script (PowerShell wrapper)
# Usage: powershell -ExecutionPolicy Bypass -File scripts\start.ps1 [--profile demo]

param(
    [string]$Profile = ""
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot

$venvPython = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Error "Virtual environment not found at .venv\. Run scripts\bootstrap.ps1 first."
    exit 1
}

$args_list = @("scripts\start.py")
if ($Profile -ne "") {
    $args_list += "--profile"
    $args_list += $Profile
}

Write-Host "Starting NEXORA with Python: $venvPython" -ForegroundColor Cyan
& $venvPython @args_list
exit $LASTEXITCODE
