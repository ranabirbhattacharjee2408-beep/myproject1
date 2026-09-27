$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    py -3 -m venv .venv
}

$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
& $python -m pip install --upgrade pip
& $python -m pip install -r requirements-desktop.txt
& $python -m pip install pyinstaller
& $python -m PyInstaller --clean --noconfirm JARVIS.spec

Write-Host ""
Write-Host "Portable build created at: $PSScriptRoot\dist\JARVIS"
Write-Host "To create the installer, open installer\JARVIS.iss in Inno Setup."