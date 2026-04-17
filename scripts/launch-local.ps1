param(
    [ValidateSet("start", "stop", "status", "restart", "logs", "test")]
    [string]$Command = "start",
    [Nullable[int]]$Port = $null,
    [switch]$SkipChecks,
    [switch]$NoBrowser,
    [switch]$OpenBrowser,
    [switch]$Detached
)

$ErrorActionPreference = "Stop"

$script:PortWasSpecified = $PSBoundParameters.ContainsKey("Port")
$script:DefaultPort = 8020
$script:PortSearchLimit = 25

$RepoRoot = Split-Path -Parent $PSScriptRoot
$RuntimeDir = Join-Path $RepoRoot ".runtime"
$PidFile = Join-Path $RuntimeDir "proofmark-studio.pid"
$PortFile = Join-Path $RuntimeDir "proofmark-studio.port"
$StdoutLog = Join-Path $RuntimeDir "proofmark-studio.stdout.log"
$StderrLog = Join-Path $RuntimeDir "proofmark-studio.stderr.log"

New-Item -ItemType Directory -Path $RuntimeDir -Force | Out-Null

function Get-AppUrl {
    param([Parameter(Mandatory = $true)][int]$Port)
    return "http://127.0.0.1:$Port"
}

function Get-HealthUrl {
    param([Parameter(Mandatory = $true)][int]$Port)
    return "$(Get-AppUrl -Port $Port)/api/health"
}

function Get-TrackedPort {
    if (-not (Test-Path $PortFile)) { return $null }
    $rawPort = Get-Content -Path $PortFile -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $rawPort) { return $null }
    try { return [int]$rawPort } catch { return $null }
}

function Get-TrackedProcess {
    if (-not (Test-Path $PidFile)) { return $null }
    $rawPid = Get-Content -Path $PidFile -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $rawPid) { return $null }
    try { return Get-Process -Id ([int]$rawPid) -ErrorAction Stop } catch { return $null }
}

function Set-TrackedState {
    param(
        [Parameter(Mandatory = $true)][int]$Port,
        [Parameter(Mandatory = $true)][int]$LauncherProcessId
    )
    Set-Content -Path $PortFile -Value $Port
    Set-Content -Path $PidFile -Value $LauncherProcessId
}

function Set-TrackedPortOnly {
    param([Parameter(Mandatory = $true)][int]$Port)
    Set-Content -Path $PortFile -Value $Port
    Remove-Item -Path $PidFile -ErrorAction SilentlyContinue
}

function Clear-TrackedState {
    Remove-Item -Path $PidFile, $PortFile -ErrorAction SilentlyContinue
}

function Resolve-RequestedPort {
    if ($script:PortWasSpecified -and $Port) { return [int]$Port }
    $trackedPort = Get-TrackedPort
    if ($trackedPort) { return $trackedPort }
    return $script:DefaultPort
}

function Get-PythonExecutable {
    $venvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"
    if (Test-Path $venvPython) { return $venvPython }
    return (Get-Command python -ErrorAction Stop).Source
}

function Get-ListeningProcessId {
    param([Parameter(Mandatory = $true)][int]$Port)
    $escapedPort = [regex]::Escape(":$Port")
    $pattern = "^\s*TCP\s+\S+$escapedPort\s+\S+\s+LISTENING\s+(\d+)\s*$"
    $line = netstat -ano -p tcp | Select-String -Pattern $pattern | Select-Object -First 1
    if (-not $line) { return $null }
    $match = [regex]::Match($line.Line, $pattern)
    if (-not $match.Success) { return $null }
    return [int]$match.Groups[1].Value
}

function Get-ProcessSummary {
    param([Nullable[int]]$ProcessId = $null)
    if (-not $ProcessId) { return $null }
    try {
        $process = Get-Process -Id $ProcessId -ErrorAction Stop
        return "$($process.ProcessName) (PID $ProcessId)"
    }
    catch {
        return "PID $ProcessId"
    }
}

