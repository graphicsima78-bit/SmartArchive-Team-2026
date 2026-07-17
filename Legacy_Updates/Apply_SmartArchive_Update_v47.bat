@echo off
title ArchivePro v47 Bulletproof Update
echo ===============================================
echo      ArchivePro Studio v47.0 (No-Crash UI)
echo ===============================================
echo.
echo Locking UI layout and stabilizing engine...
set CURR_DIR=%~dp0
copy /Y "%CURR_DIR%main.py" "main.py"
copy /Y "%CURR_DIR%archiver.py" "archiver.py"
copy /Y "%CURR_DIR%audio_analyzer.py" "audio_analyzer.py"
echo.
echo [DONE] Version 47.0 Applied! (UI & Engine Fixed)
pause
