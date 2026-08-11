@echo off
setlocal
cd /d "%~dp0"

echo Starting Literature Radar...
echo.

where py >nul 2>nul
if errorlevel 1 (
    echo Python launcher "py" was not found.
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo Creating Python environment...
    py -m venv .venv
    if errorlevel 1 (
        echo Failed to create the Python environment.
        pause
        exit /b 1
    )
)

echo Checking pip...
".venv\Scripts\python.exe" -m ensurepip --upgrade

echo Installing packages...
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 (
    echo Failed to upgrade pip.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    echo Failed to install packages from requirements.txt.
    echo.
    echo Trying direct Streamlit install...
    ".venv\Scripts\python.exe" -m pip install streamlit pandas requests pyyaml python-dateutil
    if errorlevel 1 (
        echo Direct install also failed.
        pause
        exit /b 1
    )
)

echo Verifying Streamlit...
".venv\Scripts\python.exe" -c "import streamlit; print('Streamlit version:', streamlit.__version__)"
if errorlevel 1 (
    echo Streamlit is still not installed. Reinstalling once more...
    ".venv\Scripts\python.exe" -m pip install --force-reinstall streamlit
    ".venv\Scripts\python.exe" -c "import streamlit; print('Streamlit version:', streamlit.__version__)"
    if errorlevel 1 (
        echo Streamlit installation failed.
        pause
        exit /b 1
    )
)

echo.
echo Opening the app...
".venv\Scripts\python.exe" -m streamlit run app.py

pause
