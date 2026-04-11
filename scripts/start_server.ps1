$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

if (-not (Test-Path '.env')) {
    Write-Error 'Missing .env. Copy .env.example to .env first.'
}

docker compose up -d
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

docker compose ps
exit $LASTEXITCODE
