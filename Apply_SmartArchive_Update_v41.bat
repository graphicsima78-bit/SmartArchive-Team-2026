@echo off
title ArchivePro v41 Progress Fix
echo ===============================================
echo      ArchivePro Studio v41.0 (Green Bar Fix)
echo ===============================================
echo.
echo Fixing the missing Green Progress Line...
set CURR_DIR=%~dp0
copy /Y "%CURR_DIR%main.py" "main.py"
copy /Y "%CURR_DIR%archiver.py" "archiver.py"
echo.
echo [DONE] Version 41.0 Applied! (Progress Bar is now visible)
pause
