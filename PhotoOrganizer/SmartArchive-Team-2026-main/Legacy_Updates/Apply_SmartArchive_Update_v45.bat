@echo off
title ArchivePro v45 Guardian Update
echo ===============================================
echo      ArchivePro Studio v45.0 (Guardian Mode)
echo ===============================================
echo.
echo Installing safety protocols and write-protection...
set CURR_DIR=%~dp0
copy /Y "%CURR_DIR%archiver.py" "archiver.py"
copy /Y "%CURR_DIR%main.py" "main.py"
echo.
echo [OK] Version 45.0 Applied! (Safety First)
pause
