Set-Location -Path $PSScriptRoot
Write-Host "Starting FinIntellect on port 5001..." -ForegroundColor Cyan

$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (Test-Path $venvPython) {
    & $venvPython app.py $args
}
else {
    python app.py $args
}
