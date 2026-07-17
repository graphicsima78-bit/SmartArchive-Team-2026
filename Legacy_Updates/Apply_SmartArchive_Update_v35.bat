@echo off
title ArchivePro v35 Core Restoration
echo ===============================================
echo      ArchivePro Studio v35.0 (UI & Engine Fix)
echo ===============================================
echo.
echo Restoring Engine and Fixing Theme Colors...
set CURR_DIR=%~dp0
copy /Y "%CURR_DIR%archiver.py" "archiver.py"
copy /Y "%CURR_DIR%main.py" "main.py"
copy /Y "%CURR_DIR%styles.py" "styles.py"
echo.
echo [DONE] Version 35.0 Applied! Program is ready.
pause
