@echo off
setlocal
schtasks /End /TN "SmartArchive-AutoSync" >nul 2>&1
schtasks /Delete /TN "SmartArchive-AutoSync" /F
pause
endlocal
