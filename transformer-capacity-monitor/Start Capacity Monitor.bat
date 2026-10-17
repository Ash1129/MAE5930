@echo off
rem Double-click launcher (Windows). Starts the review app, then opens it.
rem The Airflow scheduler is a macOS/Linux process; on Windows run the review app only.
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo First-time setup: .venv\Scripts\python.exe is missing.
  echo Create it with: py -3.12 -m venv .venv
  echo Then install: .venv\Scripts\python.exe -m pip install -r requirements.txt
  pause
  exit /b 1
)
if not exist "data\feeds\readings.csv" (
  echo Generating synthetic sample feeds ^(500 transformers^)...
  ".venv\Scripts\python.exe" scripts\make_synthetic_data.py --count 500
  if errorlevel 1 (
    echo Sample data failed. See the messages above.
    pause
    exit /b 1
  )
)
start "Capacity Monitor" ".venv\Scripts\python.exe" -m webapp.app
timeout /t 2 /nobreak >nul
start "" "http://127.0.0.1:5055/"
echo Capacity Monitor is running. Close this window when you like. Use "Stop Capacity Monitor.bat" to stop.
