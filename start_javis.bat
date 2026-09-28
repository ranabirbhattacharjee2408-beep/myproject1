@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Run build_windows.ps1 first ^(it creates the environment^).
  pause
  exit /b 1
)
".venv\Scripts\python.exe" launcher.py
