@echo off
title ArchivePro v66 Final Master Update
echo ===============================================
echo      ArchivePro Studio v66.0 (Final Master)
echo ===============================================
echo.
echo 1. Clearing all Python caches...
if exist __pycache__ rd /s /q __pycache__

echo 2. Overwriting core engine with synchronized logic...
set CURR_DIR=%~dp0
copy /Y "%CURR_DIR%main.py" "main.py"
copy /Y "%CURR_DIR%archiver.py" "archiver.py"
copy /Y "%CURR_DIR%audio_analyzer.py" "audio_analyzer.py"

echo.
echo [DONE] Final Suite Applied! Use python main.py or Run_ArchivePro.bat
pause
