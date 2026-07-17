@echo off
title ArchivePro v56.1 Bug Fix
echo ===============================================
echo      ArchivePro Studio v56.1 (Bug Fix)
echo ===============================================
echo.
echo Fixing AttributeError and Lambda issue...
set CURR_DIR=%~dp0
copy /Y "%CURR_DIR%main.py" "main.py"

echo.
echo [DONE] Version 56.1 Applied! The "setText" error is resolved.
pause
