$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

$port = 5174
$url = "http://127.0.0.1:$port/"
$frontendCommand = "dev:network"
$apiHost = "0.0.0.0"
$expectedPython = [string](Resolve-Path "$projectRoot\.venv\Scripts\python.exe")
$projectMarker = [regex]::Escape($projectRoot)
$existing = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
$apiExisting = @(Get-NetTCPConnection -LocalPort 8787 -State Listen -ErrorAction SilentlyContinue)

if ($existing) {
  $viteProcess = Get-CimInstance Win32_Process -Filter "ProcessId = $($existing.OwningProcess)" -ErrorAction SilentlyContinue
  if (-not $viteProcess -or $viteProcess.CommandLine -notmatch $projectMarker -or $viteProcess.CommandLine -notmatch '--host 0.0.0.0') {
    Stop-Process -Id $existing.OwningProcess -Force -ErrorAction SilentlyContinue
    Start-Sleep -Milliseconds 500
    $existing = $null
  }
}

# Keep a single project API listener. On Windows the virtual-environment
# launcher and its child interpreter can both remain visible after repeated
# starts, making the browser appear to switch between API instances.
$apiProcesses = @(
  foreach ($connection in $apiExisting) {
    $process = Get-CimInstance Win32_Process -Filter "ProcessId = $($connection.OwningProcess)" -ErrorAction SilentlyContinue
    if ($process -and $process.CommandLine -match $projectMarker -and $process.CommandLine -match 'api\.server:app') {
      [pscustomobject]@{
        Id = [int]$connection.OwningProcess
        CommandLine = [string]$process.CommandLine
        ExecutablePath = [string]$process.ExecutablePath
      }
    }
  }
)
$apiKeeper = $apiProcesses | Where-Object {
  $_.CommandLine -match '--host 0\.0\.0\.0' -and $_.ExecutablePath -eq $expectedPython
} | Select-Object -First 1
foreach ($duplicate in @($apiProcesses | Where-Object { $apiKeeper -and $_.Id -ne $apiKeeper.Id })) {
  Stop-Process -Id $duplicate.Id -Force -ErrorAction SilentlyContinue
  Start-Sleep -Milliseconds 300
}
$staleApiProcesses = @($apiProcesses | Where-Object { -not $apiKeeper -or $_.Id -ne $apiKeeper.Id })
foreach ($stale in $staleApiProcesses) {
  Stop-Process -Id $stale.Id -Force -ErrorAction SilentlyContinue
  Start-Sleep -Milliseconds 300
}
$apiExisting = @(Get-NetTCPConnection -LocalPort 8787 -State Listen -ErrorAction SilentlyContinue)

if ($apiExisting) {
  $apiProcess = Get-CimInstance Win32_Process -Filter "ProcessId = $($apiExisting.OwningProcess)" -ErrorAction SilentlyContinue
  if (-not $apiProcess -or $apiProcess.CommandLine -notmatch '--host 0.0.0.0' -or [string]$apiProcess.ExecutablePath -ne $expectedPython) {
    Stop-Process -Id $apiExisting.OwningProcess -Force -ErrorAction SilentlyContinue
    Start-Sleep -Milliseconds 500
    $apiExisting = $null
  }
}

if ($apiExisting) {
  try {
    $apiHealth = Invoke-RestMethod -Uri "http://127.0.0.1:8787/api/health" -TimeoutSec 1
    $expectedKnowledge = Join-Path $projectRoot 'knowledge'
    if ($apiHealth.knowledge -ne $expectedKnowledge) {
      Stop-Process -Id $apiExisting.OwningProcess -Force -ErrorAction SilentlyContinue
      Start-Sleep -Milliseconds 500
      $apiExisting = $null
    }
  } catch {
    Stop-Process -Id $apiExisting.OwningProcess -Force -ErrorAction SilentlyContinue
    Start-Sleep -Milliseconds 500
    $apiExisting = $null
  }
}

if (-not $existing) {
  Start-Process -FilePath "pnpm.cmd" -ArgumentList $frontendCommand -WorkingDirectory $projectRoot -WindowStyle Hidden
  Start-Sleep -Seconds 2
}

if (-not $apiExisting) {
  Start-Process -FilePath "$projectRoot\.venv\Scripts\python.exe" -ArgumentList "-m uvicorn api.server:app --host $apiHost --port 8787" -WorkingDirectory $projectRoot -WindowStyle Hidden
}

for ($attempt = 0; $attempt -lt 30; $attempt++) {
  try {
    $health = Invoke-WebRequest -Uri "http://127.0.0.1:8787/api/health" -UseBasicParsing -TimeoutSec 1
    if ($health.StatusCode -eq 200) { break }
  } catch {
    Start-Sleep -Milliseconds 250
  }
}

Start-Process $url
Write-Host "S.O.F.I.A. disponível em $url"
