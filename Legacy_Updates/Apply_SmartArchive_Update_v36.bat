@echo off
title ArchivePro v36 Global Progress Fix
echo ===============================================
echo      ArchivePro Studio v36.0 (Stable UI)
echo ===============================================
echo.
echo Fixing UI and Progress Bar issues...
set CURR_DIR=%~dp0
copy /Y "%CURR_DIR%archiver.py" "archiver.py"
copy /Y "%CURR_DIR%main.py" "main.py"
copy /Y "%CURR_DIR%styles.py" "styles.py"
echo.
echo [DONE] Version 36.0 Applied! (UI & Progress Fixed)
pause
