@echo off
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo The Python environment does not exist yet.
    echo Please run start_app.bat first.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" scripts\update_papers.py --days 60
pause
