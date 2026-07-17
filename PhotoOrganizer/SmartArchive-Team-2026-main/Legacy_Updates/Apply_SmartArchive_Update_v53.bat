@echo off
title ArchivePro v53 Final Sync
echo ===============================================
echo      ArchivePro Studio v53.0 (Persian Sync)
echo ===============================================
echo.
echo Cleaning Python cache to force new code...
if exist __pycache__ rd /s /q __pycache__

echo Synchronizing Persian Artist Names and Folder Merging...
set CURR_DIR=%~dp0
copy /Y "%CURR_DIR%main.py" "main.py"
copy /Y "%CURR_DIR%archiver.py" "archiver.py"
copy /Y "%CURR_DIR%audio_analyzer.py" "audio_analyzer.py"
echo.
echo [DONE] Version 53.0 Applied! Please restart the program.
pause
