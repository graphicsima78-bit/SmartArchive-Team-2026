@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Install_AutoSync.ps1"
echo.
pause
endlocal
