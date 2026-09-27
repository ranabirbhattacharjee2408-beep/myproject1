@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo JARVIS is not installed yet.
  echo Run build_windows.ps1 first.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" "main.py"
pause