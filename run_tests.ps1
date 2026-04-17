#!/usr/bin/env powershell
# Proofmark Studio test runner

$scriptPath = Join-Path $PSScriptRoot "scripts\launch-local.ps1"
& $scriptPath test @args
exit $LASTEXITCODE

