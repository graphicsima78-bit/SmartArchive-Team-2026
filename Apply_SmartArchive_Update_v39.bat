@echo off
title ArchivePro v39 Auto-Reset Fix
echo ===============================================
echo      ArchivePro Studio v39.0 (Auto-Reset)
echo ===============================================
echo.
echo Fixing Progress Bar Reset and Finish Logic...
set CURR_DIR=%~dp0
copy /Y "%CURR_DIR%archiver.py" "archiver.py"
copy /Y "%CURR_DIR%main.py" "main.py"
copy /Y "%CURR_DIR%styles.py" "styles.py"
echo.
echo [DONE] Version 39.0 Applied! (System Resets on Finish)
pause
