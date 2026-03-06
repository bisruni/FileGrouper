$ErrorActionPreference = "Stop"

$RootDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $RootDir

python -m pip install --quiet --upgrade pip
python -m pip install --quiet -r requirements-release.txt

if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
Get-ChildItem -Path "." -Filter "*.egg-info" | Remove-Item -Recurse -Force

python -m build --sdist --wheel .
python -m twine check dist/*

Write-Host "[release] distribution artifacts created under dist/"
