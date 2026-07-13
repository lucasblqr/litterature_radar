@echo off
cd /d "%~dp0"

py -m venv .venv
if errorlevel 1 (
    echo Failed to create the Python environment.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt

echo.
echo Setup complete. You can now run start_app.bat or run_app.bat
pause
