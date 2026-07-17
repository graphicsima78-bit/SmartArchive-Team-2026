@echo off
title ArchivePro v58 Intelligence Restored
echo ===============================================
echo      ArchivePro Studio v58.0 (AI + Vectors)
echo ===============================================
echo.
echo 1. Cleaning Python Cache...
if exist __pycache__ rd /s /q __pycache__

echo 2. Restoring Vector Intelligence and AI Options...
set CURR_DIR=%~dp0
copy /Y "%CURR_DIR%main.py" "main.py"
copy /Y "%CURR_DIR%archiver.py" "archiver.py"
copy /Y "%CURR_DIR%audio_analyzer.py" "audio_analyzer.py"

echo.
echo [DONE] Version 58.0 Applied! (Intelligence Active)
pause