function Find-OpenPort {
    param([Parameter(Mandatory = $true)][int]$StartPort)
    for ($candidate = $StartPort; $candidate -lt ($StartPort + $script:PortSearchLimit); $candidate++) {
        if (-not (Get-ListeningProcessId -Port $candidate)) { return $candidate }
    }
    return $null
}

function Test-AppHealthy {
    param([Parameter(Mandatory = $true)][int]$Port)
    try {
        $response = Invoke-RestMethod -Uri (Get-HealthUrl -Port $Port) -Method Get -TimeoutSec 2
        return $response.status -eq "ok"
    }
    catch {
        return $false
    }
}

function Stop-ProcessTree {
    param([Parameter(Mandatory = $true)][int]$TargetProcessId)
    if (-not (Get-Process -Id $TargetProcessId -ErrorAction SilentlyContinue)) { return $false }
    $null = taskkill /PID $TargetProcessId /T /F 2>$null
    Start-Sleep -Milliseconds 400
    if (Get-Process -Id $TargetProcessId -ErrorAction SilentlyContinue) {
        Stop-Process -Id $TargetProcessId -Force -ErrorAction SilentlyContinue
        Start-Sleep -Milliseconds 400
    }
    return -not (Get-Process -Id $TargetProcessId -ErrorAction SilentlyContinue)
}

function Show-Logs {
    $trackedPort = Get-TrackedPort
    if ($trackedPort) { Write-Host "url: $(Get-AppUrl -Port $trackedPort)" }
    Write-Host "stdout: $StdoutLog"
    Write-Host "stderr: $StderrLog"
}

function Invoke-Step {
    param(
        [Parameter(Mandatory = $true)][string]$Label,
        [Parameter(Mandatory = $true)][scriptblock]$Action
    )
    Write-Host $Label
    & $Action
}

function Invoke-PreflightChecks {
    Push-Location $RepoRoot
    $pythonExecutable = Get-PythonExecutable
    try {
        Invoke-Step "1/2 Import smoke..." {
            & $pythonExecutable -c "import fastapi, uvicorn, web_app"
            if ($LASTEXITCODE -ne 0) { throw "Python dependencies or app imports failed." }
        }

        Invoke-Step "2/2 Test suite..." {
            & $pythonExecutable -m pytest -q
            if ($LASTEXITCODE -ne 0) { throw "The test suite failed." }
        }
    }
    finally {
        Pop-Location
    }
}

function Open-AppInBrowser {
    param([Parameter(Mandatory = $true)][int]$Port)
    Start-Process (Get-AppUrl -Port $Port) | Out-Null
}

