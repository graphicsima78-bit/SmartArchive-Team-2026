@echo off
title ArchivePro v46 Final Integration
echo ===============================================
echo      ArchivePro Studio v46.0 (The Final One)
echo ===============================================
echo.
echo Restoring Audio Logic, Supreme Taxonomy, and UI Stability...
set CURR_DIR=%~dp0
copy /Y "%CURR_DIR%audio_analyzer.py" "audio_analyzer.py"
copy /Y "%CURR_DIR%archiver.py" "archiver.py"
copy /Y "%CURR_DIR%main.py" "main.py"
echo.
echo [DONE] Version 46.0 Applied! (All systems integrated and fixed)
pause
