@echo off
title ArchivePro v50 Smart Merger Update
echo ===============================================
echo      ArchivePro Studio v50.0 (Smart Merge)
echo ===============================================
echo.
echo Enabling Folder Matching and Existing Directory Reuse...
set CURR_DIR=%~dp0
copy /Y "%CURR_DIR%main.py" "main.py"
copy /Y "%CURR_DIR%archiver.py" "archiver.py"
copy /Y "%CURR_DIR%audio_analyzer.py" "audio_analyzer.py"
echo.
echo [DONE] Version 50.0 Applied! (Zero-Duplicate Folders)
pause
