@echo off
title ArchivePro v30 Universal Workflow Update
echo ===============================================
echo      ArchivePro Studio v30.0 (Ultimate Workflow)
echo ===============================================
echo.
echo Synchronizing Professional Workflow System...
set CURR_DIR=%~dp0
copy /Y "%CURR_DIR%archiver.py" "archiver.py"
copy /Y "%CURR_DIR%main.py" "main.py"
copy /Y "%CURR_DIR%styles.py" "styles.py"
echo.
echo [DONE] Version 30.0 Applied! (Workflow Integrated)
pause
