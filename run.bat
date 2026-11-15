@echo off
cd /d "%~dp0"
echo Starting FinIntellect on port 5001...
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" app.py %*
) else (
    python app.py %*
)
pause
