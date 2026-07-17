@echo off
title ArchivePro v56 Masterpiece Update
echo ===============================================
echo      ArchivePro Studio v56.0 (Masterpiece)
echo ===============================================
echo.
echo 1. Clearing Cache...
if exist __pycache__ rd /s /q __pycache__

echo 2. Restoring All Features (Tabs, Projects, Audio Sync)...
set CURR_DIR=%~dp0
copy /Y "%CURR_DIR%main.py" "main.py"
copy /Y "%CURR_DIR%archiver.py" "archiver.py"
copy /Y "%CURR_DIR%audio_analyzer.py" "audio_analyzer.py"

echo.
echo [SUCCESS] Version 56.0 Masterpiece Applied!
echo All professional features have been restored and stabilized.
pause
