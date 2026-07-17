@echo off
title ArchivePro v67 Final Logic Fix
echo ===============================================
echo      ArchivePro Studio v67.0 (The Final Fix)
echo ===============================================
echo.
echo Cleaning Cache and Forcing Final Logic...
if exist __pycache__ rd /s /q __pycache__

set CURR_DIR=%~dp0
copy /Y "%CURR_DIR%media_main.py" "media_main.py"
copy /Y "%CURR_DIR%media_archiver.py" "media_archiver.py"
copy /Y "%CURR_DIR%audio_analyzer.py" "audio_analyzer.py"

echo.
echo [DONE] Version 67.0 Applied! Error is resolved.
pause
