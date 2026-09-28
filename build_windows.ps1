$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

# ---- preflight -------------------------------------------------------
foreach ($f in "launcher.py","main.py","jarvis_gui.py","desktop_bot.py","bot.png","JARVIS.ico","JARVIS.spec") {
    if (-not (Test-Path $f)) { throw "Missing required file: $f" }
}
if ((Get-Item "bot.png").Length -eq 0) { throw "bot.png is empty (0 bytes)." }

# ---- environment -----------------------------------------------------
if (-not (Test-Path ".venv\Scripts\python.exe")) { py -3.12 -m venv .venv }
$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) { throw "Python 3.12 is required." }

Remove-Item -Recurse -Force -ErrorAction SilentlyContinue build, dist
& $python -m pip install --upgrade pip
# Prefer a pinned lock file if you have one (pip freeze > requirements-lock.txt)
if (Test-Path "requirements-lock.txt") {
    & $python -m pip install -r requirements-lock.txt
} else {
    & $python -m pip install -r requirements-desktop.txt
}
& $python -m pip install pyinstaller
& $python -m PyInstaller --clean --noconfirm JARVIS.spec
if (-not (Test-Path "dist\JARVIS\JARVIS.exe")) { throw "PyInstaller build failed." }
Write-Host "`nApp folder: $PSScriptRoot\dist\JARVIS"

# ---- installer (Inno Setup) ------------------------------------------
$iscc = @(
    "$env:ProgramFiles(x86)\Inno Setup 6\ISCC.exe",
    "$env:ProgramFiles\Inno Setup 6\ISCC.exe",
    "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe"
) | Where-Object { Test-Path $_ } | Select-Object -First 1

if ($iscc) {
    & $iscc "installer\JARVIS.iss"
    Write-Host "`nInstaller: $PSScriptRoot\installer\output\JARVIS_Setup.exe"
} else {
    Write-Host "Inno Setup not found. Install it, then open installer\JARVIS.iss and press Compile."
}
