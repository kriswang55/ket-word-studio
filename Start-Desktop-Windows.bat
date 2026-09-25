@echo off
cd /d "%~dp0"
if exist "releases\windows\KETWordStudio.exe" (
  start "" "releases\windows\KETWordStudio.exe"
) else (
  where py >nul 2>nul
  if errorlevel 1 (
    python run_desktop.py
  ) else (
    py -3 run_desktop.py
  )
  if errorlevel 1 pause
)
