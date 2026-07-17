@echo off
title ArchivePro v44 Absolute Stability Update
echo ===============================================
echo      ArchivePro Studio v44.0 (Absolute Stability)
echo ===============================================
echo.
echo Fixing UI collapse and Engine halt issues...
set CURR_DIR=%~dp0
copy /Y "%CURR_DIR%main.py" "main.py"
copy /Y "%CURR_DIR%archiver.py" "archiver.py"
echo.
echo [DONE] Version 44.0 Applied! (UI is now solid and non-collapsible)
pause
