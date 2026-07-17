@echo off
title ArchivePro v34 Content Creator Update
echo ===============================================
echo      ArchivePro Studio v34.0 (Creator Ready)
echo ===============================================
echo.
echo Synchronizing Social Media & Design Workflow...
set CURR_DIR=%~dp0
copy /Y "%CURR_DIR%archiver.py" "archiver.py"
copy /Y "%CURR_DIR%main.py" "main.py"
copy /Y "%CURR_DIR%styles.py" "styles.py"
echo.
echo [DONE] Version 34.0 Applied! (Ready for Reels & Covers)
pause
