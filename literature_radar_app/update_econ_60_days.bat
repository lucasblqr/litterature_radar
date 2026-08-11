@echo off
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo The Python environment does not exist yet.
    echo Please run start_app.bat first.
    pause
    exit /b 1
)

echo ============================================================
echo ECON JOURNALS - EXACT ISSN UPDATE - LAST 60 DAYS
echo ============================================================
echo This fetches the economics journals using exact journal ISSNs.
echo No topic, keyword, ranking, or abstract filter is applied to collection.
echo.

".venv\Scripts\python.exe" scripts\update_econ_papers.py --days 60

echo.
echo Finished. Run run_app.bat and open Team's interest - Econ Journal.
pause
