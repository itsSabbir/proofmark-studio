#!/usr/bin/env powershell
# Proofmark Studio: run preflight checks + app launcher
# Usage: .\run.ps1

$scriptPath = Join-Path $PSScriptRoot "scripts\launch-local.ps1"
& $scriptPath start @args
exit $LASTEXITCODE

