@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Install_AutoSync.ps1" -IntervalMinutes 10
pause
endlocal
