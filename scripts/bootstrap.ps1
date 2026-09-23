# NEXORA Bootstrap Script (PowerShell)
# Idempotent setup for the local development and demonstration environment.
# Usage: py -3.11 scripts\bootstrap.py    (Python preferred; this is a convenience wrapper)
# Or:    powershell -ExecutionPolicy Bypass -File scripts\bootstrap.ps1

param()

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot

Write-Host "NEXORA Bootstrap (PowerShell wrapper)" -ForegroundColor Cyan
Write-Host "Delegating to scripts\bootstrap.py ..."

# Prefer .venv Python if it exists, otherwise find system Python
$venvPython = Join-Path $root ".venv\Scripts\python.exe"
if (Test-Path $venvPython) {
    $pythonExe = $venvPython
} else {
    # Try py launcher, then python3, then python
    foreach ($candidate in @("py", "python3", "python")) {
        try {
            $ver = & $candidate --version 2>&1
            if ($ver -match "Python 3\.(1[1-9]|[2-9]\d)") {
                $pythonExe = $candidate
                break
            }
        } catch {}
    }
}

if (-not $pythonExe) {
    Write-Error "Python 3.11+ not found. Install Python and re-run."
    exit 1
}

Write-Host "Using Python: $pythonExe"
& $pythonExe (Join-Path $root "scripts\bootstrap.py") @args
exit $LASTEXITCODE
