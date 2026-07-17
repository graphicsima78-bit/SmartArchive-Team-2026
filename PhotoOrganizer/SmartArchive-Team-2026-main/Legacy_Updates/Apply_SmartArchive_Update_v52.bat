@echo off
title ArchivePro v52 Ultimate Stability
echo ===============================================
echo      ArchivePro Studio v52.0 (Final Stability)
echo ===============================================
echo.
echo Restoring Stable UI and Fixing Cross-Language Merging...
set CURR_DIR=%~dp0
copy /Y "%CURR_DIR%main.py" "main.py"
copy /Y "%CURR_DIR%archiver.py" "archiver.py"
copy /Y "%CURR_DIR%audio_analyzer.py" "audio_analyzer.py"
echo.
echo [DONE] Version 52.0 Applied! (Safe and Stable)
pause
