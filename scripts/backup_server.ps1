$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

$timestamp = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ')
$backupDir = Join-Path $repoRoot 'backups'
$archive = Join-Path $backupDir ("world-$timestamp.zip")
$dataPath = Join-Path $repoRoot 'data'

New-Item -ItemType Directory -Force -Path $backupDir | Out-Null

$runningServices = docker compose ps --status running --services
if ($LASTEXITCODE -eq 0 -and ($runningServices -split "`r?`n") -contains 'minecraft') {
    docker compose exec -T minecraft rcon-cli save-off *> $null
    docker compose exec -T minecraft rcon-cli save-all flush *> $null
}

if (Test-Path $archive) {
    Remove-Item -Force $archive
}
Compress-Archive -Path $dataPath -DestinationPath $archive -Force

if ($LASTEXITCODE -eq 0 -and ($runningServices -split "`r?`n") -contains 'minecraft') {
    docker compose exec -T minecraft rcon-cli save-on *> $null
}

Write-Host "Backup written to $archive"
