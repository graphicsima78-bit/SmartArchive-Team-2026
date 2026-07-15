@echo off
title ArchivePro v43 UI Stability Update
echo ===============================================
echo      ArchivePro Studio v43.0 (Media Restore)
echo ===============================================
echo.
echo Restoring Audio/Video Tab and Fixing UI Layout...
set CURR_DIR=%~dp0
copy /Y "%CURR_DIR%main.py" "main.py"
copy /Y "%CURR_DIR%archiver.py" "archiver.py"
copy /Y "%CURR_DIR%audio_analyzer.py" "audio_analyzer.py"
echo.
echo [DONE] Version 43.0 Applied! (UI is now stable)
pause
