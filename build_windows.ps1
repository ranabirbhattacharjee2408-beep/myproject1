$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    py -3.12 -m venv .venv
}

$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    throw "Python 3.12 is required to build JARVIS."
}

Remove-Item -Recurse -Force -ErrorAction SilentlyContinue build, dist
& $python -m pip install --upgrade pip
& $python -m pip install -r requirements-desktop.txt
& $python -m pip install pyinstaller
& $python -m PyInstaller --clean --noconfirm JARVIS.spec

Write-Host ""
Write-Host "Portable build created at: $PSScriptRoot\dist\JARVIS"
Write-Host "To create the installer, open installer\JARVIS.iss in Inno Setup."