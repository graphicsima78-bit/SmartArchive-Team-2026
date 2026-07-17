@echo off
setlocal
set /p MINUTES="How many minutes between automatic saves? (example: 10): "
if "%MINUTES%"=="" set MINUTES=10
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Install_AutoSync.ps1" -IntervalMinutes %MINUTES%
pause
endlocal
