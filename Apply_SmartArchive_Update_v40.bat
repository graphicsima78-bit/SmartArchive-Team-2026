@echo off
title ArchivePro v40 Drive Navigator
echo ===============================================
echo      ArchivePro Studio v40.0 (Multi-Drive)
echo ===============================================
echo.
echo Enabling Intelligent Drive Navigation and Memory...
set CURR_DIR=%~dp0
copy /Y "%CURR_DIR%archiver.py" "archiver.py"
copy /Y "%CURR_DIR%main.py" "main.py"
copy /Y "%CURR_DIR%styles.py" "styles.py"
echo.
echo [DONE] Version 40.0 Applied! (Drives Fully Supported)
pause
