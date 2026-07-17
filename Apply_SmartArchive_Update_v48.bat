@echo off
title ArchivePro v48 Clean Update
echo ===============================================
echo      ArchivePro Studio v48.0 (No Numbers)
echo ===============================================
echo.
echo Cleaning filenames and stabilizing exit...
set CURR_DIR=%~dp0
copy /Y "%CURR_DIR%main.py" "main.py"
copy /Y "%CURR_DIR%archiver.py" "archiver.py"
copy /Y "%CURR_DIR%audio_analyzer.py" "audio_analyzer.py"
echo.
echo [DONE] Version 48.0 Applied! (Clean & Stable)
pause
