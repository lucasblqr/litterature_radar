@echo off
setlocal
cd /d "%~dp0"

echo Repairing Literature Radar Python environment...
echo This will delete the old .venv folder and reinstall the packages.
echo.

if exist ".venv" (
    rmdir /s /q ".venv"
)

py -m venv .venv
if errorlevel 1 (
    echo Failed to create the Python environment.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" -m ensurepip --upgrade
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install streamlit pandas requests pyyaml python-dateutil

".venv\Scripts\python.exe" -c "import streamlit; print('Streamlit version:', streamlit.__version__)"
if errorlevel 1 (
    echo Repair failed. Streamlit is still missing.
    pause
    exit /b 1
)

echo.
echo Repair complete. Opening the app...
".venv\Scripts\python.exe" -m streamlit run app.py

pause
