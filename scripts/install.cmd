@echo off
setlocal
chcp 65001 >nul
set "PAUSE_AT_END="
echo %cmdcmdline% | findstr /i /c:" /c " >nul && set "PAUSE_AT_END=1"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1" %*
set "EC=%ERRORLEVEL%"
if defined PAUSE_AT_END (
  echo.
  echo Press any key to close this window.
  pause >nul
)
exit /b %EC%
