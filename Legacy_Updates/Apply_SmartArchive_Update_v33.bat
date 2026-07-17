@echo off
title ArchivePro v33 Vector Pro Update
echo ===============================================
echo      ArchivePro Studio v33.0 (Vector Pro)
echo ===============================================
echo.
echo Synchronizing Vector Assets and Design Objects...
set CURR_DIR=%~dp0
copy /Y "%CURR_DIR%archiver.py" "archiver.py"
copy /Y "%CURR_DIR%main.py" "main.py"
copy /Y "%CURR_DIR%styles.py" "styles.py"
echo.
echo [DONE] Version 33.0 Applied! (Vector-Design Ready)
pause
