$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

$uiPort = if ($env:SOFIA_UI_PORT) { [int]$env:SOFIA_UI_PORT } else { 5174 }
$apiPort = if ($env:SOFIA_API_PORT) { [int]$env:SOFIA_API_PORT } else { 8787 }
$uiHost = if ($env:SOFIA_UI_BIND_HOST) { $env:SOFIA_UI_BIND_HOST } else { "0.0.0.0" }
$apiHost = if ($env:SOFIA_API_BIND_HOST) { $env:SOFIA_API_BIND_HOST } else { "0.0.0.0" }
$url = "http://127.0.0.1:$uiPort/"
$frontendCommand = "exec vite --host $uiHost --port $uiPort"
$projectMarker = [regex]::Escape($projectRoot)
$existing = Get-NetTCPConnection -LocalPort $uiPort -State Listen -ErrorAction SilentlyContinue
$apiExisting = @(Get-NetTCPConnection -LocalPort $apiPort -State Listen -ErrorAction SilentlyContinue)

if ($existing) {
  $viteProcess = Get-CimInstance Win32_Process -Filter "ProcessId = $($existing.OwningProcess)" -ErrorAction SilentlyContinue
  if (-not $viteProcess -or $viteProcess.CommandLine -notmatch $projectMarker -or $viteProcess.CommandLine -notmatch "--host $([regex]::Escape($uiHost))") {
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
    if ($process -and $process.CommandLine -match 'api\.server:app' -and $process.CommandLine -match "--port $apiPort") {
      [pscustomobject]@{
        Id = [int]$connection.OwningProcess
        CommandLine = [string]$process.CommandLine
        ExecutablePath = [string]$process.ExecutablePath
      }
    }
  }
)
$apiKeeper = $apiProcesses | Where-Object {
  $_.CommandLine -match "--host $([regex]::Escape($apiHost))"
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
$apiExisting = @(Get-NetTCPConnection -LocalPort $apiPort -State Listen -ErrorAction SilentlyContinue)

if ($apiExisting) {
  $apiProcess = Get-CimInstance Win32_Process -Filter "ProcessId = $($apiExisting.OwningProcess)" -ErrorAction SilentlyContinue
  if (-not $apiProcess -or $apiProcess.CommandLine -notmatch "--host $([regex]::Escape($apiHost))") {
    Stop-Process -Id $apiExisting.OwningProcess -Force -ErrorAction SilentlyContinue
    Start-Sleep -Milliseconds 500
    $apiExisting = $null
  }
}

if ($apiExisting) {
  try {
    $apiHealth = Invoke-RestMethod -Uri "http://127.0.0.1:$apiPort/api/health" -TimeoutSec 1
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
  Start-Process -FilePath "$projectRoot\.venv\Scripts\python.exe" -ArgumentList "-m uvicorn api.server:app --host $apiHost --port $apiPort" -WorkingDirectory $projectRoot -WindowStyle Hidden
}

for ($attempt = 0; $attempt -lt 30; $attempt++) {
  try {
    $health = Invoke-WebRequest -Uri "http://127.0.0.1:$apiPort/api/health" -UseBasicParsing -TimeoutSec 1
    if ($health.StatusCode -eq 200) { break }
  } catch {
    Start-Sleep -Milliseconds 250
  }
}

Start-Process $url
$lanAddresses = @(
  Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
    Where-Object { $_.IPAddress -notmatch '^127\.' -and $_.IPAddress -notmatch '^169\.254\.' } |
    Select-Object -ExpandProperty IPAddress -Unique
)
Write-Host "S.O.F.I.A. local disponível em $url"
if ($uiHost -eq '0.0.0.0' -or $apiHost -eq '0.0.0.0') {
  if ($lanAddresses.Count -gt 0) {
    foreach ($address in $lanAddresses) {
      Write-Host "Rede interna: http://${address}:$uiPort/ (API: http://${address}:$apiPort)"
    }
  } else {
    Write-Warning "O serviço está escutando na rede, mas nenhum endereço IPv4 interno foi detectado."
  }
}
Write-Host "Se outro computador não acessar, execute .\allow-network.ps1 em PowerShell como Administrador na rede Private."
