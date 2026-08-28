$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

$port = 5174
$url = "http://127.0.0.1:$port/"
$existing = Get-NetTCPConnection -LocalAddress 127.0.0.1 -LocalPort $port -State Listen -ErrorAction SilentlyContinue
$apiExisting = Get-NetTCPConnection -LocalAddress 127.0.0.1 -LocalPort 8787 -State Listen -ErrorAction SilentlyContinue

if (-not $existing) {
  Start-Process -FilePath "pnpm.cmd" -ArgumentList "dev:local" -WorkingDirectory $projectRoot -WindowStyle Hidden
  Start-Sleep -Seconds 2
}

if (-not $apiExisting) {
  Start-Process -FilePath "$projectRoot\.venv\Scripts\python.exe" -ArgumentList "-m api.server" -WorkingDirectory $projectRoot -WindowStyle Hidden
  Start-Sleep -Seconds 2
}

Start-Process $url
Write-Host "Orbit AI disponível em $url"
