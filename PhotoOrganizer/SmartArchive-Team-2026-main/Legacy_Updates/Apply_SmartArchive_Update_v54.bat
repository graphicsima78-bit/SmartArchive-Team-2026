@echo off
title ArchivePro v54 Master Sync Update
echo ===============================================
echo      ArchivePro Studio v54.0 (Final Master)
echo ===============================================
echo.
echo 1. Wiping Python Cache...
if exist __pycache__ rd /s /q __pycache__

echo 2. Forcing New Logic Sync (Artist-Rename Active)...
set CURR_DIR=%~dp0
copy /Y "%CURR_DIR%main.py" "main.py"
copy /Y "%CURR_DIR%archiver.py" "archiver.py"
copy /Y "%CURR_DIR%audio_analyzer.py" "audio_analyzer.py"

echo.
echo [SUCCESS] Version 54.0 Applied! 
echo All folders will now sync with your language choice.
pause
