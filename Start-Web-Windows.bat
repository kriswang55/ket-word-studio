@echo off
cd /d "%~dp0"
if exist "releases\windows\KETWordStudioWeb.exe" (
  "releases\windows\KETWordStudioWeb.exe"
) else (
  where py >nul 2>nul
  if errorlevel 1 (
    python run_web.py
  ) else (
    py -3 run_web.py
  )
)
if errorlevel 1 pause
