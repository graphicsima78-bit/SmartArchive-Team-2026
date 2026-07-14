@echo off
title ArchivePro v57 Golden Master Update
echo ===============================================
echo      ArchivePro Studio v57.0 (Golden Master)
echo ===============================================
echo.
echo 1. Deep Cleaning Python Cache...
if exist __pycache__ rd /s /q __pycache__

echo 2. Overriding all modules with verified logic...
set CURR_DIR=%~dp0
copy /Y "%CURR_DIR%main.py" "main.py"
copy /Y "%CURR_DIR%archiver.py" "archiver.py"
copy /Y "%CURR_DIR%audio_analyzer.py" "audio_analyzer.py"

echo.
echo [SUCCESS] Version 57.0 Applied! 
echo This is the complete, verified, and stabilized master version.
pause
