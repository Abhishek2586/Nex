# NEXORA dev startup - run from project root: .\start.ps1
Write-Host "Starting NEXORA backend on :8000..." -ForegroundColor Cyan
$backend = Start-Process -FilePath ".venv\Scripts\python.exe" -ArgumentList "-m","uvicorn","nexora.edge.app:app","--reload","--port","8000" -WorkingDirectory $PSScriptRoot -PassThru -WindowStyle Normal
Write-Host "Starting NEXORA frontend on :5173..." -ForegroundColor Cyan
$frontend = Start-Process -FilePath "cmd.exe" -ArgumentList "/c","npm run dev" -WorkingDirectory "$PSScriptRoot\frontend" -PassThru -WindowStyle Normal
Write-Host ""
Write-Host "NEXORA running:" -ForegroundColor Green
Write-Host "  Frontend -> http://localhost:5173" -ForegroundColor Green
Write-Host "  Backend  -> http://localhost:8000" -ForegroundColor Green
Write-Host ""
Write-Host "Press ENTER to stop both..." -ForegroundColor Yellow
Read-Host
$backend.Kill(); $frontend.Kill()
Write-Host "Stopped." -ForegroundColor Red
