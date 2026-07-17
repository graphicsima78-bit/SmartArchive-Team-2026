@echo off
title ArchivePro v42 Audio Intelligence
echo ===============================================
echo      ArchivePro Studio v42.0 (Logic Fix)
echo ===============================================
echo.
echo Improving Audio Classification and Folder Logic...
set CURR_DIR=%~dp0
copy /Y "%CURR_DIR%audio_analyzer.py" "audio_analyzer.py"
copy /Y "%CURR_DIR%archiver.py" "archiver.py"
copy /Y "%CURR_DIR%main.py" "main.py"
echo.
echo [DONE] Version 42.0 Applied! (Audio Mistake Fixed)
pause
