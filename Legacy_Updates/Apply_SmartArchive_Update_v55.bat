@echo off
title ArchivePro v55 Final Stable Update
echo ===============================================
echo      ArchivePro Studio v55.0 (Final Stable)
echo ===============================================
echo.
echo 1. Cleaning Cache...
if exist __pycache__ rd /s /q __pycache__

echo 2. Applying Pure Code...
set CURR_DIR=%~dp0
copy /Y "%CURR_DIR%main.py" "main.py"
copy /Y "%CURR_DIR%archiver.py" "archiver.py"

echo.
echo [DONE] Version 55.0 Applied! This is the most stable version.
pause
