# launch-all.ps1 — start hub + sibling apps together.
#
# Usage:
#   pwsh -File scripts/launch-all.ps1 start    # default; boot all 3
#   pwsh -File scripts/launch-all.ps1 stop     # stop all 3
#   pwsh -File scripts/launch-all.ps1 status   # health-check each app
#
# Architecture: three independent FastAPI processes on distinct ports.
# Hub sets PROOFMARK_HUB_URL so siblings render the "← ProofMark Studio" link.
# Siblings stay launchable standalone (just run `python web_app.py` in their folders).

param(
  [ValidateSet('start', 'stop', 'status', 'restart')]
  [string] $Command = 'start'
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

$StudioRoot = Split-Path -Parent $PSScriptRoot
$ToolsRoot  = Split-Path -Parent $StudioRoot
$Runtime    = Join-Path $StudioRoot '.runtime'
New-Item -ItemType Directory -Force -Path $Runtime | Out-Null

$HubUrl = 'http://127.0.0.1:8020'

$APPS = @(
  @{
    name   = 'hub'
    dir    = $StudioRoot
    venv   = Join-Path $StudioRoot '.venv\Scripts\python.exe'
    script = 'web_app.py'
    port   = 8020
    health = '/api/health'
  },
  @{
    name   = 'pdf'
    dir    = Join-Path $ToolsRoot 'proofmark-pdf'
    venv   = Join-Path $ToolsRoot 'proofmark-pdf\.venv\Scripts\python.exe'
    script = 'web_app.py'
    port   = 8010
    health = '/api/health'
  },
  @{
    name   = 'text'
    dir    = Join-Path $ToolsRoot 'text-cleaner'
    venv   = Join-Path $ToolsRoot 'text-cleaner\.venv\Scripts\python.exe'
    script = 'web_app.py'
    port   = 8000
    health = '/api/health'
  }
)

function Get-AppPidFile($app)    { Join-Path $Runtime "$($app.name).pid" }
function Get-AppStdoutFile($app) { Join-Path $Runtime "$($app.name).stdout.log" }
function Get-AppStderrFile($app) { Join-Path $Runtime "$($app.name).stderr.log" }

function Test-AppHealth($app) {
  try {
    $r = Invoke-WebRequest -Uri "http://127.0.0.1:$($app.port)$($app.health)" `
           -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
    return $r.StatusCode -eq 200
  } catch {
    return $false
  }
}

function Wait-AppReady($app, [int]$timeoutSec = 20) {
  $deadline = (Get-Date).AddSeconds($timeoutSec)
  while ((Get-Date) -lt $deadline) {
    if (Test-AppHealth $app) { return $true }
    Start-Sleep -Milliseconds 400
  }
  return $false
}

function Start-App($app) {
  # Preflight: kill any stale process of ours, then kill anything already on the port.
  Stop-App $app | Out-Null
  $existing = Get-NetTCPConnection -LocalPort $app.port -State Listen -ErrorAction SilentlyContinue
  foreach ($c in $existing) { Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue }

  if (-not (Test-Path $app.venv)) {
    Write-Host "  [$($app.name)] venv missing at $($app.venv)" -ForegroundColor Red
    return $null
  }

  # Hub launches WITHOUT PROOFMARK_HUB_URL (it IS the hub); siblings get it set.
  $prev = $env:PROOFMARK_HUB_URL
  if ($app.name -eq 'hub') { $env:PROOFMARK_HUB_URL = $null } else { $env:PROOFMARK_HUB_URL = $HubUrl }

  $p = Start-Process -FilePath $app.venv `
        -ArgumentList $app.script `
        -WorkingDirectory $app.dir `
        -RedirectStandardOutput (Get-AppStdoutFile $app) `
        -RedirectStandardError  (Get-AppStderrFile $app) `
        -PassThru -WindowStyle Hidden

  $env:PROOFMARK_HUB_URL = $prev
  $p.Id | Out-File -FilePath (Get-AppPidFile $app) -Encoding ascii
  return $p
}

function Stop-App($app) {
  $pidFile = Get-AppPidFile $app
  if (Test-Path $pidFile) {
    $pidVal = Get-Content $pidFile -Raw -ErrorAction SilentlyContinue
    if ($pidVal -match '^\s*(\d+)\s*$') {
      $procId = [int]$Matches[1]
      try { Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue } catch {}
    }
    Remove-Item $pidFile -ErrorAction SilentlyContinue
  }
  # Belt-and-suspenders: if something's still on the port, kill it.
  $conns = Get-NetTCPConnection -LocalPort $app.port -State Listen -ErrorAction SilentlyContinue
  foreach ($c in $conns) {
    try { Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue } catch {}
  }
}

function Show-Status {
  Write-Host ""
  foreach ($app in $APPS) {
    $health = Test-AppHealth $app
    if ($health) {
      Write-Host ("  [{0,-4}] :{1}  READY" -f $app.name, $app.port) -ForegroundColor Green
    } else {
      Write-Host ("  [{0,-4}] :{1}  DOWN"  -f $app.name, $app.port) -ForegroundColor DarkGray
    }
  }
  Write-Host ""
}

# ─── Command dispatch ───────────────────────────────────────────────────

if ($Command -eq 'stop') {
  foreach ($app in $APPS) { Stop-App $app; Write-Host "stopped $($app.name)" }
  exit 0
}

if ($Command -eq 'status') {
  Show-Status
  exit 0
}

if ($Command -eq 'restart') {
  foreach ($app in $APPS) { Stop-App $app }
  Start-Sleep -Seconds 1
  # fall through to start
}

# start
Write-Host ""
Write-Host "ProofMark Studio — starting hub + siblings" -ForegroundColor Cyan
Write-Host "  hub  :8020   (proofmark-studio)"
Write-Host "  pdf  :8010   (proofmark-pdf)"
Write-Host "  text :8000   (text-cleaner)"
Write-Host ""

$procs = @{}
foreach ($app in $APPS) {
  Write-Host "starting $($app.name)..."
  $procs[$app.name] = Start-App $app
}

Write-Host ""
Write-Host "health-polling..."
$allUp = $true
foreach ($app in $APPS) {
  $up = Wait-AppReady $app
  if ($up) {
    Write-Host ("  [{0,-4}] :{1}  READY" -f $app.name, $app.port) -ForegroundColor Green
  } else {
    Write-Host ("  [{0,-4}] :{1}  FAILED - see $($Runtime)\$($app.name).stderr.log" -f $app.name, $app.port) -ForegroundColor Red
    $allUp = $false
  }
}

if (-not $allUp) {
  Write-Host ""
  Write-Host "one or more apps failed to start. use 'scripts/launch-all.ps1 stop' to clean up." -ForegroundColor Red
  exit 1
}

Write-Host ""
Write-Host "all systems go. opening $HubUrl in your browser..." -ForegroundColor Cyan
Start-Process $HubUrl
Write-Host ""
Write-Host "press Ctrl+C to stop all three." -ForegroundColor DarkGray

try {
  while ($true) { Start-Sleep -Seconds 3 }
} finally {
  Write-Host ""
  Write-Host "shutting down..."
  foreach ($app in $APPS) { Stop-App $app }
  Write-Host "done." -ForegroundColor Cyan
}
