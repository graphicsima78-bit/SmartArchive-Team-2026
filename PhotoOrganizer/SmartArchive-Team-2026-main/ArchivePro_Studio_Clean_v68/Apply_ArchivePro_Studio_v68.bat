@echo off
title ArchivePro v68 Master Sync
echo ===============================================
echo      ArchivePro Studio v68.0 (Master Sync)
echo ===============================================
echo.
echo Cleaning Python cache and applying fixed code...
if exist Core\__pycache__ rd /s /q Core\__pycache__

set CURR_DIR=%~dp0
copy /Y "%CURR_DIR%Core\main.py" "main.py"
copy /Y "%CURR_DIR%Core\archiver.py" "archiver.py"
copy /Y "%CURR_DIR%Core\audio_analyzer.py" "audio_analyzer.py"
copy /Y "%CURR_DIR%Core\styles.py" "styles.py"

echo.
echo [DONE] Version 68.0 Masterpiece Applied!
pause
