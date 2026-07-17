@echo off
title ArchivePro Media Edition Installer
echo ===============================================
echo      ArchivePro Studio (Audio & Video Only)
echo ===============================================
echo.
echo 1. Cleaning Python Cache...
if exist __pycache__ rd /s /q __pycache__

echo 2. Installing Specialized Media Engine...
set CURR_DIR=%~dp0
copy /Y "%CURR_DIR%media_main.py" "media_main.py"
copy /Y "%CURR_DIR%media_archiver.py" "media_archiver.py"
copy /Y "%CURR_DIR%audio_analyzer.py" "audio_analyzer.py"

echo.
echo [DONE] Media Edition Applied! 
echo To run this specific tool, execute: python media_main.py
pause