function Start-UvicornProcess {
    param(
        [Parameter(Mandatory = $true)][int]$Port,
        [switch]$DetachedMode
    )

    $pythonExecutable = Get-PythonExecutable
    $arguments = @("-m", "uvicorn", "web_app:app", "--host", "127.0.0.1", "--port", "$Port")
    if (-not $DetachedMode) { $arguments += "--reload" }

    if ($DetachedMode) {
        return Start-Process `
            -FilePath $pythonExecutable `
            -ArgumentList $arguments `
            -WorkingDirectory $RepoRoot `
            -RedirectStandardOutput $StdoutLog `
            -RedirectStandardError $StderrLog `
            -PassThru `
            -WindowStyle Hidden
    }

    return Start-Process `
        -FilePath $pythonExecutable `
        -ArgumentList $arguments `
        -WorkingDirectory $RepoRoot `
        -PassThru `
        -NoNewWindow
}

function Wait-ForHealthyApp {
    param(
        [Parameter(Mandatory = $true)][System.Diagnostics.Process]$Process,
        [Parameter(Mandatory = $true)][int]$Port
    )

    for ($attempt = 0; $attempt -lt 40; $attempt++) {
        Start-Sleep -Milliseconds 400
        if ($Process.HasExited) { break }
        if (Test-AppHealthy -Port $Port) { return $true }
    }

    return $false
}

function Start-AppInForeground {
    param(
        [Parameter(Mandatory = $true)][int]$Port,
        [Parameter(Mandatory = $true)][bool]$ShouldOpenBrowser
    )

    Remove-Item -Path $StdoutLog, $StderrLog -ErrorAction SilentlyContinue
    $startedProcess = Start-UvicornProcess -Port $Port
    Set-TrackedState -LauncherProcessId $startedProcess.Id -Port $Port

    try {
        if (-not (Wait-ForHealthyApp -Process $startedProcess -Port $Port)) {
            if (-not $startedProcess.HasExited) { Stop-ProcessTree -TargetProcessId $startedProcess.Id | Out-Null }
            throw "Proofmark Studio did not become healthy in time."
        }

        $listenerPid = Get-ListeningProcessId -Port $Port
        Write-Host "Proofmark Studio is running at $(Get-AppUrl -Port $Port) (launcher PID $($startedProcess.Id))."
        if ($listenerPid) { Write-Host "Active listener: $(Get-ProcessSummary -ProcessId $listenerPid)" }
        Write-Host "Reload mode is enabled. Keep this window open while you work and press Ctrl+C to stop the server."
        if ($ShouldOpenBrowser) { Open-AppInBrowser -Port $Port }

        Wait-Process -Id $startedProcess.Id
        $startedProcess.Refresh()
        return $startedProcess.ExitCode
    }
    finally {
        Clear-TrackedState
    }
}

function Start-AppDetached {
    param(
        [Parameter(Mandatory = $true)][int]$Port,
        [Parameter(Mandatory = $true)][bool]$ShouldOpenBrowser
    )

    Remove-Item -Path $StdoutLog, $StderrLog -ErrorAction SilentlyContinue
    $startedProcess = Start-UvicornProcess -Port $Port -DetachedMode
    if (-not (Wait-ForHealthyApp -Process $startedProcess -Port $Port)) {
        if (Get-Process -Id $startedProcess.Id -ErrorAction SilentlyContinue) {
            Stop-ProcessTree -TargetProcessId $startedProcess.Id | Out-Null
        }
        throw "Proofmark Studio did not become healthy in time. Check the logs in .runtime."
    }

    Set-TrackedState -LauncherProcessId $startedProcess.Id -Port $Port
    $listenerPid = Get-ListeningProcessId -Port $Port
    Write-Host "Proofmark Studio is running at $(Get-AppUrl -Port $Port) (launcher PID $($startedProcess.Id))."
    if ($listenerPid) { Write-Host "Active listener: $(Get-ProcessSummary -ProcessId $listenerPid)" }
    Show-Logs
    if ($ShouldOpenBrowser) { Open-AppInBrowser -Port $Port }
}

function Stop-App {
    $trackedPort = Get-TrackedPort
    $trackedProcess = Get-TrackedProcess
    $stoppedAnything = $false

    if ($trackedProcess) {
        Stop-ProcessTree -TargetProcessId $trackedProcess.Id | Out-Null
        Write-Host "Stopped tracked Proofmark Studio launcher (PID $($trackedProcess.Id))."
        $stoppedAnything = $true
    }

    if ($trackedPort) {
        $listenerPid = Get-ListeningProcessId -Port $trackedPort
        if ($listenerPid) {
            Stop-ProcessTree -TargetProcessId $listenerPid | Out-Null
            Write-Host "Stopped active listener on $(Get-AppUrl -Port $trackedPort) ($(Get-ProcessSummary -ProcessId $listenerPid))."
            $stoppedAnything = $true
        }
    }

    Clear-TrackedState

    if ($stoppedAnything) {
        Write-Host "Proofmark Studio is stopped."
        return
    }

    Write-Host "Proofmark Studio is not running."
}

function Show-Status {
    $trackedPort = Get-TrackedPort
    $trackedProcess = Get-TrackedProcess
    $activePort = if ($trackedPort) { $trackedPort } else { Resolve-RequestedPort }

    if ($activePort -and (Test-AppHealthy -Port $activePort)) {
        if ($trackedProcess) {
            Write-Host "Proofmark Studio is running at $(Get-AppUrl -Port $activePort) (launcher PID $($trackedProcess.Id))."
        }
        else {
            Write-Host "Proofmark Studio responds at $(Get-AppUrl -Port $activePort) from an existing process."
        }
        $listenerPid = Get-ListeningProcessId -Port $activePort
        if ($listenerPid) { Write-Host "Active listener: $(Get-ProcessSummary -ProcessId $listenerPid)" }
        Show-Logs
        return
    }

    if ($trackedProcess) {
        Write-Host "Tracked launcher process $($trackedProcess.Id) exists, but the health check failed."
        Show-Logs
        return
    }

    Write-Host "Proofmark Studio is stopped."
    Show-Logs
}

function Start-App {
    $shouldOpenBrowser = $OpenBrowser -or (-not $NoBrowser)
    $runDetached = [bool]$Detached
    $trackedPort = Get-TrackedPort
    $trackedProcess = Get-TrackedProcess

    if (-not $runDetached) {
        if ($trackedProcess -or ($trackedPort -and (Test-AppHealthy -Port $trackedPort))) {
            Write-Host "Stopping the current Proofmark Studio instance before starting a fresh attached session..."
            Stop-App
        }
    }

    $preferredPort = Resolve-RequestedPort

    if ($trackedPort -and (Test-AppHealthy -Port $trackedPort)) {
        Write-Host "Proofmark Studio is already running at $(Get-AppUrl -Port $trackedPort)."
        Show-Logs
        if ($shouldOpenBrowser) { Open-AppInBrowser -Port $trackedPort }
        return
    }

    if (-not $runDetached -and (Test-AppHealthy -Port $preferredPort)) {
        $listenerPid = Get-ListeningProcessId -Port $preferredPort
        if ($listenerPid) {
            Write-Host "Stopping the existing Proofmark Studio listener on $(Get-AppUrl -Port $preferredPort) so the fresh launch uses the latest files..."
            Stop-ProcessTree -TargetProcessId $listenerPid | Out-Null
            Start-Sleep -Milliseconds 400
        }
        Clear-TrackedState
    }

    if (Test-AppHealthy -Port $preferredPort) {
        $listenerPid = Get-ListeningProcessId -Port $preferredPort
        Set-TrackedPortOnly -Port $preferredPort
        Write-Host "Proofmark Studio already responds at $(Get-AppUrl -Port $preferredPort) from an existing process" -NoNewline
        if ($listenerPid) {
            Write-Host " ($(Get-ProcessSummary -ProcessId $listenerPid))."
        }
        else {
            Write-Host "."
        }
        Show-Logs
        if ($shouldOpenBrowser) { Open-AppInBrowser -Port $preferredPort }
        return
    }

    $selectedPort = Find-OpenPort -StartPort $preferredPort
    if (-not $selectedPort) {
        $lastCandidate = $preferredPort + $script:PortSearchLimit - 1
        throw "Could not find an open port between $preferredPort and $lastCandidate."
    }

    if ($selectedPort -ne $preferredPort) {
        $busyProcessId = Get-ListeningProcessId -Port $preferredPort
        Write-Host "Port $preferredPort is already in use by $(Get-ProcessSummary -ProcessId $busyProcessId)."
        Write-Host "Starting Proofmark Studio on $(Get-AppUrl -Port $selectedPort) instead."
    }

    if (-not $SkipChecks) { Invoke-PreflightChecks }

    if ($runDetached) {
        Start-AppDetached -Port $selectedPort -ShouldOpenBrowser:$shouldOpenBrowser
        return
    }

    $exitCode = Start-AppInForeground -Port $selectedPort -ShouldOpenBrowser:$shouldOpenBrowser
    if ($exitCode -and $exitCode -ne 0) { throw "Proofmark Studio exited with code $exitCode." }
}

switch ($Command) {
    "start" { Start-App }
    "stop" { Stop-App }
    "status" { Show-Status }
    "restart" {
        Stop-App
        Start-App
    }
    "logs" { Show-Logs }
    "test" { Invoke-PreflightChecks }
}
