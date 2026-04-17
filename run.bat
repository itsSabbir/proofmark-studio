@echo off
setlocal
pwsh -ExecutionPolicy Bypass -NoLogo -NoProfile -File "%~dp0scripts\launch-local.ps1" start %*
exit /b %ERRORLEVEL%

