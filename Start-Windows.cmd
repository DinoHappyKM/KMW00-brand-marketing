@echo off
setlocal
rem Local user launcher. ExecutionPolicy Bypass is process-only.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Install-Windows-Interactive.ps1"
set "KMW00_EXIT=%ERRORLEVEL%"
exit /b %KMW00_EXIT%
