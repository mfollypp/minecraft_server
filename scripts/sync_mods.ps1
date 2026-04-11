$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

if (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3 scripts/sync_mods.py
    exit $LASTEXITCODE
}

if (Get-Command python -ErrorAction SilentlyContinue) {
    & python scripts/sync_mods.py
    exit $LASTEXITCODE
}

if (Get-Command python3 -ErrorAction SilentlyContinue) {
    & python3 scripts/sync_mods.py
    exit $LASTEXITCODE
}

Write-Error 'Python 3 was not found. Install Python and ensure py, python, or python3 is available.'
