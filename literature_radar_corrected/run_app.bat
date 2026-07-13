@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo The Python environment does not exist yet.
    echo Please run start_app.bat first.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" -c "import streamlit" >nul 2>nul
if errorlevel 1 (
    echo Streamlit is missing from the Python environment.
    echo Please run repair_environment.bat.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" -m streamlit run app.py
pause
