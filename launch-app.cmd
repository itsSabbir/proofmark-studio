@echo off
setlocal

if exist "%~dp0.venv\Scripts\python.exe" (
  "%~dp0.venv\Scripts\python.exe" -c "import fastapi, uvicorn" >nul 2>nul
  if not errorlevel 1 (
    "%~dp0.venv\Scripts\python.exe" "%~dp0web_app.py" --kill-port --open-browser %*
    set EXIT_CODE=%ERRORLEVEL%
    goto done
  )
)

where python >nul 2>nul
if not errorlevel 1 (
  python "%~dp0web_app.py" --kill-port --open-browser %*
  set EXIT_CODE=%ERRORLEVEL%
  goto done
)

where py >nul 2>nul
if not errorlevel 1 (
  py -3 "%~dp0web_app.py" --kill-port --open-browser %*
  set EXIT_CODE=%ERRORLEVEL%
  goto done
)

where pwsh >nul 2>nul
if not errorlevel 1 (
  if /I "%~1"=="--smoke-test" (
    pwsh -NoLogo -NoProfile -File "%~dp0scripts\launch-local.ps1" test
  ) else (
    pwsh -NoLogo -NoProfile -File "%~dp0scripts\launch-local.ps1" start
  )
  set EXIT_CODE=%ERRORLEVEL%
  goto done
)

echo.
echo Python is required to run launch-app.cmd.
echo Install Python and make sure python, py, or pwsh is on PATH.
set EXIT_CODE=1

:done
if not "%EXIT_CODE%"=="0" (
  echo.
  echo Launch failed with exit code %EXIT_CODE%.
  echo Press any key to close this window.
  pause >nul
)

exit /b %EXIT_CODE%

