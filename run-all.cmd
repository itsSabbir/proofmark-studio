@echo off
REM run-all.cmd — boot hub + sibling apps (ProofMark PDF + Text Inspection).
REM Thin wrapper around scripts\launch-all.ps1. Ctrl+C cleans everything up.

pwsh -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\launch-all.ps1" %*
