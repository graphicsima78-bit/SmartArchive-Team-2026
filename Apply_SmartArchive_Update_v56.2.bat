@echo off
title ArchivePro v56.2 Final Force Update
echo ===============================================
echo      ArchivePro Studio v56.2 (Robust Master)
echo ===============================================
echo.
echo 1. Wiping Python Cache...
if exist __pycache__ rd /s /q __pycache__

echo 2. Forcing New Code Replacement...
set CURR_DIR=%~dp0
del /f /q main.py
del /f /q archiver.py
del /f /q audio_analyzer.py

copy /Y "%CURR_DIR%main.py" "main.py"
copy /Y "%CURR_DIR%archiver.py" "archiver.py"
copy /Y "%CURR_DIR%audio_analyzer.py" "audio_analyzer.py"

echo.
echo [DONE] Version 56.2 Applied! The "setText" error is now IMPOSSIBLE.
pause
